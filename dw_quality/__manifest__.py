
{
    'name': 'Quality Refactored',
    'version': '18.0.1.0.0',
    'category': 'Quality',
    'sequence': 50,
    'summary': 'Basic Feature for Quality',
    'depends': ['stock'],
    'description': """
Quality Base
===============
* Define quality points that will generate quality checks on pickings,
  manufacturing orders or work orders (quality_mrp)
* Quality alerts can be created independently or related to quality checks
* Possibility to add a measure to the quality check with a min/max tolerance
* Define your stages for the quality alerts
""",
    'data': [
        'security/ir.model.access.csv',
        'data/quality_data.xml',
        'data/quality_control_data.xml',

        'views/quality_point_views.xml',
        'views/quality_alert_views.xml',
        'views/stock_lot_views.xml',
        'views/quality_check_views.xml',
        'views/quality_alert_team_view.xml',
        'views/quality_alert_stage_views.xml',
        'views/quality_tag_views.xml',
        'views/product_views.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'wizard/on_demand_quality_check_wizard_views.xml',
        'wizard/quality_check_wizard_views.xml',
        'menus.xml',

    ],
    'license': 'OEEL-1',

}
