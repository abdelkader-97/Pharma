from odoo.exceptions import MissingError

from odoo import Command, fields, models, _


class DwStockLocation(models.Model):
    _inherit = 'stock.location'

    dw_is_quarantine = fields.Boolean(string="Is Quarantine")

class DwStockLot(models.Model):
    _inherit = 'stock.lot'

    dw_date_production = fields.Date(string="Production Date")


class DwStockPicking(models.Model):
    _inherit = 'stock.quant'

    ref = fields.Char(related='lot_id.ref', store=1)
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dw_qc_picking_origin_id = fields.Many2one("stock.picking")

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        for picking in self:
            if picking.picking_type_id.code in ['incoming', 'internal']:
                move_line_ids = picking.move_line_ids.filtered(
                    lambda m: m.location_dest_id.dw_is_quarantine and m.product_id.auto_qc_gen)
                if not move_line_ids:
                    continue

                warehouse_id = picking.location_dest_id.warehouse_id
                quality_operation_id = warehouse_id.dw_quality_operation_id

                if not quality_operation_id:
                    raise MissingError(_("You can’t validate this picking without a quality operation."))
                quality_picking_list = []
                for move in move_line_ids:
                    quality_picking = self._prepare_quality_picking_data(picking, move, quality_operation_id)
                    quality_picking_list.append(quality_picking)
                quality_picking_ids = self.env["stock.picking"].sudo().create(quality_picking_list)
                quality_picking_ids.mapped("move_ids").sudo()._create_quality_checks()

        return res

    def _prepare_quality_picking_data(self, picking, move, quality_operation_id):
        location_dest_id = quality_operation_id.default_location_dest_id.id
        if not location_dest_id:
            raise MissingError(
                _("You can’t validate this picking without default destination location for your quality operation."))

        return {
            'picking_type_id': quality_operation_id.id,
            'location_id': picking.location_dest_id.id,
            'location_dest_id': location_dest_id,
            'origin': picking.name,
            'state': "draft",
            'dw_qc_picking_origin_id': picking.id,
            'move_ids': self._create_quality_move(move, quality_operation_id),
            'move_line_ids': self._create_quality_move_line(move, quality_operation_id),
        }

    def _prepare_quality_move_data(self, move, quality_operation_id):
        location_dest_id = quality_operation_id.default_location_dest_id
        if not location_dest_id:
            raise MissingError(
                _("You can’t validate this picking without default destination location for your quality operation."))
        return {
            'name': move.product_id.name,
            'product_id': move.product_id.id,
            'product_uom_qty': move.quantity,
            'state': "draft",
            'product_uom': move.product_uom_id.id,
            'location_id': move.location_dest_id.id,
            'location_dest_id': location_dest_id.id,
        }

    def _prepare_quality_move_line_data(self, move_line, quality_operation_id):
        location_dest_id = quality_operation_id.default_location_dest_id

        return {
            'location_id': move_line.location_dest_id.id,
            'location_dest_id': location_dest_id.id,
            'quantity': move_line.quantity,
            'lot_id': move_line.lot_id.id,
            'product_uom_id': move_line.product_uom_id.id,
            'product_id': move_line.product_id.id,

        }

    def _create_quality_move(self, move, quality_operation_id):
        location_dest_id = quality_operation_id.default_location_dest_id
        if not location_dest_id:
            raise MissingError(
                _("You can’t validate this picking without default destination location for your quality operation."))
        return [Command.create(self._prepare_quality_move_data(move, quality_operation_id))]

    def _create_quality_move_line(self, move_line, quality_operation_id):

        return [Command.create(self._prepare_quality_move_line_data(move_line, quality_operation_id))]

