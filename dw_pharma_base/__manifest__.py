# -*- coding: utf-8 -*-
{
    'name': 'Solution Pharma BASE',
    'version': '18.0.1.1.0',
    'author': 'DIDIWAVES - ALGERIA',
    'website': 'www.digiwaves.io',
    'depends': ['dw_base', 'stock','product_expiry', 'stock_sms'],
    'images': ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/product.xml',
        'views/partner.xml',
        'views/product_pharmaceutical.xml',
        'views/res_config_settings_inherit_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
