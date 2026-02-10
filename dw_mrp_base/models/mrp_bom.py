from odoo import fields, models

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    dw_force_mrp_config = fields.Boolean("Force Configuration")
    dw_location_component_id = fields.Many2one("stock.location", string="Location of components")
    dw_location_dest_id = fields.Many2one("stock.location", string="Location of PFs")
    dw_extrat_cost = fields.Float("extrat cost")
    dw_form_id = fields.Many2one("product.pharmaceutical.form", string='Forme')