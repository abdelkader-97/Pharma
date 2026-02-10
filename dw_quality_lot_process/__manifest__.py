# -*- coding: utf-8 -*-
{
    'name': 'Quality Lot Process',
    'version': '1.0.0',
    'category': 'Quality',
    'description': """
=        """,
    'author': 'DIGIWAVES - ALGERIA',
    'website': 'www.digiwaves.io',
    'depends': [
        'dw_quality_control', 'dw_location_transfer_limit'
    ],
    'data': [
        # data
        "data/lot_status_data.xml",
        # security
        'security/security.xml',
        'security/ir.model.access.csv',

        # report
        # view
        'views/stock_lot_views.xml',
        'views/product_product_views.xml',
        'views/quality_check_views.xml',
        'views/stock_location_inherit.xml',
        'views/stock_warehouse_views.xml',
        # wizards
        'wizard/stock_lot_pass_sub_lot.xml',
        'wizard/stock_lot_cancel_reason_views.xml',
        'wizard/stock_lot_reanalyse_status_views.xml',
        # menu
        'menus.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
