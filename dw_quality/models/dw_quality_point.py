from math import sqrt
from dateutil.relativedelta import relativedelta
from datetime import datetime

import random

from odoo import api, Command, models, fields, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_round, SQL
from odoo.osv.expression import OR

class QualityPoint(models.Model):
    _name = "dw.quality.point"
    _inherit = ['mail.thread']
    _description = "Quality Control Point"
    _order = "sequence, id"
    _check_company_auto = True

    def _get_default_team_id(self):
        company_id = self.company_id.id or self.env.context.get('default_company_id', self.env.company.id)
        return self.team_id._get_quality_team(self.env['dw.quality.alert.team']._check_company_domain(company_id))

    def _get_default_test_type_id(self):
        domain = self._get_type_default_domain()
        return self.env['dw.quality.point.test_type'].search(domain, limit=1).id

    name = fields.Char(
        'Reference', copy=False, default=lambda self: _('New'),
        required=True)
    sequence = fields.Integer('Sequence')
    title = fields.Char('Title')
    team_id = fields.Many2one(
        'dw.quality.alert.team', 'Team', check_company=True,
        default=_get_default_team_id, required=True)
    product_ids = fields.Many2many(
        'product.product', string='Products',
        check_company=True,
        domain="[('type', '=', 'consu')]",
        help="Quality Point will apply to every selected Products.")
    product_category_ids = fields.Many2many(
        'product.category', string='Product Categories',
        help="Quality Point will apply to every Products in the selected Product Categories.")

    picking_type_ids = fields.Many2many(
        'stock.picking.type', string='Operation Types', required=True, check_company=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, index=True,
        default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', 'Responsible',
        check_company=True)
    active = fields.Boolean(default=True)
    check_count = fields.Integer(compute="_compute_check_count")
    check_ids = fields.One2many('dw.quality.check', 'point_id')
    test_type_id = fields.Many2one('dw.quality.point.test_type', 'Test Type', help="Defines the type of the quality control point.",
                                   required=True, default=_get_default_test_type_id, tracking=True)
    test_type = fields.Char(related='test_type_id.technical_name', readonly=True)
    note = fields.Html('Note')
    reason = fields.Html('Cause')
    failure_message = fields.Html('Failure Message')
    failure_location_ids = fields.Many2many('stock.location', string="Failure Locations", domain="[('usage', '=', 'internal')]",
                            help="If a quality check fails, a location is chosen from this list for each failed quantity.")
    measure_on = fields.Selection([
        ('operation', 'Operation'),
        ('product', 'Product'),
        ('move_line', 'Quantity')], string="Control per", default='product', required=True,
        help="""Operation = One quality check is requested at the operation level.
                  Product = A quality check is requested per product.
                 Quantity = A quality check is requested for each new product quantity registered, with partial quantity checks also possible.""")
    measure_frequency_type = fields.Selection([
        ('all', 'All'),
        ('random', 'Randomly'),
        ('periodical', 'Periodically'),
        ('on_demand', 'On-demand')], string="Control Frequency",
        default='all', required=True)
    measure_frequency_value = fields.Float('Percentage')  # TDE RENAME ?
    measure_frequency_unit_value = fields.Integer('Frequency Unit Value')  # TDE RENAME ?
    measure_frequency_unit = fields.Selection([
        ('day', 'Days'),
        ('week', 'Weeks'),
        ('month', 'Months')], default="day")  # TDE RENAME ?
    is_lot_tested_fractionally = fields.Boolean(string="Lot Tested Fractionally", help="Determines if only a fraction of the lot should be tested",
                                                compute="_compute_is_lot_tested_fractionally")
    testing_percentage_within_lot = fields.Float(help="Defines the percentage within a lot that should be tested", default=100)
    norm = fields.Float('Norm', digits='Quality Tests')  # TDE RENAME ?
    tolerance_min = fields.Float('Min Tolerance', digits='Quality Tests')
    tolerance_max = fields.Float('Max Tolerance', digits='Quality Tests')
    norm_unit = fields.Char('Norm Unit', default=lambda self: 'mm')  # TDE RENAME ?
    average = fields.Float(compute="_compute_standard_deviation_and_average")
    standard_deviation = fields.Float(compute="_compute_standard_deviation_and_average")

    def _compute_check_count(self):
        check_data = self.env['dw.quality.check']._read_group([('point_id', 'in', self.ids)], ['point_id'], ['__count'])
        result = {point.id: count for point, count in check_data}
        for point in self:
            point.check_count = result.get(point.id, 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('dw.quality.point') or _('New')
        return super().create(vals_list)

    @api.depends('name', 'title')
    @api.depends_context('on_demand_wizard')
    def _compute_display_name(self):
        if 'on_demand_wizard' in self.env.context:
            for record in self:
                record.display_name = f'{record.name} - {record.title}' if record.title else record.name
        else:
            super()._compute_display_name()

    @api.depends('testing_percentage_within_lot')
    def _compute_is_lot_tested_fractionally(self):
        for point in self:
            point.is_lot_tested_fractionally = point.testing_percentage_within_lot < 100

    def _compute_standard_deviation_and_average(self):
        for point in self:
            if point.test_type != 'measure':
                point.average = 0
                point.standard_deviation = 0
                continue
            mean = 0.0
            s = 0.0
            n = 0
            for check in point.check_ids.filtered(lambda x: x.quality_state != 'none'):
                n += 1
                delta = check.measure - mean
                mean += delta / n
                delta2 = check.measure - mean
                s += delta * delta2

            if n > 1:
                point.average = mean
                point.standard_deviation = sqrt( s / ( n - 1))
            elif n == 1:
                point.average = mean
                point.standard_deviation = 0.0
            else:
                point.average = 0.0
                point.standard_deviation = 0.0

    @api.onchange('norm')
    def onchange_norm(self):
        if self.tolerance_max == 0.0:
            self.tolerance_max = self.norm

    def check_execute_now(self):
        self.ensure_one()
        if self.measure_frequency_type == 'all':
            return True
        elif self.measure_frequency_type == 'random':
            return (random.random() < self.measure_frequency_value / 100.0)
        elif self.measure_frequency_type == 'periodical':
            delta = False
            if self.measure_frequency_unit == 'day':
                delta = relativedelta(days=self.measure_frequency_unit_value)
            elif self.measure_frequency_unit == 'week':
                delta = relativedelta(weeks=self.measure_frequency_unit_value)
            elif self.measure_frequency_unit == 'month':
                delta = relativedelta(months=self.measure_frequency_unit_value)
            date_previous = datetime.today() - delta
            checks = self.env['dw.quality.check'].search([
                ('point_id', '=', self.id),
                ('create_date', '>=', date_previous.strftime(DEFAULT_SERVER_DATETIME_FORMAT))], limit=1)
            return not(bool(checks))
        return super(QualityPoint, self).check_execute_now()

    def _get_type_default_domain(self):
        domain = [('technical_name', '=', 'passfail')]
        return domain

    def action_see_quality_checks(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("dw_quality.quality_check_action_main")
        action['domain'] = [('point_id', '=', self.id)]
        action['context'] = {
            'default_company_id': self.company_id.id,
            'default_point_id': self.id
        }
        return action

    def _get_checks_values(self, products, company_id, existing_checks=False):
        quality_points_list = []
        point_values = []
        if not existing_checks:
            existing_checks = []
        for check in existing_checks:
            point_key = (check.point_id.id, check.team_id.id, check.product_id.id)
            quality_points_list.append(point_key)

        for point in self:
            if not point.check_execute_now():
                continue
            point_products = point.product_ids

            if point.product_category_ids:
                point_product_from_categories = self.env['product.product'].search([('categ_id', 'child_of', point.product_category_ids.ids), ('id', 'in', products.ids)])
                point_products |= point_product_from_categories

            if not point.product_ids and not point.product_category_ids:
                point_products |= products

            for product in point_products:
                if product not in products:
                    continue
                point_key = (point.id, point.team_id.id, product.id)
                if point_key in quality_points_list:
                    continue
                point_values.append({
                    'point_id': point.id,
                    'measure_on': point.measure_on,
                    'team_id': point.team_id.id,
                    'product_id': product.id,
                })
                quality_points_list.append(point_key)

        return point_values

    @api.model
    def _get_domain(self, product_ids, picking_type_id, measure_on=False, on_demand=False):
        domain = [('picking_type_ids', 'in', picking_type_id.ids)]
        domain_in_products_or_categs = ['|', ('product_ids', 'in', product_ids.ids), ('product_category_ids', 'parent_of', product_ids.categ_id.ids)]
        domain_no_products_and_categs = [('product_ids', '=', False), ('product_category_ids', '=', False)]
        domain += OR([domain_in_products_or_categs, domain_no_products_and_categs])
        if measure_on:
            domain += [('measure_on', '=', measure_on)]
        domain += [('measure_frequency_type', '=' if on_demand else '!=', 'on_demand')]

        return domain
