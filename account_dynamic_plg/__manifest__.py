# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Dynamic Partner ledger Report',
    'version': '13.0.1.2',
    'category': 'Accounting',
    'author': 'Pycus',
    'summary': 'Dynamic Partner ledger Report with interactive drill down view and extra filters',
    'description': """
                This module support for viewing Partner ledger Report on the screen with 
                drilldown option. Option to download report into Pdf and Xlsx

                    """,
    "price": 35,
    "currency": 'EUR',
    'depends': ['account','report_xlsx','accounting_pdf_reports'],
    'data': [
             "views/assets.xml",
             "views/views.xml",
    ],
    'demo': [],
    'qweb':['static/src/xml/dynamic_plg_report.xml'],
    "images":['static/description/Dynamic_PLG.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
