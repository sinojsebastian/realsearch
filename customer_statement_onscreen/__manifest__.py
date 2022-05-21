# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Customer Statement OnScreen',
    'author': "Zesty Beanz Technologies Pvt LTD",
    'website': "http://www.zbeanztech.com",
    'summary': 'Customer Statement Onscreen Module',
    'description': """
    	Customer Statement Module

	""",
    'version': '13.1.0',
    'depends': ['base'],
    'data' : [
        'security/ir.model.access.csv',      
        'wizard/update_customer_statement_view.xml',
        'views/customer_statement_view.xml',
        
     ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
