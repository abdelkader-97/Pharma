from odoo import api, fields, models


class QualityCheckProductModel(models.Model):
    _name = 'dw.quality.check.product.model'

    name = fields.Char()
    product_id = fields.Many2one(
        'product.template'
    )
    model_ids = fields.One2many(
        'dw.quality.check.model',
        'product_model_id'
    )
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals):
        """
        the create method is done one by one, so we can easly get the dict inside it
        """
        res = super(QualityCheckProductModel, self).create(vals)
        if vals[0]['product_id']:
            self.env['product.template'].browse(vals[0]['product_id']).write({
                'quality_model_id': res.id
            })
        return res


class QualityCheckModel(models.Model):
    _name = 'dw.quality.check.model'
    _description = 'This model is set to perform models to be checked in the quality check model'

    name = fields.Char()
    reference = fields.Char()
    standards = fields.Char()
    result = fields.Char()
    product_model_id = fields.Many2one(
        'dw.quality.check.product.model'
    )
    company_id = fields.Many2one('res.company', related="product_model_id.company_id", store=True)
