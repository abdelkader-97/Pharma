from odoo import models, fields, _

class StockLotCancelWizard(models.TransientModel):
    _name = 'stock.lot.cancel.wizard'
    _description = 'Stock Lot Cancel Wizard'

    reason_id = fields.Many2one('stock.lot.cancel.reason', string='Reason')
    note = fields.Text(string='Note')
    lot_id = fields.Many2one('stock.lot', string='Stock Lot', required=True)
    status = fields.Selection([
        ('not_conform', 'Not Conform'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled')],string="Lot Failed Status")
    check_quality_id = fields.Many2one(
        'dw.quality.check',
        string='Check Quality',
        )
    fail_location_id = fields.Many2one(
        'stock.location',string = 'Location'
        )
    def _create_history_record(self,with_reason=False):
      
        history_vals = {
            'lot_id': self.lot_id.id,
            'user_id': self.env.user.id,
            'change_date': fields.Datetime.now(),
            'previous_status': self.lot_id.lot_status,
            'new_status': self.status if self.status else False,
            'reason_id': self.reason_id.id if with_reason else False,
            'note' : self.note if with_reason else '',
        }
        self.env['dw.stock.lot.history'].sudo().create(history_vals)
    
    def action_cancel_reason_lot(self):
        if self.check_quality_id :
            if self.fail_location_id :
                self.check_quality_id.picking_id.location_dest_id = self.fail_location_id.id
            self.check_quality_id.do_fail()
        if self.lot_id and self.lot_id.lot_quarantine_status !='analyzed' :
            self.lot_id.action_set_analyzed()    
        self._create_history_record(with_reason=True)
        self.lot_id.lot_status = self.status if self.status else False
        message = f"Lot cancelled. Reason: {self.reason_id.name if self.reason_id else 'No reason provided'}"
        self.lot_id.message_post(body=message)

        return True
