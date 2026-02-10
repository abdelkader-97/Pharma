from odoo import fields, models

class TestType(models.Model):
    _name = "dw.quality.point.test_type"
    _description = "Quality Control Test Type"

    name = fields.Char('Name', required=True, translate=True)
    technical_name = fields.Char('Technical name', required=True)
    active = fields.Boolean('active', default=True)