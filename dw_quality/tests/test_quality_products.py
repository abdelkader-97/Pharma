# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('-at_install', 'post_install')
class TestQualityOnProduct(TransactionCase):
    """Tests for ProductTemplate and ProductProduct quality integration"""

    def setUp(self):
        super().setUp()
        self.company = self.env.company

        # Create product template and product variant
        self.product_tmpl = self.env['product.template'].create({
            'name': 'Test Product Template',
            'type': 'consu',
        })
        self.product = self.product_tmpl.product_variant_id

        # Create quality team
        self.team = self.env['dw.quality.alert.team'].create({
            'name': 'QA Team',
            'company_id': self.company.id,
            'sequence': 1,
        })

        # Create picking type (required for quality point)
        picking_type = self.env['stock.picking.type'].search([], limit=1)
        if not picking_type:
            picking_type = self.env['stock.picking.type'].create({
                'name': 'Test Picking Type',
                'code': 'incoming',
                'warehouse_id': self.env['stock.warehouse'].search([], limit=1).id,
            })

        # Create quality point for the product
        self.quality_point = self.env['dw.quality.point'].create({
            'title': 'Point 1',
            'team_id': self.team.id,
            'picking_type_ids': [(6, 0, [picking_type.id])],
            'product_ids': [(6, 0, [self.product.id])],
            'test_type_id': self.env.ref('dw_quality.test_type_passfail').id,
        })

        # Create two quality checks (one pass, one fail)
        self.check_pass = self.env['dw.quality.check'].create({
            'name': 'Check Pass',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'quality_state': 'pass',
            'test_type_id': self.env.ref('dw_quality.test_type_passfail').id,
        })
        self.check_fail = self.env['dw.quality.check'].create({
            'name': 'Check Fail',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'quality_state': 'fail',
            'test_type_id': self.env.ref('dw_quality.test_type_passfail').id,
        })

    # -------------------------------------------------------------------------
    # Tests on computed fields
    # -------------------------------------------------------------------------

    def test_01_compute_quality_counts_on_product(self):
        """quality_pass_qty and quality_fail_qty should reflect the checks on product"""
        self.product._compute_quality_check_qty()
        self.assertEqual(self.product.quality_pass_qty, 1)
        self.assertEqual(self.product.quality_fail_qty, 1)
        print("✅ test_01_compute_quality_counts_on_product passed")

    def test_02_compute_quality_counts_on_template(self):
        """quality_pass_qty and quality_fail_qty should aggregate from variants"""
        self.product_tmpl._compute_quality_check_qty()
        self.assertEqual(self.product_tmpl.quality_pass_qty, 1)
        self.assertEqual(self.product_tmpl.quality_fail_qty, 1)
        print("✅ test_02_compute_quality_counts_on_template passed")

    # -------------------------------------------------------------------------
    # Tests on actions
    # -------------------------------------------------------------------------

    def test_03_action_see_quality_control_points_template(self):
        """action_see_quality_control_points on template should return proper domain & context"""
        action = self.product_tmpl.action_see_quality_control_points()
        self.assertIn('domain', action)
        self.assertIn('context', action)
        self.assertIn(self.product.id, action['context']['default_product_ids'])
        print("✅ test_03_action_see_quality_control_points_template passed")

    def test_04_action_see_quality_control_points_product(self):
        """action_see_quality_control_points on product should return proper domain & context"""
        action = self.product.action_see_quality_control_points()
        self.assertIn('domain', action)
        self.assertIn('context', action)
        self.assertIn(self.product.id, action['context']['default_product_ids'])
        print("✅ test_04_action_see_quality_control_points_product passed")

    def test_05_action_see_quality_checks_template(self):
        """action_see_quality_checks on template should return proper domain & context"""
        action = self.product_tmpl.action_see_quality_checks()
        self.assertIn('domain', action)
        self.assertIn('context', action)
        self.assertEqual(action['context']['default_product_id'], self.product_tmpl.product_variant_id.id)
        print("✅ test_05_action_see_quality_checks_template passed")

    def test_06_action_see_quality_checks_product(self):
        """action_see_quality_checks on product should return proper domain & context"""
        action = self.product.action_see_quality_checks()
        self.assertIn('domain', action)
        self.assertIn('context', action)
        self.assertEqual(action['context']['default_product_id'], self.product.id)
        print("✅ test_06_action_see_quality_checks_product passed")

    # -------------------------------------------------------------------------
    # Cleanup / unlinking
    # -------------------------------------------------------------------------

    def test_07_delete_product_cleans_quality_checks(self):
        """Deleting product should not break quality check constraints (cascade or manual cleanup)"""
        product_id = self.product.id
        self.product.unlink()
        exists = self.env['product.product'].browse(product_id).exists()
        self.assertFalse(exists)
        print("✅ test_07_delete_product_cleans_quality_checks passed")
