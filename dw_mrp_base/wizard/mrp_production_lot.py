from odoo import fields, models


class MrpProductionLot(models.TransientModel):
    _name = "mrp.production.lot"

    production_id = fields.Many2one(
        "mrp.production"
    )
    lot_id = fields.Many2one(
        "stock.lot"
    )
    expiration_date = fields.Datetime(required=True)
    use_date = fields.Datetime(required=False)
    removal_date = fields.Datetime(required=False)
    date_alert = fields.Datetime(required=False)

    def action_submit(self):
        self.lot_id.expiration_date = self.expiration_date
        self.lot_id.use_date = self.use_date
        self.lot_id.removal_date = self.removal_date
        self.lot_id.alert_date = self.date_alert
        self.production_id.lot_dates_set = True
