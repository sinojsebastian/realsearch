# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'VAT Switch',
    'version' : '1.1',
    'summary': 'Module to switch VAT on scheduled time',
    'sequence': 15,
    'description': """
VAT on all product will be replaced as per the configuration on the configured date and time
    """,
    'category': 'Accounting/Accounting',
    'website': 'https://www.inforiseit.com/',
    'images' : [],
    'depends' : ['account'],
    'data': [
        'views/vat.xml',
        'security/ir.model.access.csv',
        'data/service_cron.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
