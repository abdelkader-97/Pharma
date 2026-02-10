from odoo.exceptions import MissingError

from odoo import models, fields, api, _


class StockLotReanalyseWizard(models.TransientModel):
    _name = 'stock.lot.reanalyse.wizard'
    _description = 'Stock Lot reanalyse Wizard'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        context = self.env.context
        lot_id = context.get('default_lot_id')
        if not lot_id:
            raise MissingError(_('No lot provided. Please ensure the wizard is opened with a lot.'))

        lot = self.env['stock.lot'].browse(lot_id)

        company_id = context.get('default_company_id')

        quant_ids = lot.quant_ids.filtered(
            lambda l: l.location_id.usage == 'internal'
                      and l.location_id.perform_quality_lot_reanalyze
                      and l.quantity > 0
        )

        line_vals = []
        for quant in quant_ids:
            line_vals.append({
                'quant_id': quant.id,
                'location_id': quant.location_id.id,
                'company_id': company_id,
                'uom_id': quant.product_uom_id.id,
                'quantity': quant.quantity
            })

        line_records = self.env['stock.lot.reanalyse.line.wizard'].create(line_vals)

        res["line_ids"] = [(6, 0, line_records.ids)]

        return res

    company_id = fields.Many2one('res.company')

    reason_id = fields.Many2one('stock.lot.cancel.reason', string='Reason')
    note = fields.Text(string='Note')
    lot_id = fields.Many2one('stock.lot', string='Stock Lot', required=True)
    line_ids = fields.Many2many(
        'stock.lot.reanalyse.line.wizard', string='lines'
    )

    def confirm(self):
        lot_id = self.lot_id
        lot_id._create_history_record(self.lot_id.lot_quarantine_status, 'reanalyzed', is_quarantine=True)
        lot_id.set_lot_analyse_status('reanalyzed')
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']
        StockMoveLine = self.env['stock.move.line']
        warehouse_groups = {}
        for line in self.line_ids:
            warehouse = line.location_id.warehouse_id
            if not warehouse.quality_reanalyze_op_id:
                raise MissingError(
                    _('Warehouse %s does not have a quality reanalyze operation picking type.') % warehouse.name)
            if warehouse not in warehouse_groups:
                warehouse_groups[warehouse] = []
            warehouse_groups[warehouse].append(line)

        for warehouse, lines in warehouse_groups.items():
            picking_type = warehouse.quality_reanalyze_op_id
            location_dest_id = picking_type.default_location_dest_id.id
            location_location_id = lines[0].location_id.id

            picking = StockPicking.sudo().create({
                'picking_type_id': picking_type.id,
                'location_id': location_location_id,
                'location_dest_id': location_dest_id,
                'company_id': self.company_id.id,
            })

            move_vals = []
            move_line_vals = []
            product_id = lot_id.product_id
            for line in lines:
                move_vals.append({
                    'picking_id': picking.id,
                    'product_id': product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                    'location_id': line.location_id.id,
                    'location_dest_id': location_dest_id,
                    'name': product_id.name,

                })
            moves = StockMove.sudo().create(move_vals)

            for move, line in zip(moves, lines):
                move_line_vals.append({
                    'move_id': move.id,
                    'quant_id': line.quant_id.id,
                    'picking_id': picking.id
                })

            StockMoveLine.sudo().create(move_line_vals)
            picking.action_confirm()
            picking.button_validate()


class StockLotReanalyseLineWizard(models.TransientModel):
    _name = 'stock.lot.reanalyse.line.wizard'
    _description = 'Stock Lot reanalyse line Wizard'

    quant_id = fields.Many2one(
        'stock.quant',
    )
    location_id = fields.Many2one(
        'stock.location', string='Location', domain=[('perform_quality_lot_reanalyze', '=', True)], check_company=True
    )
    quantity = fields.Float(string="Qte", default=1)
    uom_id = fields.Many2one(
        'uom.uom',
    )
    company_id = fields.Many2one(
        'res.company', readonly=0
    )
