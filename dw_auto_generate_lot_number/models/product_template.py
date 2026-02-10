# -*- coding:utf-8 -*-

from odoo import fields, models, api

class DwProduct(models.Model):
    _inherit = 'product.template'

    auto_generate_lot_number = fields.Boolean(string='Auto Generate Lot Number',store=True,readonly=False, default=False)
    lot_code = fields.Char(string='Lot Short Code', store=True, default=False,readonly=False)
    sequence_size = fields.Integer( string='Sequence Length', store=True, readonly=False)
    counter = fields.Integer()

    @api.onchange('dw_pharma_family_id')
    def _onchange_family_id (self):
        dw_pharma_family_id=self.dw_pharma_family_id
        if dw_pharma_family_id:
            self.auto_generate_lot_number = dw_pharma_family_id.auto_generate_lot_number
            self.lot_code = dw_pharma_family_id.lot_code
            self.sequence_size = dw_pharma_family_id.sequence_size
