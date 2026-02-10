from odoo import fields, models, api

class DwProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('dw_pharma_family_id')
    def _onchange_family_id (self):
        dw_pharma_family_id=self.dw_pharma_family_id
        if dw_pharma_family_id:
            self.auto_generate_lot_number = dw_pharma_family_id.auto_generate_lot_number
            self.lot_code = dw_pharma_family_id.lot_code
            self.sequence_size = dw_pharma_family_id.sequence_size