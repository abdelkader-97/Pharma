from odoo import fields, models


class DwStockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    quality_reanalyze_op_id = fields.Many2one('stock.picking.type', string="Reanalyze quality operation",
                                              check_company=True)
