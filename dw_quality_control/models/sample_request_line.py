
from odoo import models, fields


class SampleLineRequest(models.Model):
    _name = 'quality.sample.request.lines'
    _description = 'Sample Request Line'

    product_id = fields.Many2one('product.product',string='Product', check_company=True, required=True)
    product_quantity = fields.Float(string="Quantity",digits='Qty', required=True)
    uom_id = fields.Many2one(comodel_name='uom.uom',string="Unit of Measure", required=True)
    simple_request_id = fields.Many2one('quality.sample.request',string='Simple Request')
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial Number',domain="[('product_id', '=', product_id)]", check_company=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company,)