from odoo.exceptions import ValidationError

from odoo import models, fields, _


class StockLotSubLotWizard(models.TransientModel):
    _name = 'stock.lot.sub.lot.register'
    _description = 'Stock Lot Sub Lot Register'

    reason_id = fields.Many2one('stock.lot.cancel.reason', string='Reason')
    lot_id = fields.Many2one('stock.lot', string='Stock Lot', required=True)
    partial_liberation_qc = fields.Boolean("Partial Liberation", default=False)
    status = fields.Selection([
        ('not_conform', 'Not Conform'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled')], string="Lot Failed Status")
    check_quality_id = fields.Many2one(
        'dw.quality.check',
        string='Check Quality',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location Lot',
    )
    non_conform_qty = fields.Float(string='Quantity Non-Conform')
    non_conform_lot = fields.Char()

    def _create_history_record(self, lot, status, with_reason=False):
        '''This function creates record in stock.lot.history
        the parameter with_reason is set to false in case the user does not provide a reason
        if it's set to true a new record is created with reason and note if exit'''

        history_vals = {
            'lot_id': lot.id,
            'user_id': self.env.user.id,
            'change_date': fields.Datetime.now(),
            'previous_status': lot.lot_status,
            'new_status': status if status else False,
            'reason_id': self.reason_id.id if with_reason else False,
            'note': self.note if with_reason else '',
        }
        self.env['dw.stock.lot.history'].sudo().create(history_vals)

    def action_confirm_sub_lot(self):
        partial_liberation_qc = self.partial_liberation_qc
        check_quality_id = self.check_quality_id
        lot_id = check_quality_id.lot_id

        if partial_liberation_qc and lot_id:
            non_conform_qty = self.non_conform_qty
            check_quality_id.partial_liberation_qc = True
            conform_qty = check_quality_id.picking_lot_quantity - non_conform_qty
            if conform_qty <= 0:
                raise ValidationError(_(f"Non Conform quantity should not be grater than lot quantity"))
            picking_id = check_quality_id.picking_id
            if picking_id:
                location_id = picking_id.location_id
                move_id = picking_id.move_line_ids.filtered_domain(
                    [('product_id', '=', check_quality_id.product_id.id), ('location_id', '=', location_id.id),
                     ('lot_id', '=', lot_id.id)])

                move_id.quantity = conform_qty
                quant = lot_id.quant_ids.filtered_domain([('location_id', '=', location_id.id)])
                quant.quantity = conform_qty
                non_conform_lot = self.non_conform_lot
                if non_conform_lot:
                    lot = {
                        'name': non_conform_lot,
                        'is_child': True,
                        'parent_lot_id': lot_id.id,
                        'product_id': check_quality_id.product_id.id,
                        'company_id': check_quality_id.company_id.id,
                    }
                    sub_lot_id = self.env['stock.lot'].sudo().create(lot)
                    if sub_lot_id:
                        status = self.status
                        sub_lot_id.action_set_analyzed()
                        self._create_history_record(sub_lot_id, status)
                        sub_lot_id.set_lot_status(status)
                        message = f"Lot cancelled. Reason: {self.reason_id.name or 'No reason provided'}"
                        sub_lot_id.message_post(body=message)
                        quant = {
                            'lot_id': sub_lot_id.id,
                            'product_id': sub_lot_id.product_id.id,
                            'quantity': non_conform_qty,
                            'company_id': check_quality_id.company_id.id,
                            'location_id': self.location_id.id or check_quality_id.location_id.id,
                        }
                        self.env['stock.quant'].sudo().create(quant)

        check_quality_id.do_pass()

        return True
