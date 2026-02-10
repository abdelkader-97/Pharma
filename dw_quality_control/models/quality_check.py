from odoo.exceptions import MissingError

from odoo import models, fields, api, Command, _


class QualityCheck(models.Model):
    _inherit = "dw.quality.check"

    use_expiration_date = fields.Boolean(related="lot_id.use_expiration_date", store=1)
    expiration_date = fields.Datetime(related="lot_id.expiration_date", store=1)
    lot_id = fields.Many2one(compute="_compute_lot_id", store=1, readonly=0,check_company=0)
    final_product = fields.Boolean()
    raw_material = fields.Boolean()
    product_tracking = fields.Selection([
        ('serial', 'Serial'),
        ('lot', 'Lot'),
        ('none', 'None'),
    ], store=1,
        related='product_id.tracking'
    )
    lot_domain = fields.Many2many('stock.lot', compute='_compute_lot_domain', store=1)
    line_ids = fields.One2many(
        'dw.quality.check.line',
        'quality_check_id',
        store=True,
        compute='_compute_quality_check_line_ids',
        readonly=False
    )
    simple_request_ids = fields.One2many(
        'quality.sample.request',
        'quality_check_id',

    )
    partner_supplier_id = fields.Many2one('res.partner', string="Supplier", related="dw_purchase_id.partner_id",
                                          store=1)
    dw_num_supplier = fields.Char(string='Lot Ref', related="lot_id.ref",  store=1)
    check_number = fields.Char(string='Check Number')
    dw_reception_id = fields.Many2one('stock.picking', string="Reception", compute="_compute_supplier_information",
                                      store=1)
    dw_purchase_id = fields.Many2one('purchase.order', string="Purchase", compute="_compute_supplier_information",
                                     store=1)
    location_id = fields.Many2one('stock.location', compute='_compute_per_picking_id_lot_id')
    picking_lot_quantity = fields.Float(compute='_compute_per_picking_id_lot_id', string="Quantity Lot")
    production_date = fields.Date(string="Production Date")
    dw_analyse_report_ids = fields.One2many('dw.analyse.report', 'quality_check_id', string='Analyse Report')

    @api.depends('picking_id')
    def _compute_supplier_information(self):
        for record in self:
            picking_id = record.picking_id
            if picking_id and picking_id.dw_qc_picking_origin_id:
                dw_qc_picking_origin_id = picking_id.dw_qc_picking_origin_id
                record.dw_purchase_id = dw_qc_picking_origin_id.purchase_id.id or False
                record.dw_reception_id = dw_qc_picking_origin_id.id
            else:
                record.dw_purchase_id = False
                record.dw_reception_id = False

    @api.depends('lot_domain')
    def _compute_lot_id(self):
        for record in self:
            lot_ids = record.lot_domain
            if lot_ids and not record.lot_id:
                lot_id = lot_ids[-1].id
            elif record.lot_id:
                lot_id = record.lot_id.id
            else:
                lot_id = False
            record.lot_id = lot_id

    @api.depends('lot_id', 'picking_id')
    def _compute_per_picking_id_lot_id(self):
        for record in self:
            lot_id = record.lot_id
            picking_id = record.picking_id
            if lot_id and picking_id:
                location_id = picking_id.location_id.id
                record.location_id = location_id
                record.picking_lot_quantity = sum(lot_id.quant_ids.filtered_domain([
                    ('location_id', '=', location_id)
                ]).mapped("quantity"))
            else:
                record.location_id = False
                record.picking_lot_quantity = 0

    @api.depends('product_id')
    def _compute_quality_check_line_ids(self):
        for record in self:
            if not record.product_id or not record.product_id.product_tmpl_id.quality_model_id:
                record.line_ids = [Command.clear()]
                continue

            model_lines = record.product_id.product_tmpl_id.quality_model_id.model_ids

            commands = [Command.clear()]

            for model_line in model_lines:
                commands.append(Command.create({
                    'name': model_line.name,
                    'reference': model_line.reference,
                    'standards': model_line.standards,
                    'result': model_line.result,
                }))

            record.line_ids = commands

    @api.depends('picking_id', "product_id")
    def _compute_lot_domain(self):
        for record in self:
            picking_id = record.picking_id
            product_id = record.product_id
            lot_ids = picking_id.move_line_ids.filtered_domain([('product_id', '=', product_id.id)]).mapped(
                'lot_id') or picking_id.move_line_ids_without_package.filtered_domain(
                [('product_id', '=', product_id.id)]).mapped(
                'lot_id')
            if not lot_ids:
                lot_ids = product_id.stock_quant_ids.mapped("lot_id")
            record.lot_domain = lot_ids

    def button_sample_request(self):
        self.ensure_one()
        product_id = self.product_id
        lot_id = self.lot_id
        location_id = self.location_id
        if not product_id:
            raise MissingError(_("you have to select Product"))
        if not lot_id:
            raise MissingError(_("you have to select a Lot"))
        if not location_id:
            raise MissingError(_("you have to select a source location for the lot"))

        line_ids_data = [Command.create(
            {
                'product_id': product_id.id, 'lot_id': lot_id.id, 'uom_id': self.uom_id.id
            })

        ]
        type_id =location_id.warehouse_id.dw_quality_sample_id or self.env.ref('stock.picking_type_internal')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sample Request',
            'view_mode': 'form',
            'res_model': 'quality.sample.request',
            'context': {'default_quality_check_id': self.id,
                        'default_location_id': location_id.id,
                        'default_location_dest_id': type_id.default_location_dest_id.id or False,
                        'default_product_id': product_id.id,
                        'default_user_id': self.user_id.id,
                        'default_lot_id': lot_id.id,
                        'default_line_ids': line_ids_data,
                        'default_type_id': type_id.id
                        }, }

    def action_view_sample_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sample Request',
            'view_mode': 'list,form',
            'res_model': 'quality.sample.request',
            "domain": [('quality_check_id', '=', self.id)],
            'context': {'create': False, },
        }
