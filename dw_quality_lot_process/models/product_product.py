from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    requires_lot_compliance_check = fields.Boolean(default=False, string='Requires Lot Compliance Check')


class DwProductTemplate(models.Model):
    _inherit = 'product.template'
    requires_lot_compliance_check = fields.Boolean(default=False, string='Requires Lot Compliance Check')
