# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Odoo 13 Inforise Accounting Report Module',
    'author': 'Zesty Beanz Technology (P) Ltd.',
    'website': 'www.zbeanztech.com',
    'version': '13.0.1.4',
    'demo': [],
    'description': """
                  Odoo 13 Inforise Accounting Report Module
                   """,
                 
    'depends': ['account'],
    'data': [
        'report/report_voucher.xml',
        'report/customer_invoice_report.xml',
        'report/report_invoice.xml',
        'report/payment_receipt_report.xml',
        'views/report_external_layout.xml',
        'views/report.xml',
        'views/res_company_view.xml',
#         'views/account_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

