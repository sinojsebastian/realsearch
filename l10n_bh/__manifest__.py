# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Bahrain - Accounting',
    'version': '13.0.03',
    'author': 'Zesty Beanz Technology (P) Ltd.',
    'website': 'www.zbeanztech.com',
    'category': 'Localization/Account Charts',
    'description': """
Bahrain accounting chart and localization.
=======================================================
    """,
    'depends': ['bh_base', 'account'],
    'demo': [],
    'data': ['l10n_bh_chart.xml',
         'l10n_bh_wizard.xml',
         'l10n_bh_tax.xml',
         'bh_base_decimal_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}