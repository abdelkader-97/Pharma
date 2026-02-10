from odoo import fields, models


class DwStockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    dw_quality_operation_id = fields.Many2one('stock.picking.type', string="Quality Operation")
    dw_quality_sample_id = fields.Many2one('stock.picking.type', string="Quality Sample Operation")
