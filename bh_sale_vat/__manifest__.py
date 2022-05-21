# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Bahrain Sale VAT',
    'version': '0.11',
    'author': 'Zesty Beanz Technology (P) Ltd.',
    'depends': ['sale_management'],
    'website': 'www.zbeanztech.com',
    'demo': [],
    'description': """
        Bahrain Sale VAT
    """,
    'data': [
        'report/report_saleorder.xml',
        'bh_sale_vat_view.xml',
        'sale_report.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
