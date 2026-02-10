from odoo import models, fields


class DwMethode(models.Model):
    _name = 'dw.analyse.methode'
    _description = 'Methodes'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    type = fields.Selection([
        ('identification', 'Identification'),
        ('dosage', 'Dosage'),
        ('essai', 'Test'),
        ('autre', 'Other'),
    ], string="Method Type")
    principle = fields.Text("Principle")
    procedure = fields.Text("Procedure")
    specification = fields.Text("Specification")