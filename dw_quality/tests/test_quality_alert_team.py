# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError

@tagged('post_install', '-at_install')
class TestQualityAlertTeam(TransactionCase):
    """Tests for dw.quality.alert.team model"""

    def setUp(self):
        super().setUp()
        self.company = self.env.company

        # Create a team
        self.team = self.env['dw.quality.alert.team'].create({
            'name': 'QA Team',
            'company_id': self.company.id,
            'sequence': 10,
        })

        # Create a product & quality point for related checks
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu'
        })
        self.point = self.env['dw.quality.point'].create({
            'title': 'Point 1',
            'team_id': self.team.id,
            'picking_type_ids': [(6, 0, self.env['stock.picking.type'].search([], limit=1).ids)],
            'test_type_id': self.env.ref('dw_quality.test_type_passfail').id,
        })

        # Create an open stage for alerts
        self.stage = self.env['dw.quality.alert.stage'].create({
            'name': 'Open',
            'done': False
        })

    def test_01_team_creation(self):
        """A team should be created with correct default values"""
        self.assertEqual(self.team.name, 'QA Team')
        self.assertEqual(self.team.company_id, self.company)
        self.assertEqual(self.team.color, 1)
        self.assertEqual(self.team.sequence, 10)
        print("✅ test_01_team_creation passed")

    def test_02_compute_check_count(self):
        """_compute_check_count should count quality checks with state 'none'"""
        # Initially there should be 0
        self.team._compute_check_count()
        self.assertEqual(self.team.check_count, 0)

        # Create a check with quality_state='none'
        self.env['dw.quality.check'].create({
            'point_id': self.point.id,
            'product_id': self.product.id,
            'team_id': self.team.id,
            'test_type_id': self.point.test_type_id.id,
            'quality_state': 'none'
        })
        self.team._compute_check_count()
        self.assertEqual(self.team.check_count, 1)

        # Create a check with quality_state='pass' → should not be counted
        self.env['dw.quality.check'].create({
            'point_id': self.point.id,
            'product_id': self.product.id,
            'team_id': self.team.id,
            'test_type_id': self.point.test_type_id.id,
            'quality_state': 'pass'
        })
        self.team._compute_check_count()
        self.assertEqual(self.team.check_count, 1, "Only 'none' checks should be counted")
        print("✅ test_02_compute_check_count passed")

    def test_03_compute_alert_count(self):
        """_compute_alert_count should count alerts in non-done stages"""
        self.team._compute_alert_count()
        self.assertEqual(self.team.alert_count, 0)

        # Create an open alert
        self.env['dw.quality.alert'].create({
            'name': 'Test Alert',
            'team_id': self.team.id,
            'stage_id': self.stage.id,
        })
        self.team._compute_alert_count()
        self.assertEqual(self.team.alert_count, 1)

        # Create an alert in a done stage → should not be counted
        done_stage = self.env['dw.quality.alert.stage'].create({'name': 'Done', 'done': True})
        self.env['dw.quality.alert'].create({
            'name': 'Closed Alert',
            'team_id': self.team.id,
            'stage_id': done_stage.id,
        })
        self.team._compute_alert_count()
        self.assertEqual(self.team.alert_count, 1)
        print("✅ test_03_compute_alert_count passed")

    def test_04_get_quality_team_found(self):
        """_get_quality_team should return the team ID when found"""
        domain = [('company_id', '=', self.company.id)]
        team_id = self.env['dw.quality.alert.team']._get_quality_team(domain)
        self.assertEqual(team_id, self.team.id)
        print("✅ test_04_get_quality_team_found passed")

    def test_05_get_quality_team_not_found(self):
        """_get_quality_team should raise error when no team exists"""
        # Remove team
        self.point.unlink()
        self.team.unlink()
        domain = [('company_id', '=', self.company.id)]
        with self.assertRaises(UserError):
            self.env['dw.quality.alert.team']._get_quality_team(domain)
        print("✅ test_05_get_quality_team_not_found passed")

    def test_06_ordering(self):
        """Ordering should be based on sequence then ID"""
        team2 = self.env['dw.quality.alert.team'].create({
            'name': 'QA Team 2',
            'company_id': self.company.id,
            'sequence': 5,
        })
        records = self.env['dw.quality.alert.team'].search([], order='sequence, id')
        self.assertEqual(records[0], team2)
        self.assertEqual(records[1], self.team)
        print("✅ test_06_ordering passed")
