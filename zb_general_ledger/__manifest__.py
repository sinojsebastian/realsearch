# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)
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
    'name': 'General Ledger in Excel',
    'version': '1.0.6',
    'author': 'Zesty Beanz Technology FZE',
    'website': 'www.zbeanztech.com',
    'depends': ['account', 'report_xlsx','stock','accounting_pdf_reports'],
    'demo': [],
    'description': 
        """
        General Ledger in Excel
        """,
    'data': [
            'report/report.xml',
            'wizard/account_report_general_ledger_view.xml',
            'views/report_generalledger.xml',
        ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
    'summary': 'General Ledger Reports with Excel and PDF options',
    'category': 'Account',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: