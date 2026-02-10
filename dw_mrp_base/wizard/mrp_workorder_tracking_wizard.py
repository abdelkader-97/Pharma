# -*- coding:utf-8 -*-

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class MrpProductionWorkorderTrackingWizard(models.TransientModel):
    _name = 'mrp.workorder.tracking.wizard'
    _description = 'Workorder Tracking'

    user_id = fields.Many2one("res.users", compute='_compute_user_id')
    production_id = fields.Many2one('mrp.production', 'Production', required=True, )
    production_ids = fields.Many2many('mrp.production', compute='_compute_production_ids', )
    workorder_id = fields.Many2one('mrp.workorder', 'Workorder', required=True, )
    workorder_state = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('progress', 'Started'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ],
        string='Workorder State',
        related='workorder_id.state',
    )

    # RELATED FIELDS
    operation_id = fields.Many2one(related='workorder_id.operation_id')
    worksheet = fields.Binary('Worksheet', related='operation_id.worksheet', readonly=True)
    worksheet_type = fields.Selection(string='Worksheet Type', related='operation_id.worksheet_type', readonly=True)
    worksheet_google_slide = fields.Char('Worksheet URL', related='operation_id.worksheet_google_slide', readonly=True)
    # is_first_step = fields.Boolean(related='workorder_id.is_first_step')
    # is_last_step = fields.Boolean(related='workorder_id.is_last_step')
    workorder_ids = fields.One2many(related="production_id.workorder_ids", )
    consumption_ids = fields.One2many('mrp.workorder.consumption', 'workorder_id',
                                      related='workorder_id.consumption_ids', readonly=False, )
    workcenter_id = fields.Many2one(related='workorder_id.workcenter_id', readonly=False)
    production_state = fields.Selection(related='workorder_id.production_state', readonly=False)
    working_state = fields.Selection(related='workorder_id.working_state', readonly=False)
    state_workorder = fields.Selection(related='workorder_id.state', readonly=False)
    is_user_working = fields.Boolean(related='workorder_id.is_user_working', readonly=False)

    state = fields.Selection(related='production_id.state', readonly=True)
    move_list_raw_ids = fields.One2many('stock.move', compute='_move_list_raw_ids')
    emp_pin = fields.Char("PIN employee", required=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.user.company_id,
    )

    @api.depends('workorder_id')
    def _move_list_raw_ids(self):
        for rec in self:
            product_ids = rec.workorder_id.operation_id.consumption_model_ids.product_id.ids
            rec.move_list_raw_ids = self.env['stock.move'].sudo().search(
                [('product_id', '=', product_ids), ('id', 'in', rec.production_id.move_raw_ids.ids),
                 ("company_id", '=', self.company_id.id)])

    @api.depends('user_id')
    def _compute_production_ids(self):
        for rec in self:
            workorder_ids = self.get_user_workorder(rec.user_id, False)
            # Get all productions related to the pending workorders
            production_ids = workorder_ids.mapped('production_id').filtered(
                lambda production: production.company_id.id == self.company_id.id)
            rec.production_ids = production_ids

    @api.depends('emp_pin')
    def _compute_user_id(self):
        for rec in self:
            rec.user_id = self.env['res.users'].search(
                [("employee_id.company_id", '=', self.company_id.id), ('employee_id.pin', '=', rec.emp_pin)],
                limit=1) if rec.emp_pin else None

    @api.onchange('production_id')
    def _onchange_production_id(self):
        # Reinitialize workorder_id
        self.workorder_id = False

        # Initialize empty domain
        domain = []
        mtw_domain = []

        if self.user_id or self.production_id:
            # Get all the pending workorder_ids related to the selected technician
            workorder_ids = self.get_user_workorder(self.user_id, self.production_id)

            # Initialize the workorder_id with the current running task
            started_workorder_ids = workorder_ids.filtered(
                lambda workorder: workorder.state in ('progress', 'pending', 'ready'))
            self.workorder_id = started_workorder_ids if len(started_workorder_ids) < 2 else started_workorder_ids[0]

            # Add filter to domain
            domain += [('id', 'in', started_workorder_ids.ids)]

        # Return domain

        return {
            'domain': {
                'workorder_id': domain,
            }
        }

    def button_start(self):
        self.ensure_one()
        # Raise error if the Task is not yet defined
        if not self.workorder_id:
            raise ValidationError(
                _('You have to select the Workorder first')
            )
        # Raise error if the Technician is not yet defined
        if not self.user_id:
            raise ValidationError(
                _('You have to select the User first')
            )
        return self.workorder_id.button_start()

    def button_pending(self):
        self.ensure_one()
        # Raise error if the Task is not yet defined
        if not self.workorder_id:
            raise ValidationError(
                _('You have to select the Workorder first')
            )
        # Raise error if the Technician is not yet defined
        if not self.user_id:
            raise ValidationError(
                _('You have to select the User first')
            )

        return self.workorder_id.button_pending()

    def button_finish(self):
        self.ensure_one()
        # Raise error if the Task is not yet defined
        if not self.workorder_id:
            raise ValidationError(
                _('You have to select the Workorder first')
            )
        # Raise error if the Technician is not yet defined
        if not self.user_id:
            raise ValidationError(
                _('You have to select the User first')
            )

        return self.workorder_id.button_finish()

    def button_unblock(self):
        self.ensure_one()
        # Raise error if the Task is not yet defined
        if not self.workorder_id:
            raise ValidationError(
                _('You have to select the Workorder first')
            )
        # Raise error if the Technician is not yet defined
        if not self.user_id:
            raise ValidationError(
                _('You have to select the User first')
            )

        return self.workorder_id.button_unblock()

    @api.model
    def get_user_workorder(self, technician_id=None, production_id=None):
        # Initialize Task Model
        WorkorderObj = self.env['mrp.workorder']

        # Initialize domain
        domain = [
            ('state', 'in', ['ready', 'progress', 'pending']),
            ('technician_ids', '!=', False),
            ('production_id.state', 'not in', ('draft', 'done', 'cancel'))
        ]

        # If the production_id parameter is defined add filter to domain on it
        if production_id:
            domain.append(('production_id', '=', production_id.id))

        # Search the workorders
        workorder_ids = WorkorderObj.search(domain)

        # filter only on the task of the right technician if technician_id is defined
        if technician_id:
            workorder_ids = workorder_ids.filtered(lambda t: technician_id in t.technician_ids)

        # Return the tasks
        return workorder_ids
