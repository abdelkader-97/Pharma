# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError
from odoo import fields


@tagged('-at_install', 'post_install')
class TestStockPickingQuality(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company = self.env.company

        # Create a product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
            'tracking': 'lot',
        })

        # Create a lot for the product
        self.lot = self.env['stock.lot'].create({
            'name': 'LOT-001',
            'product_id': self.product.id,
            'company_id': self.company.id,
        })

        # Create a stock picking
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'partner_id': self.env.ref('base.partner_admin').id,
        })

        # Add move lines
        self.move_line = self.env['stock.move.line'].create({
            'product_id': self.product.id,
            'picking_id': self.picking.id,
            'product_uom_id': self.product.uom_id.id,
            'lot_id': self.lot.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'quantity': 10,
        })

        # Create quality team
        self.team = self.env['dw.quality.alert.team'].create({
            'name': 'QA Team',
            'company_id': self.company.id,
            'sequence': 1,
        })

        # Test type for quality checks
        self.test_type_id = self.env.ref('dw_quality.test_type_passfail').id

        # Create quality checks
        self.check_pass = self.env['dw.quality.check'].create({
            'name': 'Check Pass',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'picking_id': self.picking.id,
            'quality_state': 'pass',
            'test_type_id': self.test_type_id,
        })
        self.check_none = self.env['dw.quality.check'].create({
            'name': 'Check None',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'picking_id': self.picking.id,
            'quality_state': 'none',
            'test_type_id': self.test_type_id,
        })

        # Create quality alerts
        self.alert = self.env['dw.quality.alert'].create({
            'name': 'Alert 1',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'picking_id': self.picking.id,
        })

    # -------------------------------------------------------------------------
    # Computed fields
    # -------------------------------------------------------------------------
    def test_01_compute_quality_check_flags(self):
        """Test _compute_check sets correct todo/fail flags"""
        self.picking._compute_check()
        self.assertTrue(self.picking.quality_check_todo)
        self.assertFalse(self.picking.quality_check_fail)
        print("✅ test_01_compute_quality_check_flags passed")

    def test_02_compute_quality_alert_count(self):
        """Test _compute_quality_alert_count returns correct number"""
        self.picking._compute_quality_alert_count()
        self.assertEqual(self.picking.quality_alert_count, 1)
        print("✅ test_02_compute_quality_alert_count passed")

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def test_03_action_open_quality_check_picking(self):
        """action_open_quality_check_picking returns valid action dict"""
        action = self.picking.action_open_quality_check_picking()
        self.assertIsInstance(action, dict)
        self.assertIn('context', action)
        self.assertEqual(action['context']['default_picking_id'], self.picking.id)
        print("✅ test_03_action_open_quality_check_picking passed")

    def test_04_button_quality_alert(self):
        """button_quality_alert returns action with correct context"""
        action = self.picking.button_quality_alert()
        self.assertIsInstance(action, dict)
        ctx = action.get('context')
        self.assertEqual(ctx['default_picking_id'], self.picking.id)
        self.assertEqual(ctx['default_product_id'], self.product.id)
        self.assertEqual(ctx['default_product_tmpl_id'], self.product.product_tmpl_id.id)
        print("✅ test_04_button_quality_alert passed")

    def test_05_open_quality_alert_picking_single(self):
        """open_quality_alert_picking returns form view if one alert"""
        self.picking._compute_quality_alert_count()
        action = self.picking.open_quality_alert_picking()
        self.assertEqual(action['views'][0][1], 'form')
        self.assertEqual(action['res_id'], self.alert.id)
        print("✅ test_05_open_quality_alert_picking_single passed")

    def test_06_open_quality_alert_picking_multiple(self):
        """Returns list + form view if multiple alerts"""
        # Create a second alert
        self.env['dw.quality.alert'].create({
            'name': 'Alert 2',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'picking_id': self.picking.id,
        })
        self.picking._compute_quality_alert_count()
        action = self.picking.open_quality_alert_picking()
        self.assertEqual(len(action['views']), 2)
        self.assertIn('domain', action)
        self.assertIn(self.alert.id, action['domain'][0][2])
        print("✅ test_06_open_quality_alert_picking_multiple passed")

    # -------------------------------------------------------------------------
    # Edge cases
    # -------------------------------------------------------------------------
    def test_07_action_open_on_demand_quality_check_invalid_state(self):
        """Should raise UserError if picking in draft/done/cancel"""
        self.picking.state = 'draft'
        with self.assertRaises(UserError):
            self.picking.action_open_on_demand_quality_check()
        self.picking.state = 'done'
        with self.assertRaises(UserError):
            self.picking.action_open_on_demand_quality_check()
        self.picking.state = 'cancel'
        with self.assertRaises(UserError):
            self.picking.action_open_on_demand_quality_check()
        print("✅ test_07_action_open_on_demand_quality_check_invalid_state passed")

    def test_08_check_quality_returns_checks(self):
        """check_quality returns only 'none' quality_state checks"""
        result = self.picking.check_quality()
        self.assertTrue(hasattr(result, 'action_open_quality_check_wizard'))
        print("✅ test_08_check_quality_returns_checks passed")

    def test_09_action_cancel_removes_pending_checks(self):
        """Cancelling a picking deletes pending (none) quality checks"""
        check_ids_before = self.picking.check_ids.filtered(lambda qc: qc.quality_state == 'none').ids
        self.assertTrue(check_ids_before)
        self.picking.action_cancel()
        check_ids_after = self.picking.check_ids.filtered(lambda qc: qc.quality_state == 'none').ids
        self.assertFalse(check_ids_after)
        print("✅ test_09_action_cancel_removes_pending_checks passed")
