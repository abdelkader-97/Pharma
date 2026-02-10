from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    """ def _validate_move_transfer(self, move_id):
            product = move_id.product_id
            location = move_id.location_id
            location_dest = move_id.location_dest_id

            # Validate transfer at the move_id level
            if (product and product.restrict_transfer) :
                if (location and not location.perform_transfer) or (location_dest and not location_dest.perform_transfer):
                    raise UserError(_(f"The transfer for {product.name} cannot be performed in the specified locations."))

            # Validate transfer at the move_line_id level if move lines exist
                if move_id.move_line_ids:
                    if any(
                        not move_line.location_id.perform_transfer or 
                        not move_line.location_dest_id.perform_transfer 
                        for move_line in move_id.move_line_ids
                    ):
                        raise UserError(_(f"The transfer for {product.name} cannot be performed for one or more move lines."))
    def button_validate(self):
        for picking in self:
            for move_id in picking.move_ids:
                self._validate_move_transfer(move_id)
        
        return super().button_validate() """

    

    
    



    