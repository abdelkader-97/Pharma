from odoo import fields, models


class DwStockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    dw_transit_production_id = fields.Many2one('stock.location', string='Production Transit Location')
