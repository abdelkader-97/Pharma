from odoo import models, fields


class DwTest(models.Model):
    _name = 'dw.analyse.test'
    _description = 'Tests'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')