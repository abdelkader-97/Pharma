from odoo import  fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_dw_auto_generate_lot_number = fields.Boolean("Lot Auto generate")
    module_dw_supplier_reference = fields.Boolean("Supplier Reference",help="Allows you to enter the supplier's reference for lot on the reception.")
