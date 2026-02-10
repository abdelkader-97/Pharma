# -*- coding: utf-8 -*-
{
    'name': 'Quality Control - PHARMA',
    'version': '1.0.0',
    'category': 'Manufacturing/Quality',
    'description': """
=        """,
    'author': 'DIGIWAVES - ALGERIA',
    'website': 'www.digiwaves.io',
    'depends': [
        'dw_quality', 'product_expiry', 'purchase_stock', 'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sample_sequence.xml',
        'data/sampling_sequence.xml',
        'data/dw_analyse_norm_data.xml',
        'data/dw_methodes_data.xml',
        'views/quality_check_model_views.xml',
        'views/product_views.xml',
        'views/quality_check_views.xml',
        'views/stock_location.xml',
        'views/stock_warehouse.xml',
        'views/sample_request_view.xml',
        'views/res_config_settings_inherit_views.xml',
        'views/dw_quality_sampling_views.xml',
        'views/dw_analyse_methode_views.xml',
        'views/dw_analyse_norm_views.xml',
        'views/dw_analyse_test_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
