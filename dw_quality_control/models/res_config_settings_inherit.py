from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    module_dw_quality_lot_process = fields.Boolean("Lot quality Compliance Process")
