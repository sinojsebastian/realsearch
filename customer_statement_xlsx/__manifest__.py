# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Customer Statement Xlsx',
    'author': "Zesty Beanz Technologies Pvt LTD",
    'website': "http://www.zbeanztech.com",
    'summary': 'Statement Xlsx Module',
    'description': """
        Statement Module

    """,
    'version': '13.1.6',
    'depends': ['base','report_xlsx'],
    'data' : [
              
        'wizard/customer_statement_wizard_view.xml',
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
