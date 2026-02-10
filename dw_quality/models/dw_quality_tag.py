from odoo import models, fields

class QualityTag(models.Model):
    _name = "dw.quality.tag"
    _description = "Quality Tag"

    name = fields.Char('Tag Name', required=True)
    color = fields.Integer('Color Index', help='Used in the kanban view')