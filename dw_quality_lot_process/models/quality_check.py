from odoo import models, fields


class QualityCheck(models.Model):
    _inherit = "dw.quality.check"

    check_lot_compliance = fields.Boolean(related='product_id.requires_lot_compliance_check')
    initial_qty = fields.Float(string="Initial Quanity", readonly=True)
    partial_liberation_qc = fields.Boolean("Partial Liberation", default=False)

    def _set_initial_qty(self):
        self.initial_qty = self.picking_lot_quantity
        self.lot_id.initial_qty = self.picking_lot_quantity

    def do_pass(self):
        lot_id = self.with_company(self.company_id).lot_id
        if lot_id and lot_id.compliance_check:
            if lot_id.lot_quarantine_status != 'analyzed':
                lot_id.action_set_analyzed()
            lot_id.action_set_conform()
        self._set_initial_qty()
        return super().do_pass()

    def do_fail(self):
        self.with_company(self.company_id)._set_initial_qty()
        return super().do_fail()

    def do_fail_process(self):
        lot_id = self.lot_id
        if lot_id and lot_id.compliance_check:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cancel Lot',
                'res_model': 'stock.lot.cancel.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_lot_id': lot_id.id, 'default_check_quality_id': self.id}
            }

    def do_pass_process(self):
        lot_id = self.lot_id
        if lot_id and lot_id.compliance_check:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Sub Lot REgister',
                'res_model': 'stock.lot.sub.lot.register',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_lot_id': lot_id.id, 'default_check_quality_id': self.id}
            }
