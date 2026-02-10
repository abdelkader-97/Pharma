from odoo import fields, api, models, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    consumption_ids = fields.One2many(
        'mrp.workorder.consumption',
        'workorder_id'
    )
    technician_ids = fields.Many2many(
        'res.users'
    )

    @api.model
    def open_workorder_tracking_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Workorder Tracking',
            'res_model': 'mrp.workorder.tracking.wizard',
            'views': [[self.env.ref('dw_mrp_base.mrp_workorder_tracking_wizard_view_form').id, 'form']],
            'target': 'fullscreen',
            'flags': {
                'withControlPanel': False,
                'form_view_initial_mode': 'edit',
            },
            'context': {
                'refresh_move_lines': True
            }
        }

    def action_view_consumptions_view(self):
        tree_view = self.env.ref('dw_mrp_base.mrp_workorder_consumption_list')
        return {
            'name': _('Workorder consumptions'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.workorder.consumption',
            'target': 'new',
            'view_mode': 'list',
            'views': [(tree_view.id, 'list')],
            'domain': [('workorder_id', '=', self.id)],
            'context':{
                'default_workorder_id':self.id,
                'workorder_id':self.id,
                'refresh_move_lines':True,
            }
        }

    def create(self, vals):
        result = super().create(vals)
        for res in result:
            if res.operation_id:
                lines = []
                for consumption in res.operation_id.consumption_model_ids:
                    lines.append((0, 0, {
                        'product_id': consumption.product_id.id,
                        'workorder_id': res.operation_id.id,
                        'quantity': 0,
                        'old_quantity': 0,
                    }))
                res.with_context(refresh_move_lines=False).write({
                    'consumption_ids': lines
                })
        return result


class MrpWorkorderConsumption(models.Model):
    _name = 'mrp.workorder.consumption'

    workorder_id = fields.Many2one(
        'mrp.workorder'
    )
    product_id = fields.Many2one(
        'product.product',
        required=True,
    )
    old_quantity = fields.Float()
    quantity = fields.Float(
        required=True
    )
    bom_product_ids = fields.Many2many(
        "product.product",
    )
    lot_id = fields.Many2one(
        'stock.lot',
    )
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    @api.onchange('workorder_id')
    def _onchange_workorder_id(self):
        return {
            'domain': {
                'bom_product_ids': [('id', '=', self.workorder_id.production_bom_id.bom_line_ids.mapped('product_id'))]
            }
        }

    def new_lot_consumption(self):
        return self.copy({"lot_id": False})

    @api.onchange('product_id')
    def _onchange_product_id(self):
        return {
            'domain': {
                'lot_id': [('product_id', '=', self.product_id.id)]
            }
        }

    def refresh_move_lines(self):
        move_id = self.workorder_id.production_id.move_raw_ids.filtered(
            lambda l: l.product_id == self._origin.product_id)
        if move_id:
            move_id.refresh_lines(self._origin.quantity, self._origin.old_quantity, self._origin.lot_id, self._origin)

    @api.model
    def create(self, vals):
        if 'old_quantity' not in vals:
            vals['old_quantity'] = vals['quantity']
        res = super().create(vals)
        if self.env.context.get('refresh_move_lines'):
            res.refresh_move_lines()
        return res

    def write(self, vals):
        if 'quantity' in vals and 'old_quantity' not in vals and self.old_quantity != vals['quantity']:
            vals['old_quantity'] = self.quantity
        res = super().write(vals)
        if self.env.context.get('refresh_move_lines'):
            for rec in self:
                rec.refresh_move_lines()
        return res
