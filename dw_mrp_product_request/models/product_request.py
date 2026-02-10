import datetime

from odoo.exceptions import UserError

from odoo import _, api, fields, models


class PurchaseProductRequest(models.Model):
    _name = "product.request"
    _description = "Product Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("product.request")

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Request Reference",
        required=True,
        default="New",
        # track_visibility="onchange",
        readonly=True,
    )
    date_start = fields.Date(
        string="Request date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        # track_visibility="onchange",
    )
    desired_date = fields.Date(
        string="Desired reception date",
        help="Date when the user desire to receive the request.",
        default=fields.Date.context_today,
        # track_visibility="onchange",
    )
    latest_date = fields.Date(
        string="Latest reception date",
        help="Date when the user desire to receive the request at latest.",
        default=fields.Date.context_today,
        # track_visibility="onchange",
    )
    project = fields.Char('Project(s)')
    requested_by = fields.Many2one(
        "res.users",
        string="Requested by",
        required=True,
        copy=False,
        # track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
    assigned_to = fields.Many2one(
        "res.users",
        string="Assigned to",
        related="create_uid",
        index=True,
        store=True,
    )
    description = fields.Text(string="Description")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,
    )
    line_ids = fields.One2many(
        comodel_name="product.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('rejected', 'Rejected'),
        ],
        string="State",
        default="draft",
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")

    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )

    purchase_team_members_id = fields.Many2one('res.users', string='Purchase team members')
    financial_validator = fields.Many2one('res.users', string='Financial Validator')
    po_date_approve = fields.Date()
    url = fields.Char()

    request_status = fields.Selection(
        [
            ('available', 'Available'),
            ('not_available', 'Not Available')
        ],
        default="not_available"
    )
    production_id = fields.Many2one(
        'mrp.production'
    )
    roadmap_id = fields.Many2one(
        'mrp.roadmap'
    )
    picking_count = fields.Integer(
        compute='_compute_picking_count'
    )

    # def _compute_picking_count(self):
    #     for record in self:
    #         record.picking_count = len()

    def action_confirm(self):
        self.state = 'done'

    def _prepare_datas(self, group_id, location_id, location_dest_id):
        lines = []

        for val in self.line_ids:
            lines.append([0, 0, {
                'product_id': val.product_id.id,
                'name': val.product_id.display_name,
                'product_uom_qty': val.product_qty,
                'product_uom': val.product_uom_id.id,
                'company_id': self.env.company.id,
                'date': datetime.datetime.now(),
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'procure_method': 'make_to_stock',
                'picking_type_id': self.production_id.location_src_id.warehouse_id.pbm_type_id.id,
                'group_id': group_id.id,
                'production_id': False
            }])
        production_id = self.production_id
        datas = {
            'picking_type_id': production_id.location_src_id.warehouse_id.pbm_type_id.id,
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'move_type': 'direct',
            # 'production_id': production_id.id,
            'origin': production_id.name,
            'product_request_id': self.id,
            'move_ids_without_package': lines
        }
        return datas

    def action_create_picking_request(self):
        """
        This method is used by the product request button. It creates a stock picking and show it
        :return: Action Dict
        """
        # a procurement group is used to centerlize all transfers in one group
        # as for pickings and mrp production

        group_id = self.production_id.procurement_group_id
        if not group_id:
            group_id = self.env['procurement.group'].sudo().create({
                'name': self.production_id.name,
                'move_type': 'direct',
            })

            self.sudo().production_id.write({
                'procurement_group_id': group_id.id
            })

        location_id = self.production_id.location_src_id.warehouse_id.lot_stock_id
        location_transit_id = self.production_id.location_src_id.warehouse_id.dw_transit_production_id
        location_dest_id = self.production_id.location_src_id

        datas = [self._prepare_datas(group_id, location_id, location_transit_id)]
        datas.append(self._prepare_datas(group_id, location_transit_id, location_dest_id))

        picking_ids = self.env['stock.picking'].sudo().create(datas)

        self.action_confirm()
        self.clear_caches()

        return {
            'name': 'Picking(s)',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'stock.picking',
            'domain': [('product_request_id', '=', self.id), ('id', 'in', picking_ids.ids)],
            'context': {'default_product_request_id': self.id},
        }

    def action_view_pickings(self):

        return {
            'name': 'Picking(s)',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'stock.picking',
            'domain': [('product_request_id', '=', self.id)],
            'context': {'default_product_request_id': self.id},
        }

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and any(
                [not line.cancelled and line.product_qty for line in rec.line_ids]
            )

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseProductRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        if not vals.get('name') == _('New'):
            vals['name'] = self.env["ir.sequence"].next_by_code("product.request") or _('/')
        request = super(PurchaseProductRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseProductRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_done(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'ongoing'
            elif rec.state == 'ongoing':
                val = {
                    'res_id': rec.id,
                    'res_model_id': self.env['ir.model']._get_id('purchase.product.request'),
                    'activity_type_id': 4,
                    'date_deadline': fields.Date.today(),
                    'automated': True,
                    'summary': f"demande de Besoin {rec.name} Approuvé",
                    'note': f"Cher {rec.create_uid.name} : Votre demande de Besoin a été Approuvé, vous pouvez continuer la procedure en cliquant sur cree une demande de prix !",
                    'user_id': rec.create_uid.id
                }
                self.env['mail.activity'].with_context(mail_activity_quick_update=True).create(val)
                return self.write({"state": "done"})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})
