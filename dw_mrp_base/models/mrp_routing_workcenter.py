from odoo import fields, api, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    consumption_model_ids = fields.One2many(
        'mrp.routing.workcenter.consumption.model',
        'routing_id'
    )


class MrpRoutingWorkcenterConsumptionModel(models.Model):
    _name = 'mrp.routing.workcenter.consumption.model'

    product_id = fields.Many2one(
        'product.product',
        required=True,
        # domain=get_product_domain
    )
    routing_id = fields.Many2one(
        'mrp.routing.workcenter'
    )
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    @api.onchange('routing_id')
    def domain_by_routing_id(self):
        return {
            'domain': {
                'product_id': [('id', 'in', self.routing_id.bom_id.bom_line_ids.mapped('product_id').ids)]
            }
        }
