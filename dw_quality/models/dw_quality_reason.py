from odoo import models, fields

class QualityReason(models.Model):
    _name = "dw.quality.reason"
    _description = "Root Cause for Quality Failure"

    name = fields.Char('Name', required=True, translate=True)
