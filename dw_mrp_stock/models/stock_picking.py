from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    production_id = fields.Many2one(
        'mrp.production', readonly=0
    )
