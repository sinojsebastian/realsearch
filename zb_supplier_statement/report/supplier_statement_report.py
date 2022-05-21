# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2020 Tiny SPRL (<http://tiny.be>).
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

import time
from datetime import datetime
from operator import itemgetter

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')
#check
class SupplierStatementReport(models.AbstractModel):
    _name = "report.zb_supplier_statement.report_supplierstatement"
    
    def get_opening_balance(self, date, supplier_id):
        '''Function to calculate opening balance'''
        
        move_line_search_conditions = """l.account_id = a.id
                                        and a.user_type_id = act.id
                                        and act.type in ('payable')
                                        and l.move_id = m.id
                                        and m.journal_id = jn.id
                                      """
        if date:
           move_line_search_conditions += "and m.date < '%s'"%date
        if supplier_id:
            move_line_search_conditions += "and l.partner_id = '%s'"%supplier_id
        move_line_search_conditions += " order by l.debit,l.credit"
        self._cr.execute('select l.id from account_move_line l, account_account_type act,account_journal jn,account_move m,account_account a where %s'
                   %move_line_search_conditions)
        line_ids = map(lambda x: x[0], self._cr.fetchall())
        move_line_ids = self.env['account.move.line'].browse(line_ids)
        debit=0.0
        credit=0.0
        for line in move_line_ids:
            debit += line.debit
            credit += line.credit
        vals = ({
                     'debit':debit or 0.000,
                     'credit':credit  or 0.000,
                     'balance':debit-credit or 0.000,
                     })

        return vals
    
    def get_invoice_voucher(self, supplier_id, date, end_date, journal_type,show_paid_inv):
        
        move_line_search_conditions = """l.account_id = a.id
                                        and a.user_type_id = act.id
                                        and act.type in ('payable')
                                        and l.move_id = m.id
                                        and m.journal_id = jn.id
                                        and jn.type not in ('post_dated_chq')
                                      """
        if date:
           move_line_search_conditions += "and m.date >= '%s'"%date
        if not show_paid_inv :
           move_line_search_conditions += "and l.full_reconcile_id is NULL "
        if supplier_id:
            move_line_search_conditions += "and l.partner_id = '%s'"%supplier_id
        
        move_line_search_conditions += " order by l.debit,l.credit"
        self._cr.execute('select l.id from account_move_line l, \
        account_account_type act,account_journal jn,account_move m,account_account a where %s'
                   %move_line_search_conditions)
        line_ids = map(lambda x: x[0], self._cr.fetchall())
        move_line_ids = self.env['account.move.line'].browse(line_ids)
        list_data = []
        s =''
        maturity = ''
        due_date = ''
        for line in move_line_ids:
            if not line.reconciled and not line.payment_id:
                due_date = line.date_maturity
                maturity = (datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')-datetime.strptime(str(due_date), '%Y-%m-%d')).days
            
            s =''
            for all in line.move_id.line_ids:
                if all.partner_id==line.partner_id:
                    s += str(all.name) + ','
                
            list_data.append({
            'date': line.move_id.date,
            'ref': 'Move Name: '+line.move_id.name +'\n'+'Description : ' +s[:-1],
            'debit': line.debit or 0.000,
            'credit': line.credit or 0.000,
            'due_date':due_date or '',
            'due_days':maturity or '',
            })

        return list_data


    
    @api.model
    def _get_report_values(self, docids,data=None):
        result =[]
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        supplier_id = docs.id
        
        dbt = ''
        cdt = ''
        sign = ''
        
        from_date = data['form'][0].get('from_date', time.strftime('%Y-%m-%d'))
        show_paid_inv = data['form'][0].get('show_paid_inv', False)
        end_date = datetime.today().strftime('%Y-%m-%d')
        journal_type = {
            'sale':'Sales'
        }
        if from_date:
            open_balance = self.get_opening_balance(from_date, supplier_id)
            
            check_first_move_line = True
            balance_for_line = open_balance.get('balance')
            list_data = self.get_invoice_voucher( supplier_id, from_date, end_date, journal_type,show_paid_inv)
            list_data = sorted(list_data, key=lambda d: (d['date'])) 
            debit_sum = 0
            credit_sum = 0
            if not list_data:
                data_dict = { 
                         'ref': 'Opening Balance',
                         'journal': ' ',
                         'debit': open_balance.get('debit'),
                         'credit': open_balance.get('credit'),
                         'due_date':'',
                         'due_days':'',
                         'open_balance': open_balance.get('balance') or 0.000,
                         'date':'',
                    }
                result.append(data_dict)
            for each_data in list_data:
                if check_first_move_line:
                    check_first_move_line = False
                    data_dict = { 
                         'ref': 'Opening Balance',
                         'journal': ' ',
                         'debit': open_balance.get('debit') or 0.000,
                         'credit': open_balance.get('credit') or 0.000,
                         'open_balance': open_balance.get('balance') or 0.000,
                         'date':'',
                         'due_date':'',
                         'due_days':'',
                    }
                    result.append(data_dict)

                if each_data['debit'] > 0:
                    balance_for_line = balance_for_line + each_data['debit']
                    debit_sum += each_data['debit']
                if each_data['credit']>0:
                    credit_sum += each_data['credit']
                    balance_for_line = balance_for_line - each_data['credit']
                data_dict = {
                    'date': each_data['date'] and datetime.strptime(str(each_data['date']), '%Y-%m-%d').strftime('%d-%m-%Y') or '',
                    'ref': each_data['ref'],
                    'debit': each_data['debit'] or 0.000,
                    'credit': each_data['credit'] or 0.000,
                    'open_balance': -balance_for_line or 0.000,
                    'due_date':each_data['due_date'] and datetime.strptime(str(each_data['due_date']), '%Y-%m-%d').strftime('%d-%m-%Y') or '',
                    'due_days':each_data['due_days'],
                    
                }
                result.append(data_dict)
        docargs = {
                   'doc_ids':self._ids,
                   'doc_model': model,
                   'docs': docs,
                   'statement_data' : result,
                   'data': data['form'],
                   }
        return docargs
        
       
