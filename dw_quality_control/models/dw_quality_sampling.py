from odoo import models, fields, api, _


class DwSampling(models.Model):
    _name = 'dw.quality.sampling'
    _description = 'Sampling'
    _inherit = ['mail.thread']

    name = fields.Char(
        'Reference', copy=False, default=lambda self: _('New'), required=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',
        check_company=True, domain="[('type', 'in', ['product', 'consu'])]", required=True)
    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        check_company=True, index=True,
        domain="[('type', 'in', ['product', 'consu'])]")
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure', required=True,
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_tmpl_id.uom_id.category_id')
    sampling_date = fields.Date(string='Sampling Date', default=fields.Date.today)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    dw_sampling_line_ids = fields.One2many('dw.quality.sampling.line', 'sampling_id', string='Sampling Lines')

    @api.model_create_multi
    def create(self, vals_list):
        IrSequence = self.env['ir.sequence']
        for vals in vals_list:
            if not vals.get("name") or vals['name'] == _('New'):
                seq_name = IrSequence.next_by_code('dw.quality.sampling.seq')
                vals['name'] = seq_name or _('New')
        return super().create(vals_list)

    @api.depends('product_id')
    def _compute_product_uom_id(self):
        """ Changes UoM if product_id changes. """
        for record in self:
            record.product_uom_id = record.product_id.uom_id.id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_tmpl_id = self.product_id.product_tmpl_id

class DwSamplingLine(models.Model):
    _name = 'dw.quality.sampling.line'
    _description = 'Sampling Line'

    sampling_id = fields.Many2one('dw.quality.sampling', string='Sampling', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True, check_company=True)
    company_id = fields.Many2one(
        related='sampling_id.company_id', store=True, index=True, readonly=True)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial Number', domain="[('product_id', '=', product_id)]",
                             check_company=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        required=True,
        help="Unit of Measure is the unit of measurement for the inventory control",
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
