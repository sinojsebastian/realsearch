# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Check Book',
    'author': "Zesty Beanz Technologies Pvt LTD",
    'website': "http://www.zbeanztech.com",
    'summary': 'Check Book Module',
    'description': """
        Check Book Module

    """,
    'version': '0.10',
    'depends': ['base','account','bh_account_vat'],
    'data' : [
            'security/ir.model.access.csv',
            'views/check_book_views.xml',
            'views/account_payment_views.xml',
     ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
