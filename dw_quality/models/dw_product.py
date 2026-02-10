from math import sqrt
from dateutil.relativedelta import relativedelta
from datetime import datetime

import random

from odoo import api, Command, models, fields, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_round, SQL
from odoo.osv.expression import OR

class ProductTemplate(models.Model):
    _inherit = "product.template"

    quality_pass_qty = fields.Integer(compute='_compute_quality_check_qty')
    quality_fail_qty = fields.Integer(compute='_compute_quality_check_qty')
    quality_button_name = fields.Char("Quality Points")

    @api.depends('product_variant_ids')
    def _compute_quality_check_qty(self):
        for product_tmpl in self:
            product_tmpl.quality_fail_qty, product_tmpl.quality_pass_qty = product_tmpl.product_variant_ids._count_quality_checks()

    def action_see_quality_control_points(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("dw_quality.quality_point_action")
        action['context'] = dict(self.env.context, default_product_ids=self.product_variant_ids.ids)

        domain_in_products_or_categs = ['|', ('product_ids', 'in', self.product_variant_ids.ids), ('product_category_ids', 'parent_of', self.categ_id.ids)]
        domain_no_products_and_categs = [('product_ids', '=', False), ('product_category_ids', '=', False)]
        action['domain'] = OR([domain_in_products_or_categs, domain_no_products_and_categs])
        return action

    def action_see_quality_checks(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("dw_quality.quality_check_action_main")
        action['context'] = dict(self.env.context, default_product_id=self.product_variant_id.id, create=False)
        action['domain'] = [
            '|',
                ('product_id', 'in', self.product_variant_ids.ids),
                '&',
                    ('measure_on', '=', 'operation'),
                    ('picking_id.move_ids.product_tmpl_id', '=', self.id),
        ]
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    quality_pass_qty = fields.Integer(compute='_compute_quality_check_qty')
    quality_fail_qty = fields.Integer(compute='_compute_quality_check_qty')

    def _compute_quality_check_qty(self):
        for product in self:
            product.quality_fail_qty, product.quality_pass_qty = product._count_quality_checks()

    def _count_quality_checks(self):
        quality_fail_qty = 0
        quality_pass_qty = 0
        domain = [
            '|',
                ('product_id', 'in', self.ids),
                '&',
                    ('measure_on', '=', 'operation'),
                    ('picking_id.move_ids.product_id', 'in', self.ids),
            ('company_id', '=', self.env.company.id),
            ('quality_state', '!=', 'none')
        ]
        quality_checks_by_state = self.env['dw.quality.check']._read_group(domain, ['quality_state'], ['__count'])
        for quality_state, count in quality_checks_by_state:
            if quality_state == 'fail':
                quality_fail_qty = count
            elif quality_state == 'pass':
                quality_pass_qty = count

        return quality_fail_qty, quality_pass_qty

    def action_see_quality_control_points(self):
        self.ensure_one()
        action = self.product_tmpl_id.action_see_quality_control_points()
        action['context'].update(default_product_ids=self.ids)

        domain_in_products_or_categs = ['|', ('product_ids', 'in', self.ids), ('product_category_ids', 'parent_of', self.categ_id.ids)]
        domain_no_products_and_categs = [('product_ids', '=', False), ('product_category_ids', '=', False)]
        action['domain'] = OR([domain_in_products_or_categs, domain_no_products_and_categs])
        return action

    def action_see_quality_checks(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("dw_quality.quality_check_action_main")
        action['context'] = dict(self.env.context, default_product_id=self.id, create=False)
        action['domain'] = [
            '|',
                ('product_id', '=', self.id),
                '&',
                    ('measure_on', '=', 'operation'),
                    ('picking_id.move_ids.product_id', '=', self.id),
        ]
        return action

    def _additional_quality_point_where_clause(self) -> SQL:
        return SQL()