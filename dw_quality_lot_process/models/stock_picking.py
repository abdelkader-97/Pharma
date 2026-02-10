from odoo.exceptions import ValidationError

from odoo import _, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            picking_type = picking.picking_type_id.code or False
            move_ids = picking.move_ids.filtered(lambda m: m.product_id and m.product_id.requires_lot_compliance_check)
            if picking_type == 'internal':
                self._check_internal_transfer(move_ids)
            elif picking_type == 'mrp_operation':
                self._check_lot_mrp_operation_compliance(move_ids)
            elif picking_type == 'outgoing':
                self._check_lot_outgoing_compliance(move_ids)

        return super(StockPicking, self).button_validate()

    def _check_lot_outgoing_compliance(self, move_ids):
        for move_id in move_ids:
            for move_line in move_id.move_line_ids:
                location_id = move_line.location_id
                if location_id:
                    self._check_transfer_compliance(location_id, move_line.lot_id, move_id.product_id, 'out')

    def _check_lot_mrp_operation_compliance(self, move_ids):
        for move_id in move_ids:
            for move_line in move_id.move_line_ids:
                location_dest = move_line.location_dest_id
                if location_dest:
                    self._check_transfer_compliance(location_dest, move_line.lot_id, move_id.product_id, 'in')

    def _check_internal_transfer(self, move_ids):
        for move_id in move_ids:
            for move_line in move_id.move_line_ids:
                location_source = move_line.location_id
                location_dest = move_line.location_dest_id
                if location_source and location_dest:
                    self._check_transfer_compliance(location_source, move_line.lot_id, move_id.product_id, 'out')
                    self._check_transfer_compliance(location_dest, move_line.lot_id, move_id.product_id, 'in')

    def _check_transfer_compliance(self, location, lot, product, direction):
        if not location.perform_transfer and location.must_check_lot_compliance:
            if direction == 'in':
                authorized_lot_status = location.allowed_lot_status_in.mapped('name') or None
            else:
                authorized_lot_status = location.allowed_lot_status_out.mapped('name') or None

            if authorized_lot_status is not None:
                self._validate_lot_conformity(authorized_lot_status, lot, product, location)
            # If authorized_lot_status is None, all lot statuses are accepted, so no validation is needed.

    def _validate_lot_conformity(self, authorized_lot_status, lot, product, location=False):
        lot_status = lot.lot_status
        if lot_status not in authorized_lot_status:
            lot_status_display = dict(lot._fields['lot_status'].selection).get(lot_status, lot_status)
            raise ValidationError(
                _(f"The transfer for {product.name} cannot be performed for lot: {lot.name} with status: {lot_status_display} in locaation : {location.name or False}")
            )
