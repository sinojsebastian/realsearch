# -*- coding: utf-8 -*-
{
    'name': 'Journal Entry Report',
    'version': '1.2',
    'author': 'ZestyBeanz',
    'summary': 'Print a particular Journal Entry',
    'description': """  """,
    'category': 'Accounting',
    'website': 'http://www.zestybeanz.com/',
    'depends': ['base', 'account',
                ],

    'data': [
        'views/layout.xml',
        'views/report_journal_entry.xml'
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
