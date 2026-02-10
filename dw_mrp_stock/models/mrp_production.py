from odoo import fields, models, _, Command, api
from odoo.exceptions import UserError, MissingError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    dw_transfer_pf_done = fields.Boolean(string='FP Transfer Done', default=False, tracking=True,  help="Indicates if the transfer of finished products is done.")
    dw_is_colture = fields.Boolean(string='MO closed', default=False, tracking=True, help="Indicates if the manufacturing order is closed.")
    dw_leftover_done = fields.Boolean(string='leftover Done', default=False, help="Indicates if leftover products have been processed."
)

    @api.model
    def _prepare_picking_transfer_pf_datas(self, group_id, location_id, location_dest_id, operation_id):
        lines = []
        product_id = self.product_id
        lines.append(
            Command.create({
                'product_id': product_id.id,
                'name': product_id.display_name,
                'product_uom_qty': self.qty_producing,
                'product_uom': self.product_uom_id.id,
                'company_id': self.company_id.id,
                'date': fields.Datetime.now(),
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'procure_method': 'make_to_stock',
                'picking_type_id': self.location_src_id.warehouse_id.int_type_id.id,
                'group_id': group_id.id,
                'production_id': False
            })
        )
        datas = {
            'picking_type_id': operation_id.id,
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'move_type': 'direct',
            'origin': self.name,
            'production_id': self.id,
            'move_ids_without_package': lines
        }
        return datas


    def action_create_picking_transfer_pf(self):
        self.ensure_one()
        self.sudo().write({'dw_transfer_pf_done': True})
        StockPicking = self.env['stock.picking'].sudo()

        group_id = self.procurement_group_id
        if not group_id:
            self.env['procurement.group'].sudo().create({
                'name': self.name,
                'move_type': 'direct',
            })

            self.write({
                'procurement_group_id': group_id.id
            })
        location_src_id = self.location_dest_id
        warehouse_id = location_src_id.warehouse_id
        location_transit_id = warehouse_id.dw_transit_production_id

        if not location_transit_id:
            raise MissingError(_("There is no transit location selected."))

        location_dest_id = warehouse_id.wh_input_stock_loc_id
        in_type_operation = warehouse_id.int_type_id

        data = [
            self._prepare_picking_transfer_pf_datas(group_id, self.location_dest_id, location_transit_id,
                                                    in_type_operation),
            self._prepare_picking_transfer_pf_datas(group_id, location_transit_id, location_dest_id, in_type_operation)
        ]
        
        picking_ids = StockPicking.create(data)

        for pick in picking_ids:
            pick.sudo().action_assign()

        return {
            'name': _('PF Picking(s)'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'stock.picking',
            'domain': [('production_id', '=', self.id), ('id', 'in', picking_ids.ids)],
            'context': {'default_production_id': self.id},
        }

    def action_confirm_mp_colture(self):
        if any(not rec.dw_leftover_done for rec in self):
            raise UserError(_("You can't close without doing the return!"))
        if any(not rec.dw_transfer_pf_done and not rec.mrp_production_source_count for rec in self):
            raise UserError(_('You cannot close without doing the Finished Product Transfer !.'))
        self.sudo().write({'dw_is_colture': True})
