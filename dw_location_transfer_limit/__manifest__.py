# -*- coding: utf-8 -*-
{
    'name': 'Location Transfer Limit',
    'version': '1.0.0',
    'category': 'Inventory',
    'description': """ Location Transfer Limit """,
    'author': 'DIGIWAVES - ALGERIA',
    'website': 'www.digiwaves.io',
    'depends': [
       'stock'
    ],
    'data': [
        #security
        'security/security.xml',
        'security/ir.model.access.csv',
        #view
        'views/stock_storage_category.xml',
        'views/product_product_views.xml',
        'views/stock_location_inherit.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
