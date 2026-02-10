from odoo import models, fields


class QualityProductTemplate(models.Model):
    _inherit = 'product.template'

    quality_model_id = fields.Many2one('dw.quality.check.product.model', string='Quality Model')
    auto_qc_gen = fields.Boolean(string="auto-generated quality check.")
    dw_analysis_report_ids = fields.One2many('dw.analyse.report', 'product_id', string='Analyse Report')
    dw_sampling_ids = fields.One2many('dw.quality.sampling', 'product_id', string='Sampling')
    dw_sampling_count = fields.Integer('# sampling',
                                       compute='_compute_sampling_count', compute_sudo=False)

    def _compute_sampling_count(self):
        for product in self:
            product.dw_sampling_count = len(product.dw_sampling_ids)

    def action_open_sampling(self):
        self.ensure_one()
        return {
            'name': 'Sampling',
            'type': 'ir.actions.act_window',
            'res_model': 'dw.quality.sampling',
            'view_mode': 'list,form',
            'domain': [('product_tmpl_id', '=', self.id)],
            'context': {
                'default_product_tmpl_id': self.id,
                'default_product_id': self.product_variant_ids and self.product_variant_ids[0].id or False,
            },
        }

class QualityProductProduct(models.Model):
    _inherit = 'product.product'

    quality_model_id = fields.Many2one('dw.quality.check.product.model', string='Quality Model')
    auto_qc_gen = fields.Boolean(string="auto-generated quality check.")
    dw_analysis_report_ids = fields.One2many('dw.analyse.report', 'product_id', string='Analyse Report')
    dw_sampling_ids = fields.One2many('dw.quality.sampling', 'product_id', string='Sampling')
    dw_sampling_count = fields.Integer('# sampling',
                                       compute='_compute_sampling_count', compute_sudo=False)

    def _compute_sampling_count(self):
        for product in self:
            product.dw_sampling_count = len(product.dw_sampling_ids)

    def action_open_sampling(self):
        self.ensure_one()
        return {
            'name': 'Sampling',
            'type': 'ir.actions.act_window',
            'res_model': 'dw.quality.sampling',
            'view_mode': 'list,form',
            'domain': [('product_id', '=', self.id)],
            'context': {
                'default_product_id': self.id,
            },
        }