import datetime

from odoo import fields, models



class StockMove(models.Model):
    _inherit = 'stock.move'

    def refresh_lines(self, quantity, old_quantity, lot_id, consumption_id):
        context = self.env.context.get('new_move_line')
        # in case there is some lines
        move_line_ids = self.move_line_ids.filtered(lambda l: l.consumption_id == consumption_id)
        if move_line_ids and not context:
            for line in move_line_ids:
                if line.consumption_id == consumption_id:
                    line.lot_id = lot_id
                    quantity = (line.quantity - old_quantity + quantity) \
                        if old_quantity > 0 and quantity > 0 and quantity != line.quantity else 0 if quantity == 0 \
                        else quantity

                    quantity_product_uom = (line.quantity_product_uom - old_quantity + quantity) \
                        if old_quantity > 0 and quantity > 0 and quantity != line.quantity_product_uom else 0 if quantity == 0 \
                        else quantity
                    line.quantity = quantity
                    line.quantity_product_uom = quantity_product_uom
        else:
            datas = {
                'lot_id': lot_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'product_id': consumption_id.product_id.id,
                'quantity': quantity,
                'quantity_product_uom': quantity,
                'product_uom_id': consumption_id.product_id.uom_id.id,
                'company_id': self.env.company.id,
                'date': datetime.datetime.now(),
                'move_id': self.id,
                'consumption_id': consumption_id.id
            }
            self.env['stock.move.line'].sudo().create(datas)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    consumption_id = fields.Many2one(
        'mrp.workorder.consumption',
    )
