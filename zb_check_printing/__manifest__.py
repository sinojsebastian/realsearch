# -*- coding: utf-8 -*-
{
    'name': 'Check Printing',
    'version': '1.6',
    'category': 'Hidden/Dependency',
    'summary': 'Check printing commons',
    'description': """
        Customised Check Printing Module.
    """,
    'website': 'https://www.odoo.com/page/accounting',
    'depends' : ['account_check_printing','zb_pdc_name_on_cheque','account_payment'],
    'data': [
        'data/report_paperformat.xml',
        'views/account_views.xml',
        'views/check_printing_report.xml',
        'views/report_check.xml',
        
        
    ],
    'installable': True,
    'auto_install': False,
}
