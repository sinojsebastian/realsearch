# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name"         : "Job Order",
    "version"      : "0.19",
    "author"       : "InforiseIT & ZestyBeanz",
    "website"      : "http://www.zbeanztech.com",
    "description"  : """HelpDesk Module""",
    "category"     : "Client Modules/Real Estate",
     'depends': ['zb_building_management','helpdesk','sale'],
    "init_xml"     : [],
    "demo"         : [],
    'data' : [
            'wizard/job_invoice_wizard_view.xml',
            'security/ir.model.access.csv',
            'data/ir_sequence_data.xml',
            'data/data.xml',
            'views/job_order.xml',
            'views/helpdesk_ticket.xml',
            'views/sale_view.xml',
            'views/purchase_view.xml',
            'views/building_view.xml',
     ],
    'test': [
    ],
   
    'installable': True,
    'auto_install': False,
    'application': True,
}
