from odoo import _, api, fields, models
import datetime


class DwConsumptionLine(models.Model):
    _name = "consumption.line"

    product_id = fields.Many2one("product.product", required=0, string="Article")
    product_uom = fields.Many2one("uom.uom", required=0, string="Unité")
    product_uom_qty = fields.Float("Quantité")


class DwAdditionalConsumption(models.TransientModel):
    _name = "dw.additional.consumption"

    production_id = fields.Many2one(
        "mrp.production"
    )

    line_ids = fields.Many2many("consumption.line", readonly=0)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        product_id = self.env['mrp.production'].browse(self.env.context['active_id'])
        res["production_id"] = product_id.id
        move_raw_ids = []
        raw_ids = product_id.move_raw_ids.filtered(lambda l: not l.product_id.bom_ids)
        for raw in raw_ids:
            data = [0, 0, {
                'product_id': raw.product_id.id,
                'product_uom_qty': 0,
                'product_uom': raw.product_id.uom_id.id,

            }]
            move_raw_ids.append(data)
        res["line_ids"] = move_raw_ids
        return res

    def action_submit(self):
        production_id = self.production_id
        move_raw_ids = self.line_ids
        vals = move_raw_ids.filtered(lambda l: l.product_uom_qty)
        lines = []
        for val in vals:
            lines.append([0, 0, {
                'product_id': val.product_id.id,
                'name': val.product_id.display_name,
                'product_qty': val.product_uom_qty,
                'product_production_qty': val.product_uom_qty,
                'product_uom_id': val.product_uom.id,
                'date_required': datetime.date.today(),
                'estimated_cost': val.product_id.standard_price,
            }])
        datas = {
            'requested_by': self.env.user.id,
            'project': _('Additional Consumption for %s') % production_id.name,
            'date_start': datetime.date.today(),
            'desired_date': production_id.date_start,
            'latest_date': production_id.date_start,
            'production_id': production_id.id,
            'line_ids': lines,
        }
        if lines:
            self.env['product.request'].sudo().create(datas)
