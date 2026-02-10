from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    product_request_id = fields.Many2one(
        'product.request'
    )