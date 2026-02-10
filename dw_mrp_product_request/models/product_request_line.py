from odoo.exceptions import UserError, ValidationError

from odoo import _, api, fields, models


class PurchaseProductRequestLine(models.Model):
    _name = "product.request.line"
    _description = "Product Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.constrains('name', 'product_id')
    def _check_name_product(self):
        if any(
                not record.name and not record.product_id for record in self):
            raise ValidationError(
                _('You Have to specify what your request is about.')
            )

    name = fields.Char(string="Description", )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Product Unit of Measure",
        # track_visibility="onchange",
    )
    product_qty = fields.Float(
        string="Quantity", digits="Product Unit of Measure"
    )
    product_production_qty = fields.Float(
        string="Production Quantity"
    )
    request_id = fields.Many2one(
        comodel_name="product.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Assigned to",
        store=True,
    )
    date_start = fields.Date(related="request_id.date_start", store=True)
    description = fields.Text(
        # related="request_id.description",
        string="PR Description",
        store=True,
        readonly=False,
    )
    date_required = fields.Date(
        string="Request Date",
        required=True,
        # track_visibility="onchange",
        default=fields.Date.context_today,
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    justification = fields.Text(string="Justification")
    request_state = fields.Selection(
        related="request_id.state",
        store=True,
    )
    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False
    )

    estimated_cost = fields.Monetary(
        string="Estimated Cost",
        currency_field="currency_id",
        default=0.0,
        help="Estimated cost of Purchase Request Line, not propagated to PO.",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)

    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)])

    @api.depends(
        "name",
        "product_uom_id",
        "product_qty",
        "date_required",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        # for rec in self.filtered(lambda p: p.purchase_lines):
        #     rec.is_editable = False

    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def write(self, vals):
        res = super(PurchaseProductRequestLine, self).write(vals)
        if vals.get("cancelled"):
            requests = self.mapped("request_id")
            requests.check_auto_reject()
        return res

    def _can_be_deleted(self):
        self.ensure_one()
        return self.request_state == "draft"

    def unlink(self):
        for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "You can only delete a request line "
                        "if the purchase request is in draft state."
                    )
                )
        return super(PurchaseProductRequestLine, self).unlink()
