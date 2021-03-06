# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Post Dated Cheque Management',
    'version': '0.09',
    'category': 'Accounting',
    'description': """
    This module is for Post Dated Cheque Management for odoo 11
    """,
    'author': 'Zesty Beanz Technologies Pvt Ltd',
    'website': 'http://www.zbeanztech.com',
    'depends': ['bh_account_vat'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/reject_cheque_view.xml',
        'wizard/res_config_view.xml',
        'views/account_view.xml',
        'views/pdc_view.xml',
        'report/account_report_payment_receipt_templates.xml',
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: