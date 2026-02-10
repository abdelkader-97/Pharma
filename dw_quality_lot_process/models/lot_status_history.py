from odoo import models, fields, api
from datetime import datetime

class LotStatusHistory(models.Model):
    _name = 'dw.stock.lot.history'
    _description = 'Lot Status History'

    lot_id = fields.Many2one('stock.lot', string="Lot", required=True, ondelete='cascade')

    previous_status = fields.Selection([
        ('quarantine', 'Quarantine'),
        ('conform', 'Conform'),
        ('not_conform', 'Not Conform'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled')
    ], string="Previous Status")

    new_status = fields.Selection([
        ('quarantine', 'Quarantine'),
        ('conform', 'Conform'),
        ('not_conform', 'Not Conform'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled')
    ], string="New Status")

    previous_lot_quarantine_status = fields.Selection([
        ('draft','Draft'),
        ('in_progress', 'In progress'),
        ('analyzed','Analyzed'),
        ('reanalyzed','reanalyzed')
        ],string="Previous Analyse State",)
    new_lot_quarantine_status = fields.Selection([
        ('draft','Draft'),
        ('in_progress', 'In progress'),
        ('analyzed','Analyzed'),
        ('reanalyzed','reanalyzed')
        ],string="New Analyse State",)

    change_date = fields.Datetime(string="Change Date", default=lambda self: fields.Datetime.now())

    user_id = fields.Many2one('res.users', string="Changed By", default=lambda self: self.env.user)
    previous_date_expiration = fields.Datetime(string="Previous Expiration Date")
    new_date_expiration = fields.Datetime(string="New Date expiration")
    reason_id = fields.Many2one('stock.lot.cancel.reason', string="Reason")
    note = fields.Text(string="Note")

class StockLotCancelReason(models.Model):
    _name = 'stock.lot.cancel.reason'
    _description = 'Cancellation Reason'

    name = fields.Char(string="Reason", required=True)