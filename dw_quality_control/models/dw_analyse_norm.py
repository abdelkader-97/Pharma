from odoo import models, fields

class TestType(models.Model):
    _name = "dw.analyse.norm.type"
    _description = "Analyse Norm Type"

    name = fields.Char('Name', required=True)
    technical_name = fields.Char('Technical name', required=True)
    active = fields.Boolean('active', default=True)

class DwStandard(models.Model):
    _name = 'dw.analyse.norm'
    _description = 'Norms'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    test_type_id = fields.Many2one('dw.analyse.norm.type', 'Test Type',
                                   help="Defines the type of the quality control point.",required=True,)
    test_type = fields.Char(related='test_type_id.technical_name', readonly=True)
    norm = fields.Float('Norm', digits='Quality Tests')
    tolerance_min = fields.Float('Min Tolerance', digits='Quality Tests')
    tolerance_max = fields.Float('Max Tolerance', digits='Quality Tests')
    norm_unit = fields.Char('Norm Unit', default=lambda self: 'mm')
    description = fields.Text(string='Description')