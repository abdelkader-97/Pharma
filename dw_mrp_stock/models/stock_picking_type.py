from odoo import api, fields, models, _


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    stock_production = fields.Boolean(
        help=_("When checked it means that this operation will be used as manufacturing operation but in"
               " stock location not in the manufacturing unit")
    )
