# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Customer Statement',
    'author': "Zesty Beanz Technologies Pvt LTD",
    'website': "http://www.zbeanztech.com",
    'summary': 'Customer Statement Module',
    'description': """
    	Customer Statement Module

	""",
    'version': '13.0.1.6',
    'depends': ['base'],
    'data' : [
              
        'wizard/customer_statement_wizard_view.xml',
        'report/report_customer_statement_qweb.xml',
        'report/report_layout.xml',
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
