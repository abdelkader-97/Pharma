from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    perform_transfer = fields.Boolean(string="Perform Transfer", default=True,
                                      help='This field indicates if we can perfom a tranfer from this location')

    @api.onchange('storage_category_id')
    def onchange_perform_transfer(self):
        storage_category_id = self.storage_category_id
        if storage_category_id:
            self.perform_transfer = storage_category_id.perform_transfer
