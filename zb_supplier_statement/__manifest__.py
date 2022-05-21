# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Supplier Statement',
    'author': "Zesty Beanz Technologies Pvt LTD",
    'website': "http://www.zbeanztech.com",
    'summary': 'Supplier Statement Module',
    'description': """
    	Supplier Statement Module

	""",
    'version': '13.1.1',
    'depends': ['base'],
    'data' : [
              
        'wizard/supplier_statement_wizard_view.xml',
        'report/report_supplier_statement_view.xml',
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
