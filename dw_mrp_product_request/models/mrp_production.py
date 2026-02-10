import datetime

from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.depends('move_raw_ids.state')
    def _compute_product_request_needed(self):
        for record in self:
            record.product_request_needed = True if len(record.move_raw_ids.filtered(
                lambda l: l if l.state in ('waiting', 'partially_available', 'confirmed') else None)) > 0 else False

    dw_leftover_done = fields.Boolean(string='leftover Done', default=False)
    product_request_needed = fields.Boolean(
        compute='_compute_product_request_needed'
    )

    request_ids = fields.One2many(
        'product.request',
        'production_id'
    )
    mrp_product_request_count = fields.Integer(
        compute='_compute_mrp_product_request_count'
    )

    def action_request_products(self):

        datas = self._prepare_datas()
        request_id = self.env['product.request'].create(datas)

        tree_view = self.env.ref('dw_mrp_product_request.view_product_request_tree')
        form_view = self.env.ref('dw_mrp_product_request.view_product_request_form')

        action = {
            'name': _('Product Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.request',
        }

        action['views'] = [
            (tree_view.id, 'list'),
            (form_view.id, 'form')
        ]
        action['view_mode'] = 'list, form'
        action['res_id'] = request_id.id
        action['domain'] = [('production_id', '=', self.id)]
        action['context'] = {'default_production_id': self.id}

        return action

    def action_view_product_request(self):

        tree_view = self.env.ref('dw_mrp_product_request.view_product_request_tree')
        form_view = self.env.ref('dw_mrp_product_request.view_product_request_form')

        action = {
            'name': _('Product Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.request',
        }

        action['views'] = [
            (tree_view.id, 'list'),
            (form_view.id, 'form')
        ]
        action['view_mode'] = 'list, form'
        action['domain'] = [('production_id', '=', self.id)]
        action['context'] = {'default_production_id': self.id}

        return action

    def action_create_picking_request(self):
        """
        This method is used by the product request button. It creates a stock picking and show it
        :return: Action Dict
        """
        # a procurement group is used to centerlize all transfers in one group
        # as for pickings and mrp production
        self.ensure_one()
        self.sudo().write({'dw_leftover_done': True})

        group_id = self.procurement_group_id
        if not group_id:
            self.env['procurement.group'].sudo().create({
                'name': self.name,
                'move_type': 'direct',
            })

            self.write({
                'procurement_group_id': group_id.id
            })
        location_src_id = self.location_src_id
        warehouse_id = location_src_id.warehouse_id
        location_id = location_src_id
        location_dest_id = warehouse_id.lot_stock_id
        location_transit_id = warehouse_id.dw_transit_production_id
        datas = []
        data = self._prepare_picking_datas(group_id, location_id, location_transit_id)
        datas.append(data) if data['move_ids_without_package'] else []
        data = self._prepare_picking_datas(group_id, location_transit_id, location_dest_id)
        datas.append(data) if data['move_ids_without_package'] else []

        picking_id = self.env['stock.picking'].sudo().create(datas)
        if picking_id:
            self.sudo().action_confirm()

            action = {
                'name': _('Production return picking(s)'),
                'res_model': 'stock.picking',
                'domain': [('id', 'in', picking_id.ids)],
                'context': {'default_production_id': self.id},
                'type': 'ir.actions.act_window',
                'view_mode': 'list,form',
            }

            return action

    def _prepare_datas(self):
        vals = self.move_raw_ids.filtered(lambda l: l.state in ('draft', 'waiting', 'partially_available', 'confirmed'))
        lines = []
        context = self.env.context.get("use_product_qty")
        for val in vals:
            if not val.product_id.bom_ids:
                quantity = val.should_consume_qty - sum(val.move_line_ids.mapped('quantity_product_uom'))
                lines.append([0, 0, {
                    'product_id': val.product_id.id,
                    'name': val.product_id.display_name,
                    'product_qty': quantity if not context else val.product_uom_qty,
                    'product_production_qty': val.should_consume_qty if not context else val.product_uom_qty,
                    'product_uom_id': val.product_uom.id,
                    'date_required': datetime.date.today(),
                    'estimated_cost': val.product_id.standard_price,
                }])
        datas = {
            'requested_by': self.env.user.id,
            'project': self.name,
            'date_start': datetime.date.today(),
            'desired_date': self.date_start,
            'latest_date': self.date_start,
            'production_id': self.id,
            'line_ids': lines,
        }
        return datas

    def _prepare_picking_datas(self, group_id, location_id, location_dest_id):
        lines = []

        for val in self.move_raw_ids:
            quantity = val.product_uom_qty - val.quantity
            if quantity == 0:
                continue
            lines.append([0, 0, {
                'product_id': val.product_id.id,
                'name': val.product_id.display_name,
                'product_uom_qty': quantity,
                'product_uom': val.product_id.uom_id.id,
                'company_id': self.env.company.id,
                'date': datetime.datetime.now(),
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'procure_method': 'make_to_stock',
                'picking_type_id': self.location_src_id.warehouse_id.int_type_id.id,
                'group_id': group_id.id,
                'production_id': False
            }])
        datas = {
            'picking_type_id': self.location_src_id.warehouse_id.int_type_id.id,
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'move_type': 'direct',
            'origin': self.name,
            'move_ids_without_package': lines
        }
        return datas

    @api.depends('request_ids')
    def _compute_mrp_product_request_count(self):
        for record in self:
            record.mrp_product_request_count = len(record.request_ids)

    def additional_consumption(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Action Reload',
            'res_model': 'dw.additional.consumption',
            'views': [[self.env.ref('dw_mrp_product_request.dw_additional_consumption_wizard_form').id, 'form']],
            'target': 'new',
            'view_mode': 'form',

        }


