from odoo import fields, models, _
from odoo.exceptions import UserError


class DwProductPharmaceuticalDosage(models.Model):
    _name = 'product.pharmaceutical.dosage'
    _description = 'Dosage'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )


class DwProductPharmaceuticalFamily(models.Model):
    _name = 'product.pharmaceutical.family'
    _description = 'Family'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    product_categ_id = fields.Many2one(
        'product.category',
        string='Product Category'
    )
    company_id = fields.Many2one('res.company', string='Company', )
    subfamily_ids = fields.One2many('product.pharmaceutical.subfamily', 'family_id', string='Subfamily')
    product_count = fields.Integer(compute="_compute_products_count")
    product_ids = fields.One2many('product.template', 'dw_pharma_family_id', string='Products')
    purchase_ok = fields.Boolean(string='Can be Purchased', default=False, tracking=True)
    sale_ok = fields.Boolean(string='Can be Sold', default=False, tracking=True)
    is_storable = fields.Boolean(help='A storable product is a product for which you manage stock', string='Track Inventory', default=False, tracking=True)
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')],
        string="Tracking", required=True, default='none', tracking=True,
        help="Ensure the traceability of a storable product in your warehouse.")
    use_expiration_date = fields.Boolean(string='Use Expiration Date', tracking=True, copy=False)
    product_detailed_type = fields.Selection([
        ('combo', 'Combo'),
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type',
        help='The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')

    def _compute_products_count(self):
        for product in self:
            product.product_count = len(product.mapped('product_ids'))

    def action_view_product(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Products"),
            'res_model': 'product.template',
            'view_mode': 'kanban,list,form',
            'domain': [('dw_pharma_family_id', '=', self.id)],
            'context': {
                'default_dw_pharma_family_id': self.id,
            },
        }


class DwProductPharmaceuticalSubfamily(models.Model):
    _name = 'product.pharmaceutical.subfamily'
    _description = 'Subfamily'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    family_id = fields.Many2one('product.pharmaceutical.family', string='Family')


class DwProductPharmaceuticalClass(models.Model):
    _name = 'product.pharmaceutical.class'
    _description = 'Class'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    subclass_ids = fields.One2many('product.pharmaceutical.subclass', 'class_id', string='Subclass')


class DwProductPharmaceuticalSubclass(models.Model):
    _name = 'product.pharmaceutical.subclass'
    _description = 'Subclass'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    class_id = fields.Many2one('product.pharmaceutical.class', string='Class')


class DwProductPharmaceuticalForm(models.Model):
    _name = 'product.pharmaceutical.form'
    _description = 'Form'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    subform_ids = fields.One2many('product.pharmaceutical.subform', 'form_id', string='Subform')


class DwProductPharmaceuticalSubform(models.Model):
    _name = 'product.pharmaceutical.subform'
    _description = 'Subform'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    form_id = fields.Many2one('product.pharmaceutical.form', string='Form')


class DwProductPharmaceuticalNetwork(models.Model):
    _name = 'product.pharmaceutical.network'
    _description = 'Network'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    description = fields.Text(string="Description")


class DwProductPharmaceuticalPfDest(models.Model):
    _name = 'product.pharmaceutical.pf.dest'
    _description = 'PF destination'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    description = fields.Text(string="Description")


class DwProductPharmaceuticalNature(models.Model):
    _name = 'product.pharmaceutical.nature'
    _description = 'Nature article'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    description = fields.Text(string="Description")


class DwProductPharmaceuticalSpeciality(models.Model):
    _name = 'product.pharmaceutical.speciality'
    _description = 'Speciality article'

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', )
    description = fields.Text(string="Description")
