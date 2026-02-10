from odoo import api, fields, models
from collections import defaultdict
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)
        moves._create_quality_checks()
        return moves

    def _create_quality_checks(self):
        # Groupby move by picking. Use it in order to generate missing quality checks.
        pick_moves = defaultdict(lambda: self.env['stock.move'])
        for move in self:
            if move.picking_id and not move.scrapped:
                pick_moves[move.picking_id] |= move
        check_vals_list = self._create_operation_quality_checks(pick_moves)
        for picking, moves in pick_moves.items():
            # Quality checks by product
            quality_points_domain = self.env['dw.quality.point']._get_domain(moves.product_id, picking.picking_type_id, measure_on='product')
            quality_points = self.env['dw.quality.point'].sudo().search(quality_points_domain)

            if not quality_points:
                continue
            picking_check_vals_list = quality_points._get_checks_values(moves.product_id, picking.company_id.id, existing_checks=picking.sudo().check_ids)
            for check_value in picking_check_vals_list:
                check_value.update({
                    'picking_id': picking.id,
                })
            check_vals_list += picking_check_vals_list
        self.env['dw.quality.check'].sudo().create(check_vals_list)

    def _create_operation_quality_checks(self, pick_moves):
        check_vals_list = []
        for picking, moves in pick_moves.items():
            quality_points_domain = self.env['dw.quality.point']._get_domain(moves.product_id, picking.picking_type_id, measure_on='operation')
            quality_points = self.env['dw.quality.point'].sudo().search(quality_points_domain)
            for point in quality_points:
                if point.check_execute_now():
                    check_vals_list.append({
                        'point_id': point.id,
                        'team_id': point.team_id.id,
                        'measure_on': 'operation',
                        'picking_id': picking.id,
                    })
        return check_vals_list

    def _action_cancel(self):
        res = super()._action_cancel()

        to_unlink = self.env['dw.quality.check'].sudo()
        is_product_canceled = defaultdict(lambda: True)
        for qc in self.picking_id.sudo().check_ids:
            if qc.quality_state != 'none':
                continue
            if (qc.picking_id, qc.product_id) not in is_product_canceled:
                for move in qc.picking_id.move_ids:
                    is_product_canceled[(move.picking_id, move.product_id)] &= move.state == 'cancel'
            if is_product_canceled[(qc.picking_id, qc.product_id)]:
                to_unlink |= qc
        to_unlink.unlink()

        return res


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    check_ids = fields.One2many('dw.quality.check', 'move_line_id', 'Checks')
    check_state = fields.Selection([
        ('no_checks', 'No checks'),
        ('in_progress', 'Some checks to be done'),
        ('pass', 'All checks passed'),
        ('fail', 'Some checks failed')], compute="_compute_check_state")

    @api.depends('check_ids')
    def _compute_check_state(self):
        for line in self:
            if not line.check_ids:
                line.check_state = 'no_checks'
            elif line.check_ids.filtered(lambda check: check.quality_state == 'none'):
                line.check_state = 'in_progress'
            elif line.check_ids.filtered(lambda check: check.quality_state == 'fail'):
                line.check_state = "fail"
            else:
                line.check_state = "pass"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        if self.env.context.get('no_checks'):
            # no checks for you
            return lines
        lines._filter_move_lines_applicable_for_quality_check()._create_check()
        return lines

    def write(self, vals):
        if self._create_quality_check_at_write(vals):
            self.filtered(lambda ml: not ml.picked and not ml.sudo().check_ids)._create_check()
        return super().write(vals)

    def unlink(self):
        self.sudo()._unlink_quality_check()
        return super(StockMoveLine, self).unlink()

    def action_open_quality_check_wizard(self):
        return self.check_ids.action_open_quality_check_wizard()

    def _unlink_quality_check(self):
        self.check_ids.filtered(lambda qc: qc._check_to_unlink()).unlink()

    def _create_quality_check_at_write(self, vals):
        return vals.get('quantity')

    def _create_check(self):
        check_values_list = []
        quality_points_domain = self.env['dw.quality.point']._get_domain(
            self.product_id, self.move_id.picking_type_id, measure_on='move_line')
        quality_points = self.env['dw.quality.point'].sudo().search(quality_points_domain)
        quality_points_by_product_picking_type = {}
        for quality_point in quality_points:
            for product in quality_point.product_ids:
                for picking_type in quality_point.picking_type_ids:
                    quality_points_by_product_picking_type.setdefault(
                        (product, picking_type), set()).add(quality_point.id)
            for categ in quality_point.product_category_ids:
                categ_product = self.env['product.product'].search([
                    ('categ_id', 'child_of', categ.id)
                ])
                for product in categ_product & self.product_id:
                    for picking_type in quality_point.picking_type_ids:
                        quality_points_by_product_picking_type.setdefault(
                            (product, picking_type), set()).add(quality_point.id)
            if not quality_point.product_ids and not quality_point.product_category_ids:
                for picking_type in quality_point.picking_type_ids:
                    quality_points_by_product_picking_type.setdefault(
                        (None, picking_type), set()).add(quality_point.id)

        for ml in self:
            quality_points_product = quality_points_by_product_picking_type.get((ml.product_id, ml.move_id.picking_type_id), set())
            quality_points_all_products = ml._get_quality_points_all_products(quality_points_by_product_picking_type)
            quality_points = self.env['dw.quality.point'].sudo().search([('id', 'in', list(quality_points_product | quality_points_all_products))])
            for quality_point in quality_points:
                if quality_point.check_execute_now():
                    check_values = ml._get_check_values(quality_point)
                    check_values_list.append(check_values)
        if check_values_list:
            self.env['dw.quality.check'].sudo().create(check_values_list)

    def _filter_move_lines_applicable_for_quality_check(self):
        return self.filtered(lambda line: line.quantity != 0)

    def _get_check_values(self, quality_point):
        return {
            'point_id': quality_point.id,
            'measure_on': quality_point.measure_on,
            'team_id': quality_point.team_id.id,
            'product_id': self.product_id.id,
            'picking_id': self.picking_id.id,
            'move_line_id': self.id,
            'lot_name': self.lot_name,
        }

    def _get_quality_points_all_products(self, quality_points_by_product_picking_type):
        return quality_points_by_product_picking_type.get((None, self.move_id.picking_type_id), set())

