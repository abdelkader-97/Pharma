# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo import fields


@tagged('-at_install', 'post_install')
class TestQualityOnLot(TransactionCase):
    """Tests for the inherited stock.lot model with quality features"""

    def setUp(self):
        super().setUp()
        self.company = self.env.company

        # Create a product (lot tracked)
        self.product = self.env['product.product'].create({
            'name': 'Lot Product',
            'type': 'consu',
            'tracking': 'lot',
        })

        # Create a lot for this product
        self.lot = self.env['stock.lot'].create({
            'name': 'LOT-001',
            'product_id': self.product.id,
            'company_id': self.company.id,
        })

        # Create a quality team (required for checks)
        self.team = self.env['dw.quality.alert.team'].create({
            'name': 'QA Team',
            'company_id': self.company.id,
            'sequence': 1,
        })

        # Quality check test type
        self.test_type_id = self.env.ref('dw_quality.test_type_passfail').id

        # Create some quality checks related to this lot
        self.check_pass = self.env['dw.quality.check'].create({
            'name': 'Check Pass',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'lot_id': self.lot.id,
            'quality_state': 'pass',
            'test_type_id': self.test_type_id,
        })
        self.check_fail = self.env['dw.quality.check'].create({
            'name': 'Check Fail',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'lot_id': self.lot.id,
            'quality_state': 'fail',
            'test_type_id': self.test_type_id,
        })

        # Create some quality alerts related to this lot
        self.alert_open = self.env['dw.quality.alert'].create({
            'name': 'Alert 1',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'lot_id': self.lot.id,
        })
        self.alert_open2 = self.env['dw.quality.alert'].create({
            'name': 'Alert 2',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'lot_id': self.lot.id,
        })

    # -------------------------------------------------------------------------
    # Tests on computed fields
    # -------------------------------------------------------------------------

    def test_01_compute_quality_check_qty(self):
        """_compute_quality_check_qty should return correct count"""
        self.lot._compute_quality_check_qty()
        self.assertEqual(self.lot.quality_check_qty, 2)
        print("✅ test_01_compute_quality_check_qty passed")

    def test_02_compute_quality_alert_qty(self):
        """_compute_quality_alert_qty should return correct count"""
        self.lot._compute_quality_alert_qty()
        self.assertEqual(self.lot.quality_alert_qty, 2)
        print("✅ test_02_compute_quality_alert_qty passed")

    # -------------------------------------------------------------------------
    # Tests on actions
    # -------------------------------------------------------------------------

    def test_03_action_open_quality_checks(self):
        """action_open_quality_checks should return correct domain with lot_id"""
        action = self.lot.action_open_quality_checks()
        self.assertIsInstance(action, dict)
        self.assertIn('domain', action)
        # Check lot_id is in domain
        domain_flat = str(action['domain'])
        self.assertIn(str(self.lot.id), domain_flat)
        print("✅ test_03_action_open_quality_checks passed")

    def test_04_action_lot_open_quality_alerts(self):
        """action_lot_open_quality_alerts should set correct domain and context"""
        action = self.lot.action_lot_open_quality_alerts()
        self.assertIsInstance(action, dict)
        self.assertIn('domain', action)
        self.assertIn('context', action)
        # Check domain
        self.assertIn(('lot_id', '=', self.lot.id), action['domain'])
        # Check context values
        ctx = action['context']
        self.assertEqual(ctx['default_lot_id'], self.lot.id)
        self.assertEqual(ctx['default_product_id'], self.product.id)
        self.assertEqual(ctx['default_company_id'], self.company.id)
        print("✅ test_04_action_lot_open_quality_alerts passed")

    # -------------------------------------------------------------------------
    # Edge Cases
    # -------------------------------------------------------------------------

    def test_05_no_quality_records_should_return_zero(self):
        """Lot with no quality records should return 0 counts"""
        new_lot = self.env['stock.lot'].create({
            'name': 'LOT-002',
            'product_id': self.product.id,
            'company_id': self.company.id,
        })
        new_lot._compute_quality_check_qty()
        new_lot._compute_quality_alert_qty()
        self.assertEqual(new_lot.quality_check_qty, 0)
        self.assertEqual(new_lot.quality_alert_qty, 0)
        print("✅ test_05_no_quality_records_should_return_zero passed")

    def test_06_unlink_lot_should_not_break_quality(self):
        lot_id = self.lot.id
        self.lot.unlink()
        self.assertFalse(self.env['stock.lot'].browse(lot_id).exists())
        print("✅ test_06_unlink_lot_should_not_break_quality passed")
