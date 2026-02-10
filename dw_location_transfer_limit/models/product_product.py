from odoo import _, models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    restrict_transfer = fields.Boolean(string="Restrict Transfer", default=False)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    restrict_transfer = fields.Boolean(string="Restrict Transfer", default=False)
