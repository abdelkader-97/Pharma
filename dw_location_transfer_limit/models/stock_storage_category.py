from odoo import fields, models


class StockStrorageCategory(models.Model):
    _inherit = 'stock.storage.category'

    
    perform_transfer = fields.Boolean(string ="Perform Transfer", default=True,help='This field indicates if we can perfom a tranfer from this location')