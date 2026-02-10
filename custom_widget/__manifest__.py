# -*- encoding: utf-8 -*-
{
    'name': 'Custom Widgets',
    "version": "18.0.1.1.0",
    'author': 'DIGIWAVES - ALGERIA',
    'website': 'www.digiwaves.io',
    'sequence': 30,
    'category': 'Tools',
    'depends': ['web', 'shared_assets'],
    'assets': {
        'web.assets_backend': [
            'custom_widget/static/src/components/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
