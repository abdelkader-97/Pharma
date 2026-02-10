from odoo import fields, models, _


class StockLot(models.Model):
    _inherit = 'stock.lot'

    lot_status = fields.Selection([
        ('quarantine', 'Quarantine'),
        ('conform', 'Conform'),
        ('not_conform', 'Not Conform'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled')
    ], string="Lot status", default='quarantine', company_dependent=True)

    lot_quarantine_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In progress'),
        ('analyzed', 'Analyzed'),
        ('reanalyzed', 'reanalyzed')
    ], string="Analyse Status", default='draft', company_dependent=True)

    compliance_check = fields.Boolean(related='product_id.requires_lot_compliance_check', readonly=True)
    lot_status_history_ids = fields.One2many('dw.stock.lot.history', 'lot_id', string="Status History")
    initial_qty = fields.Float(string="Initial Quantity", readonly=True, default=lambda self: self.product_qty)
    is_child = fields.Boolean(string="Is Child ?")
    parent_lot_id = fields.Many2one(
        'stock.lot',
        string='Parent Lot',
    )
    children_lot_ids = fields.One2many('stock.lot', 'parent_lot_id', string="Children Lots")

    def set_lot_status(self, status):
        self.lot_status = status

    def set_lot_analyse_status(self, analyse_status):
        self.lot_quarantine_status = analyse_status

    def _create_history_record(self, previous_status, new_status, is_quarantine=False):
        '''This function creates stock.lot.history record'''
        history_vals = {
            'lot_id': self.id,
            'user_id': self.env.user.id,
            'change_date': fields.Datetime.now(),
            'previous_status' if not is_quarantine else 'previous_lot_quarantine_status': previous_status,
            'new_status' if not is_quarantine else 'new_lot_quarantine_status': new_status,
        }
        self.env['dw.stock.lot.history'].sudo().create(history_vals)

    def action_set_quarantine(self):
        self._create_history_record(self.lot_status, 'quarantine')
        self.lot_status = 'quarantine'

    def action_set_conform(self):
        self._create_history_record(self.lot_status, 'conform')
        self.lot_status = 'conform'

    def action_set_not_conform(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel Lot',
            'res_model': 'stock.lot.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lot_id': self.id, 'default_status': 'not_conform'}
        }

    def action_set_blocked(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel Lot',
            'res_model': 'stock.lot.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lot_id': self.id, 'default_status': 'blocked'}
        }

    def action_set_cancelled(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel Lot',
            'res_model': 'stock.lot.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lot_id': self.id, 'default_status': 'cancelled'}
        }

    def action_set_in_progress(self):
        self._create_history_record(self.lot_quarantine_status, 'in_progress', is_quarantine=True)
        self.lot_quarantine_status = 'in_progress'

    def action_set_analyzed(self):
        self._create_history_record(self.lot_quarantine_status, 'analyzed', is_quarantine=True)
        self.lot_quarantine_status = 'analyzed'

    def action_set_reanalyzed(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reanalyze Lot',
            'res_model': 'stock.lot.reanalyse.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lot_id': self.id, 'default_company_id': self.company_id.id}
        }

    def write(self, vals):
        if 'expiration_date' in vals:
            change_date = fields.Datetime.now()
            user_id = self.env.user.id
            history_vals_list = []
            for record in self:
                history_vals_list.append({
                    'lot_id': record.id,
                    'previous_date_expiration': record.expiration_date,
                    'new_date_expiration': vals.get('expiration_date'),
                    'user_id': user_id,
                    'change_date': change_date,
                })

            if history_vals_list:
                self.env['dw.stock.lot.history'].sudo().create(history_vals_list)

        return super(StockLot, self).write(vals)

    def action_view_child_lots(self):
        return {
            "name": _("Sub lots views"),
            "type": "ir.actions.act_window",
            "res_model": "stock.lot",
            'view_mode': 'list,form',
            "domain": [('parent_lot_id', '=', self.id)],
            'context': {
                'default_parent_lot_id': self.id,
            },
        }

    def action_view_parent_lot(self):
        return {
            "name": _("Parent lot views"),
            "type": "ir.actions.act_window",
            "res_model": "stock.lot",
            'view_mode': 'list,form',
            "domain": [('id', '=', self.parent_id.id or False)],
            'context': {
                'create': 0,
            },
        }
