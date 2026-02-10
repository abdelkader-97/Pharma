from math import sqrt
from dateutil.relativedelta import relativedelta
from datetime import datetime

import random

from odoo import api, Command, models, fields, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_round, SQL
from odoo.osv.expression import OR


class QualityAlert(models.Model):
    _name = "dw.quality.alert"
    _inherit = ['mail.thread']
    _description = "Quality Alert"
    _check_company_auto = True

    def _get_default_stage_id(self):
        team_id = self.env.context.get('default_team_id')
        if not team_id and self.env.context.get('active_model') == 'dw.quality.alert.team' and\
                self.env.context.get('active_id'):
            team_id = self.env['dw.quality.alert.team'].browse(self.env.context.get('active_id')).exists().id
        domain = [('team_ids', '=', False)]
        if team_id:
            domain = OR([domain, [('team_ids', 'in', team_id)]])
        return self.env['dw.quality.alert.stage'].search(domain, limit=1).id

    def _get_default_team_id(self):
        company_id = self.company_id.id or self.env.context.get('default_company_id', self.env.company.id)
        domain = ['|', ('company_id', '=', company_id), ('company_id', '=', False)]
        return self.team_id._get_quality_team(domain)

    name = fields.Char('Name', default=lambda self: _('New'), copy=False)
    description = fields.Html('Description')
    stage_id = fields.Many2one(
        'dw.quality.alert.stage', 'Stage', ondelete='restrict',
        group_expand='_read_group_stage_ids',
        default=lambda self: self._get_default_stage_id(),
        domain="['|', ('team_ids', '=', False), ('team_ids', 'in', team_id)]", tracking=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True,
        default=lambda self: self.env.company)
    reason_id = fields.Many2one('dw.quality.reason', 'Root Cause')
    tag_ids = fields.Many2many('dw.quality.tag', string="Tags")
    date_assign = fields.Datetime('Date Assigned')
    date_close = fields.Datetime('Date Closed')
    picking_id = fields.Many2one('stock.picking', 'Picking', check_company=True)
    action_corrective = fields.Html('Corrective Action')
    action_preventive = fields.Html('Preventive Action')
    user_id = fields.Many2one('res.users', 'Responsible', tracking=True, default=lambda self: self.env.user)
    team_id = fields.Many2one(
        'dw.quality.alert.team', 'Team', required=True, check_company=True,
        default=lambda x: x._get_default_team_id())
    partner_id = fields.Many2one('res.partner', 'Vendor', check_company=True)
    check_id = fields.Many2one('dw.quality.check', 'Check', check_company=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product', check_company=True,
        domain="[('type', '=', 'consu')]")
    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        domain="[('product_tmpl_id', '=', product_tmpl_id)]")
    lot_id = fields.Many2one(
        'stock.lot', 'Lot', check_company=True,
        domain="['|', ('product_id', '=', product_id), ('product_id.product_tmpl_id', '=', product_tmpl_id)]")
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority',
        index=True)
    title = fields.Char('Title')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('dw.quality.alert') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        res = super(QualityAlert, self).write(vals)
        if 'stage_id' in vals and self.stage_id.done:
            self.write({'date_close': fields.Datetime.now()})
        return res

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        self.product_id = self.product_tmpl_id.product_variant_ids.ids and self.product_tmpl_id.product_variant_ids.ids[0]

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.team_id:
            self.company_id = self.team_id.company_id or self.env.company

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        team_id = self.env.context.get('default_team_id')
        domain = [('id', 'in', stages.ids)]
        if not team_id and self.env.context.get('active_model') == 'dw.quality.alert.team' and\
                self.env.context.get('active_id'):
            team_id = self.env['dw.quality.alert.team'].browse(self.env.context.get('active_id')).exists().id
        if team_id:
            domain = OR([domain, ['|', ('team_ids', '=', False), ('team_ids', 'in', team_id)]])
        elif not stages:
            domain = [('team_ids', '=', False)]
        stage_ids = stages.sudo()._search(domain, order=stages._order)
        return stages.browse(stage_ids)

    def action_see_check(self):
        return {
            'name': _('Quality Check'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'dw.quality.check',
            'target': 'current',
            'res_id': self.check_id.id,
        }

    @api.depends('name', 'title')
    def _compute_display_name(self):
        for record in self:
            name = record.name + ' - ' + record.title if record.title else record.name
            record.display_name = name

    @api.model
    def name_create(self, name):
        record = self.create({
            'title': name,
        })
        return record.id, record.display_name