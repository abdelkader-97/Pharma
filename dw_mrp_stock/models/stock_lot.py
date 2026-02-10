from odoo import fields, models, api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    active = fields.Boolean(
        default=True
    )
