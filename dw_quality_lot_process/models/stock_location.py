from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.model
    def _default_lot_status(self):
        lot_status_conform = self.env.ref('dw_quality_lot_process.stock_lot_status_conform')
        return [(6, 0, [lot_status_conform.id])]

    allowed_lot_status_in = fields.Many2many('stock.lot.status', string='Lot status IN',
                                             default=lambda self: self._default_lot_status(),
                                             relation='location_status_lot_in',
                                             column1='location_id',
                                             column2='status_id',
                                             help="This field indicates the authorized lot status to transfer in the current location")

    allowed_lot_status_out = fields.Many2many('stock.lot.status', string='Lot status OUT',
                                              default=lambda self: self._default_lot_status(),
                                              relation='location_status_lot_out',
                                              column1='location_id',
                                              column2='status_id',
                                              help="This field indicates the authorized lot status to transfer out of the current location")

    must_check_lot_compliance = fields.Boolean(string="Check Lot Conformity", default=False,
                                               help='This field indicates if we should check lot conformity in the location')

    perform_quality_lot_reanalyze = fields.Boolean(string="Perform Quality lot reanalyze", default=False,
                                       help="Check this box to perform a quality reanalysis for lots.")

class StockLotStatus(models.Model):
    _name = 'stock.lot.status'
    _description = 'Lot status'

    name = fields.Selection([
        ('quarantine', 'Quarantine'),
        ('conform', 'Conform'),
        ('not_conform', 'Not Conform'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled')
    ], string="Lot Status", required=True)


class LotStatus(models.Model):
    _name = 'lot.status'
