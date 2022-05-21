# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Bahrain Account VAT',
    'version': '1.3',
    'author': 'Zesty Beanz Technology (P) Ltd.',
    'website': 'www.zbeanztech.com',
    'depends': ['account'],
    'demo': [],
    'description': """ Bahrain Account VAT""",
    'data': [
            'report/report_invoice.xml',
            'view/bh_account_vat_view.xml',
            'view/account_report.xml',
            

             ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
