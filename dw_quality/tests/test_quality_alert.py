# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo import fields
from unittest.mock import patch

class TestQualityAlert(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company = self.env.company

        # Create team
        self.team = self.env['dw.quality.alert.team'].create({
            'name': 'QA Team',
            'company_id': self.company.id,
            'sequence': 1,
        })

        # Create stage
        self.stage_open = self.env['dw.quality.alert.stage'].create({
            'name': 'Open',
            'done': False,
            'team_ids': [(6, 0, [self.team.id])]
        })
        self.stage_done = self.env['dw.quality.alert.stage'].create({
            'name': 'Done',
            'done': True,
            'team_ids': [(6, 0, [self.team.id])]
        })

        # Create product and variant
        self.product_tmpl = self.env['product.template'].create({
            'name': 'Product Template Test',
            'type': 'consu',
        })
        self.product = self.env['product.product'].create({
            'name': 'Product Variant Test',
            'product_tmpl_id': self.product_tmpl.id
        })

        # Create picking type and lot for relations
        self.picking = self.env['stock.picking'].create({
            'partner_id': self.env.ref('base.partner_admin').id,
            'picking_type_id': self.env['stock.picking.type'].search([], limit=1).id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
        })
        self.lot = self.env['stock.lot'].create({
            'name': 'LOT-001',
            'product_id': self.product.id,
            'company_id': self.company.id,
        })

        # Create quality check
        self.check = self.env['dw.quality.check'].create({
            'name': 'Check Test',
            'team_id': self.team.id,
            'product_id': self.product.id,
            'test_type_id': self.env.ref('dw_quality.test_type_passfail').id,
        })

    def test_01_create_quality_alert(self):
        """Should create quality alert with defaults and sequence name"""
        alert = self.env['dw.quality.alert'].create({
            'team_id': self.team.id,
            'stage_id': self.stage_open.id,
            'product_tmpl_id': self.product_tmpl.id,
            'product_id': self.product.id,
            'picking_id': self.picking.id,
            'lot_id': self.lot.id,
            'check_id': self.check.id,
            'title': 'Test Alert',
        })
        self.assertTrue(alert.name.startswith('QA') or alert.name != 'New')
        self.assertEqual(alert.team_id, self.team)
        self.assertEqual(alert.stage_id, self.stage_open)
        self.assertEqual(alert.product_tmpl_id, self.product_tmpl)
        self.assertEqual(alert.product_id, self.product)
        self.assertEqual(alert.check_id, self.check)
        self.assertEqual(alert.company_id, self.team.company_id)
        self.assertEqual(alert.display_name, f"{alert.name} - Test Alert")
        print("✅ test_01_create_quality_alert passed")

    def test_02_onchange_product_tmpl_id(self):
        """Onchange should set product_id to the first variant"""
        alert = self.env['dw.quality.alert'].new({
            'team_id': self.team.id,
            'product_tmpl_id': self.product_tmpl.id
        })
        alert.onchange_product_tmpl_id()
        self.assertEqual(alert.product_id, self.product)
        print("✅ test_02_onchange_product_tmpl_id passed")

    def test_03_onchange_team_id_sets_company(self):
        """Onchange team should set company_id"""
        alert = self.env['dw.quality.alert'].new({})
        alert.team_id = self.team
        alert.onchange_team_id()
        self.assertEqual(alert.company_id, self.company)
        print("✅ test_03_onchange_team_id_sets_company passed")

    def test_04_write_stage_done_sets_date_close(self):
        """Changing stage to a done stage should set date_close"""
        alert = self.env['dw.quality.alert'].create({
            'team_id': self.team.id,
            'stage_id': self.stage_open.id,
        })
        self.assertFalse(alert.date_close)
        alert.write({'stage_id': self.stage_done.id})
        self.assertTrue(alert.date_close)
        print("✅ test_04_write_stage_done_sets_date_close passed")

    def test_05_group_expand_stage(self):
        """_read_group_stage_ids should return stages for the team"""
        domain = [('team_id', '=', self.team.id)]
        stages = self.env['dw.quality.alert.stage'].search([])
        expanded = self.env['dw.quality.alert']._read_group_stage_ids(stages, domain)
        self.assertIn(self.stage_open, expanded)
        self.assertIn(self.stage_done, expanded)
        print("✅ test_05_group_expand_stage passed")

    def test_06_action_see_check(self):
        """action_see_check should return a proper action dict"""
        alert = self.env['dw.quality.alert'].create({
            'team_id': self.team.id,
            'stage_id': self.stage_open.id,
            'check_id': self.check.id,
        })
        action = alert.action_see_check()
        self.assertEqual(action['res_id'], self.check.id)
        self.assertEqual(action['res_model'], 'dw.quality.check')
        print("✅ test_06_action_see_check passed")

    def test_07_name_create(self):
        """name_create should create a new alert and return id + display_name"""
        new_id, display_name = self.env['dw.quality.alert'].name_create("Quick Alert")
        alert = self.env['dw.quality.alert'].browse(new_id)
        self.assertTrue(alert.exists())
        self.assertIn("Quick Alert", display_name)
        print("✅ test_07_name_create passed")

    def test_08_delete_alert(self):
        """Deleting an alert should work without foreign key issues"""
        alert = self.env['dw.quality.alert'].create({
            'team_id': self.team.id,
            'stage_id': self.stage_open.id,
        })
        alert_id = alert.id
        alert.unlink()
        self.assertFalse(self.env['dw.quality.alert'].browse(alert_id).exists())
        print("✅ test_08_delete_alert passed")
