import ast
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class QualityAlertTeam(models.Model):
    _name = "dw.quality.alert.team"
    _inherit = ['mail.thread']
    _description = "Quality Alert Team"
    _order = "sequence, id"

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', index=True)
    sequence = fields.Integer('Sequence')
    check_count = fields.Integer('# Quality Checks', compute='_compute_check_count')
    alert_count = fields.Integer('# Quality Alerts', compute='_compute_alert_count')
    color = fields.Integer('Color', default=1)

    def _compute_check_count(self):
        check_data = self.env['dw.quality.check']._read_group([('team_id', 'in', self.ids), ('quality_state', '=', 'none')], ['team_id'], ['__count'])
        check_result = {team.id: count for team, count in check_data}
        for team in self:
            team.check_count = check_result.get(team.id, 0)

    def _compute_alert_count(self):
        alert_data = self.env['dw.quality.alert']._read_group([('team_id', 'in', self.ids), ('stage_id.done', '=', False)], ['team_id'], ['__count'])
        alert_result = {team.id: count for team, count in alert_data}
        for team in self:
            team.alert_count = alert_result.get(team.id, 0)

    def _get_quality_team(self, domain):
        team_id = self.env['dw.quality.alert.team'].search(domain, limit=1).id
        if team_id:
            return team_id
        else:
            raise UserError(_("No quality team found for this company.\n"
                              "Please go to configuration and create one first."))