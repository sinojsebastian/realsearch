# -*- coding: utf-8 -*-


{
    'name': 'PDC Name On cheque',
    'version': '1.5',
    'category': 'Accounting',
    'description': """
    This module is for adding a new field Name On Cheque for odoo 11
    """,
    'author': 'Zesty Beanz Technologies Pvt Ltd',
    'website': 'http://www.zbeanztech.com',
    'depends': ['zb_pdc_management'],
    'data': [
          'views/payment_view.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

