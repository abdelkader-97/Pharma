from odoo import fields, models

class DwResPartner(models.Model):
    _inherit = 'res.partner'

    dw_supplier_nature = fields.Selection(
        [('fabricant', 'Fabricant'), ('regroupeur', 'Regroupeur'),('distributeur_exclusif','Distributeur Exclusif'),('Distributeur','Distributeur'),('supplier','Supplier'),('provider','Provider')],
        string="Supplier nature",
    )
