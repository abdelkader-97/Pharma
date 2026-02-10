# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from unittest.mock import patch
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

@tagged('post_install', '-at_install')
class TestQualityPoint(TransactionCase):
    """ Tests for dw.quality.point model """

    def setUp(self):
        super().setUp()

        # Create basic data
        self.company = self.env.company
        self.team = self.env['dw.quality.alert.team'].create({'name': 'QA Team'})
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
        })
        self.category = self.env['product.category'].create({'name': 'Cat 1'})
        self.product.categ_id = self.category

        self.picking_type = self.env['stock.picking.type'].search([], limit=1)

        # Create a quality point
        self.point = self.env['dw.quality.point'].create({
            'title': 'Control Point 1',
            'team_id': self.team.id,
            'picking_type_ids': [(6, 0, [self.picking_type.id])],
            'test_type_id': self.env.ref('dw_quality.test_type_passfail').id,
            'tolerance_min': 5.0,
            'tolerance_max': 10.0,
            'testing_percentage_within_lot': 100,
        })

    def test_01_creation_and_defaults(self):
        """Quality Point is created with correct defaults"""
        self.assertTrue(self.point.name)
        self.assertEqual(self.point.team_id, self.team)
        self.assertEqual(self.point.company_id, self.company)
        self.assertEqual(self.point.measure_frequency_type, 'all')
        print("✅ test_01_creation_and_defaults passed")

    def test_02_display_name(self):
        """Display name should include title"""
        self.point.title = "My Title"
        self.point._compute_display_name()
        self.assertIn("QCP", self.point.display_name)
        print("✅ test_02_display_name passed")

    def test_03_onchange_norm_sets_tolerance(self):
        """Tolerance max is set on norm onchange"""
        p = self.env['dw.quality.point'].new({
            'norm': 12.0,
            'tolerance_max': 0.0,
        })
        p.onchange_norm()
        self.assertEqual(p.tolerance_max, 12.0)
        print("✅ test_03_onchange_norm_sets_tolerance passed")

    def test_04_fractional_lot(self):
        """Lot is fractional when testing percentage < 100"""
        self.point.testing_percentage_within_lot = 50
        self.point._compute_is_lot_tested_fractionally()
        self.assertTrue(self.point.is_lot_tested_fractionally)
        print("✅ test_04_fractional_lot passed")

    def test_05_standard_deviation_and_average(self):
        """Standard deviation and average are computed correctly"""
        self.point.test_type_id = self.env['dw.quality.point.test_type'].create({
            'name': 'Measure',
            'technical_name': 'measure'
        })

        # create some checks
        self.env['dw.quality.check'].create({
            'point_id': self.point.id,
            'product_id': self.product.id,
            'team_id': self.team.id,
            'test_type_id': self.point.test_type_id.id,
            'measure': 10,
            'quality_state': 'pass',
        })
        self.env['dw.quality.check'].create({
            'point_id': self.point.id,
            'product_id': self.product.id,
            'team_id': self.team.id,
            'test_type_id': self.point.test_type_id.id,
            'measure': 20,
            'quality_state': 'pass',
        })
        self.point._compute_standard_deviation_and_average()
        self.assertAlmostEqual(self.point.average, 15.0, places=1)
        self.assertGreater(self.point.standard_deviation, 0)
        print("✅ test_05_standard_deviation_and_average passed")

    def test_06_check_execute_now_all(self):
        """check_execute_now always returns True for type=all"""
        self.point.measure_frequency_type = 'all'
        self.assertTrue(self.point.check_execute_now())
        print("✅ test_06_check_execute_now_all passed")

    def test_07_check_execute_now_random(self):
        """check_execute_now respects random chance"""
        self.point.measure_frequency_type = 'random'
        self.point.measure_frequency_value = 100
        with patch('random.random', return_value=0.0):
            self.assertTrue(self.point.check_execute_now())
        with patch('random.random', return_value=1.0):
            self.assertFalse(self.point.check_execute_now())

        print("✅ test_07_check_execute_now_random passed")

    def test_08_check_execute_now_periodical(self):
        """check_execute_now periodical respects previous checks"""
        self.point.measure_frequency_type = 'periodical'
        self.point.measure_frequency_unit = 'day'
        self.point.measure_frequency_unit_value = 2

        # First call -> no checks yet
        self.assertTrue(self.point.check_execute_now())

        # Create a check today
        self.env['dw.quality.check'].create({
            'point_id': self.point.id,
            'product_id': self.product.id,
            'team_id': self.team.id,
            'test_type_id': self.point.test_type_id.id,
            'measure': 7,
            'create_date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        })
        # Second call -> should return False
        self.assertFalse(self.point.check_execute_now())
        print("✅ test_08_check_execute_now_periodical passed")

    def test_09_get_domain(self):
        """_get_domain builds correct domain"""
        domain = self.env['dw.quality.point']._get_domain(
            self.product,
            self.picking_type,
            measure_on='product'
        )
        self.assertIn(('measure_on', '=', 'product'), domain)
        print("✅ test_09_get_domain passed")

    def test_10_get_checks_values(self):
        """_get_checks_values generates values for missing checks"""
        vals = self.point._get_checks_values(self.product, self.company.id)
        self.assertTrue(vals)
        self.assertEqual(vals[0]['product_id'], self.product.id)
        self.assertEqual(vals[0]['point_id'], self.point.id)
        print("✅ test_10_get_checks_values passed")

    def test_11_action_see_quality_checks(self):
        """Smart button returns correct action"""
        action = self.point.action_see_quality_checks()
        self.assertEqual(action['res_model'], 'dw.quality.check')
        self.assertIn(('point_id', '=', self.point.id), action['domain'])
        print("✅ test_11_action_see_quality_checks passed")


