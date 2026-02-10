# -*- coding: utf-8 -*-
{
    'name': 'Shared Assets',
    'version': '1.0',
    'category': 'Tools',
    'author': 'DIGIWAVES - ALGERIA',
    'website': 'www.digiwaves.io',
    'depends': [
        'web'
    ],

    'assets': {
        'web.assets_backend': [
            'shared_assets/static/libs/js/jquery.min.js',
            'shared_assets/static/libs/js/bootstrap.bundle.min.js',
            'shared_assets/static/libs/js/popper.min.js',
            'shared_assets/static/libs/js/bootstrap.min.js',
            'shared_assets/static/libs/js/bootstrap-datepicker.js',
            'shared_assets/static/libs/js/d3-collection.min.js',
            'shared_assets/static/libs/js/tabulator.6.2.min.js',
            # 'shared_assets/static/libs/js/jsuites.js',
            # 'shared_assets/static/libs/js/tabulator.min.js',
            'shared_assets/static/libs/js/select2.min.js',
            'shared_assets/static/libs/js/moment.min.js',
            'shared_assets/static/libs/js/daterangepicker.min.js',
            
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
