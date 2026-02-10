# -*- coding:utf-8 -*-

from odoo import fields, models, api

class StockLot(models.Model):
    _inherit = 'stock.move.line'

    @api.model
    def create(self, values):
        res = super().create(values)
        if res and res.product_id and res.product_id.auto_generate_lot_number:
            res.lot_name = generate_sequence(res.product_id.lot_code, res.product_id.sequence_size, res.product_id.counter)
            res.product_id.counter += 1
        return res

def generate_sequence(prefix, sequence_size, seq):
    formatted_seq = f"{seq:0{sequence_size}d}"
    return f"{prefix}{formatted_seq}"

