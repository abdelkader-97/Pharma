{
    'name': 'MRP - Stock',
    'description': """
        =
        """,
    'author': 'DIGIWAVES ALGERIA',
    'website': 'https://digiwaves.io/',
    'category': 'Localization',
    'version': '1.0.0',
    'depends': [
        'dw_mrp_base', 'dw_mrp_product_request'
    ],
    'data': [
        'views/stock_warehouse_views.xml',
        'views/stock_picking_type.xml',
        'views/stock_lot.xml',
        'views/mrp_production.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
