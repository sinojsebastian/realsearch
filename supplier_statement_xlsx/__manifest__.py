# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Supplier Statement Xlsx',
    'author': "Zesty Beanz Technologies Pvt LTD",
    'website': "http://www.zbeanztech.com",
    'summary': 'Supplier Statement Xlsx Module',
    'description': """
        Supplier Statement Module

    """,
    'version': '13.0.1.0',
    'depends': ['base','report_xlsx'],
    'data' : [
              
        'wizard/supplier_statement_wizard_view.xml',
        'views/report_view.xml',
        
     ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
