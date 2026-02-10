from odoo import fields, api, models, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    lot_dates_set = fields.Boolean(default=False)
    use_expiration_date = fields.Boolean(related='product_id.use_expiration_date', store=1)
    extra_cost = fields.Float(readonly=False, compute="_compute_extra_cost", store=1)

    @api.depends('lot_producing_id', 'lot_producing_id.expiration_date')
    def _compute_lot_dates_set(self):
        for record in self:
            if record.lot_producing_id and record.lot_producing_id.expiration_date:
                record.lot_dates_set = True
            else:
                record.lot_dates_set = False

    def action_cancel(self):
        super().action_cancel()
        if self.lot_producing_id:
            self.lot_producing_id.action_archive()

    def action_set_lot_dates(self):
        form_view = self.env.ref('dw_mrp_base.mrp_production_lot_wizard_form')

        return {
            'name': _('Set Production lot dates'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production.lot',
            'target': 'new',
            'view_mode': 'form',
            'views': [(form_view.id, 'form')],
            'domaine': [('production_id', '=', self.id)],
            'context': {
                'default_production_id': self.id,
                'default_lot_id': self.lot_producing_id.id,
            }
        }

    @api.onchange("product_id", "bom_id")
    def onchange_dw_location_component(self):
        bom_id = self.bom_id
        if bom_id and bom_id.dw_force_mrp_config and bom_id.dw_location_component_id:
            self.location_src_id = bom_id.dw_location_component_id

    @api.depends("bom_id")
    def _compute_extra_cost(self):
        for prod in self:
            prod.extra_cost = prod.bom_id.dw_extrat_cost if prod.bom_id else 0
