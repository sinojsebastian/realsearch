# -*- encoding: utf-8 -*-
# Copyright Knacktechs SA

{
    'name': 'Advance Payment Allocation',
    'description': """
    This module allows to do the partial payment of multiple invoices of same customer from payment menu.
""",
    "version": "13.1.0.45",
    "license": "AGPL-3",
    'author': "Knacktechs Solutions",
    'category': 'Accounting',
    'website': 'http://www.knacktechs.com',
    'depends': ['base','sale','account'],
    
    'data': [   
            'security/ir.model.access.csv',
            'views/account_payment_view.xml',
            
               ],
    'images': [
        'static/description/banner.jpg'
    ],
    
    # tests order matter
    'test': [
             ],
    'active': False,
    'installable': True,
    'application': True,
    'price':'16',
    'currency':'EUR'
}
