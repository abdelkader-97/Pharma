from odoo import fields, models, api

class DwProductTemplate(models.Model):
    _inherit = 'product.template'

    dw_pharma_dci = fields.Char(string="DCI")
    dw_pharma_regis_num = fields.Char(string="Registration Number")
    dw_pharma_date_de = fields.Date(string="Date DE")
    dw_pharma_duration = fields.Float(string="Duration")
    dw_pharma_duration_unit = fields.Selection(
        [('days', 'Days'), ('months', 'Months'), ('years', 'Years')],
        string="Duration Unit",
        default='years',
    )
    dw_pharma_dosage_id = fields.Many2one('product.pharmaceutical.dosage', string="Dosage")
    dw_pharma_family_id = fields.Many2one('product.pharmaceutical.family', string='Family')
    dw_pharma_subfamily_id = fields.Many2one('product.pharmaceutical.subfamily', string='Subfamily')
    dw_pharma_class_id = fields.Many2one('product.pharmaceutical.class', string='Class')
    dw_pharma_subclass_id = fields.Many2one('product.pharmaceutical.subclass', string='Subclass')
    dw_pharma_form_id = fields.Many2one('product.pharmaceutical.form', string="Form")
    dw_pharma_subform_id = fields.Many2one('product.pharmaceutical.subform', string="Subform")
    dw_pharma_network_id = fields.Many2one('product.pharmaceutical.network', string="Network")
    dw_pharma_pf_dest_id = fields.Many2one('product.pharmaceutical.pf.dest', string="PF Destination")

    dw_price_ppa = fields.Monetary(string="Algerian public price", )
    dw_price_pua = fields.Monetary(string="Unit Purchase Price", )
    dw_price_wholesaler = fields.Monetary(string="wholesale price", help='The price for selling to wholesalers.')
    dw_pharma_nature_product_id = fields.Many2one('product.pharmaceutical.nature', string="Nature")
    dw_pharma_speciality_product_id = fields.Many2one('product.pharmaceutical.speciality', string="Speciality")
    dw_commercial_name = fields.Char(string="Commercial Name")
    dw_is_blocked = fields.Boolean(string="Blocked")
    dw_blacklist_date = fields.Date(string="Blacklist date")

    @api.onchange('dw_pharma_family_id')
    def onchange_dw_pharma_family_id(self):
        """Update product attributes based on pharmacy family settings.
        """
        if not self.dw_pharma_family_id:
            return
        family = self.dw_pharma_family_id
        product_categ_id = family.product_categ_id
        values = {
            'purchase_ok': family.purchase_ok,
            'sale_ok': family.sale_ok,
            'tracking': family.tracking,
            'use_expiration_date': family.use_expiration_date,
            'type': family.product_detailed_type,
        }
        if product_categ_id:
            values['categ_id'] = product_categ_id.id
        self.update(values)


class DwProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('dw_pharma_family_id')
    def onchange_dw_pharma_family_id(self):
        """Update product attributes based on pharmacy family settings.
        """
        if not self.dw_pharma_family_id:
            return
        family = self.dw_pharma_family_id
        product_categ_id = family.product_categ_id
        values = {
            'purchase_ok': family.purchase_ok,
            'sale_ok': family.sale_ok,
            'tracking': family.tracking,
            'use_expiration_date': family.use_expiration_date,
            'type': family.product_detailed_type,
        }
        if product_categ_id:
            values['categ_id'] = product_categ_id.id
        self.update(values)
