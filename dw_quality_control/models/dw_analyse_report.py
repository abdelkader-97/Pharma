from odoo import models, fields, api


class DwAnalyseReport(models.Model):
    _name = 'dw.analyse.report'
    _description = 'Analyse Report'

    product_id = fields.Many2one('product.product', string='Product', required=True, check_company=True)
    company_id = fields.Many2one('res.company', string='Company',required=True, default=lambda self: self.env.company)
    test_id = fields.Many2one('dw.analyse.test' ,string='Test')
    methode_ids = fields.Many2many('dw.analyse.methode',string='Methode')
    norm_id= fields.Many2one('dw.analyse.norm', string='Norm')
    quality_check_id = fields.Many2one('dw.quality.check', string='Quality Check')
    resultat = fields.Char(string='Resultat')
    resultat_type = fields.Selection([
        ('conform', 'Conform'),
        ('non_conform', 'Non Conform'),
        ('reanalyse', 'Reanalyse')],
        string='Resultat Type')

    @api.onchange('quality_check_id')
    def _onchange_quality_check_id(self):
        if self.quality_check_id:
                self.company_id = self.quality_check_id.company_id
