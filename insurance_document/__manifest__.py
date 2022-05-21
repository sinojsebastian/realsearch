# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Insurance Document",
    'description': """
        Insurance Document Module
    """,
    'author': 'Zesty Beanz Technology (P) Ltd.',
    'website': 'www.zbeanztech.com',
    'category': 'Human Resources',
    'version': '0.06',
    # any module necessary for this one to work correctly
    'depends': ['base','zb_building_management'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/insurance_document_view.xml',
        'views/building_view.xml',
    ], 
    'test': [],
    'installable': True,
    'auto_install': False,
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: