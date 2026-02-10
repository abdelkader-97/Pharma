{
    'name': 'MRP - Product Request',
    'description': """
        =
        """,
    'author': 'DIGIWAVES ALGERIA',
    'website': 'https://digiwaves.io/',
    'category': 'Localization',
    'version': '1.0.0',
    'depends': [
        'dw_mrp_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_request_view.xml',
        'views/mrp_production_views.xml',

        'wizard/dw_additional_consumption_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
