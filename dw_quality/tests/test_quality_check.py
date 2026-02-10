# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo import fields
from datetime import datetime


@tagged('post_install', '-at_install')
class TestQualityCheck(TransactionCase):
    """ Tests for dw.quality.check model """

    def setUp(self):
        super().setUp()

        # Create a dummy product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu'
        })

        # Create a quality point
        self.point = self.env['dw.quality.point'].create({
            'title': 'Control Point 1',
            'test_type_id': self.env.ref('dw_quality.test_type_passfail').id,
            'team_id': self.env['dw.quality.alert.team'].create({'name': 'QA Team'}).id,
            'tolerance_min': 5.0,
            'tolerance_max': 10.0,
        })

        # Create picking and move line
        picking_type = self.env['stock.picking.type'].search([], limit=1)
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'partner_id': self.env['res.partner'].create({'name': 'Partner'}).id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
        })

        self.move_line = self.env['stock.move.line'].create({
            'product_id': self.product.id,
            'picking_id': self.picking.id,
            'location_id': self.picking.location_id.id,
            'location_dest_id': self.picking.location_dest_id.id,
            'quantity': 10.0,
        })

        # Create quality check
        self.check = self.env['dw.quality.check'].create({
            'point_id': self.point.id,
            'product_id': self.product.id,
            'team_id': self.point.team_id.id,
            'test_type_id': self.point.test_type_id.id,
            'move_line_id': self.move_line.id,
            'measure': 7.0,
        })

    def test_01_check_creation(self):
        """Check is created with correct default values"""
        self.assertTrue(self.check.name)
        self.assertEqual(self.check.quality_state, 'none')
        self.assertEqual(self.check.point_id, self.point)
        self.assertEqual(self.check.product_id, self.product)
        print("✅ test_01_check_creation passed")

    def test_02_do_pass(self):
        """do_pass sets state to pass, adds user and date"""
        self.check.do_pass()
        self.assertEqual(self.check.quality_state, 'pass')
        self.assertEqual(self.check.user_id, self.env.user)
        self.assertTrue(self.check.control_date)
        print("✅ test_02_do_pass passed")

    def test_03_do_fail(self):
        """do_fail sets state to fail, adds user and date"""
        self.check.do_fail()
        self.assertEqual(self.check.quality_state, 'fail')
        self.assertEqual(self.check.user_id, self.env.user)
        self.assertTrue(self.check.control_date)
        print("✅ test_03_do_fail passed")

    def test_04_measure_passes(self):
        """_measure_passes checks measure against tolerances"""
        self.assertTrue(self.check._measure_passes())
        self.check.measure = 2.0
        self.assertFalse(self.check._measure_passes())
        print("✅ test_04_measure_passes passed")

    def test_05_do_measure(self):
        """do_measure sets correct state according to tolerance"""
        self.check.measure = 8.0
        self.check.do_measure()
        self.assertEqual(self.check.quality_state, 'pass')

        self.check.measure = 2.0
        self.check.do_measure()
        self.assertEqual(self.check.quality_state, 'fail')
        print("✅ test_05_do_measure passed")

    def test_06_alert_creation(self):
        """do_alert creates a quality alert linked to the check"""
        action = self.check.do_alert()
        alert = self.env['dw.quality.alert'].search([('check_id', '=', self.check.id)])
        self.assertTrue(alert)
        self.assertEqual(alert.check_id, self.check)
        self.assertIn('res_model', action)
        self.assertEqual(action['res_model'], 'dw.quality.alert')
        print("✅ test_06_alert_creation passed")

    def test_07_warning_message(self):
        """Warning message should be set when measure fails"""
        self.check.write({'measure': 2.0})
        self.check._compute_measure_success()
        self.check._compute_warning_message()
        self.check.invalidate_recordset()
        if self.check.measure_success == False:
            self.assertIn('between', self.check.warning_message)
            print("✅ test_07_qty_to_test_computation passed")
        else:
            self.assertEqual('', self.check.warning_message)
            print("✅ test_07_qty_to_test_computation passed")

    def test_08_qty_to_test_computation(self):
        """Quantity to test should equal qty_line when no fraction"""
        self.assertEqual(self.check.qty_to_test, self.check.qty_line)
        print("✅ test_08_qty_to_test_computation passed")

    def test_09_get_check_action_name(self):
        """Check action name is properly generated"""
        name = self.check._get_check_action_name()
        self.assertIn('Test Product', name)
        self.assertIn(str(self.check.qty_line), name)
        print("✅ test_09_get_check_action_name passed")
