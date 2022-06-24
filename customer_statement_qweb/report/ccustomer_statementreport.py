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
from odoo.exceptions import UserError
import time
from openerp import api, fields, models,_
from datetime import datetime
from operator import itemgetter
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class CustomersStatementReport(models.AbstractModel):
    _name = "report.customer_statement_qweb.report_customerstatement"
    
    def get_opening_balance(self, date, customer_id,show_paid_inv,module_id):
        '''Function to calculate opening balance'''
        
        move_line_search_conditions = """l.account_id = a.id
                                        and a.user_type_id = act.id
                                        and act.type in ('receivable')
                                        and l.move_id = m.id
                                        and m.state in ('posted')
                                        and m.journal_id = jn.id
                                        and jn.type not in ('post_dated_chq')
                                      """
        lines_to_display = {}
        if date:
           move_line_search_conditions += "and m.date < '%s'"%date
        if customer_id:
            move_line_search_conditions += "and l.partner_id = '%s'"%customer_id

        if show_paid_inv :
            move_line_search_conditions += "and m.invoice_payment_state in ('paid','in_payment','not_paid')"
        else:
            move_line_search_conditions += "and m.invoice_payment_state in ('in_payment','not_paid')"
        
        if module_id:
            move_line_search_conditions += "and l.module_id = '%s'"%module_id
 
        move_line_search_conditions += " order by l.debit,l.credit"
        self._cr.execute('select l.id from account_move_line l, account_account_type act,account_journal jn,account_move m,account_account a where %s'
                   %move_line_search_conditions)
        line_ids = map(lambda x: x[0], self._cr.fetchall())
        move_line_ids = self.env['account.move.line'].sudo().browse(line_ids)

        debit=credit=0.0
        for line in move_line_ids:

            debit += line.debit
            credit += line.credit
        vals = ({
                     'debit':debit,
                     'credit':credit,
                     'balance':debit-credit
                     })

        return vals

    def action_statement_values(self, move_lines):
        data = []
        maturity = ''
        due_date = ''
        for line in move_lines:
            description = ''
            desc_list = []
            refr = '%s: %s'%(line.move_id.name,line.name)
            # '%s'%(line.move_id.name)
            if not line.reconciled and not line.payment_id:
                due_date = line.date_maturity
                if due_date:
                    maturity = (datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT)-datetime.strptime(str(due_date), DEFAULT_SERVER_DATE_FORMAT)).days
            for each in line.move_id.invoice_line_ids:
                if each.name:
                    desc_list.append(each.name)
            if desc_list:
                description = (','.join(desc_list))

            data.append({
            'date': line.move_id.date,
            'ref': refr,
            'description':description,
            'due_date':due_date or '',
            'due_days':maturity or '',
            'module_id':line.module_id or False,
            'debit': line.debit or 0.000,
            'credit': line.credit or 0.000,
            })
        return data


    def get_invoice_voucher(self, show_paid_inv,customer_id, date, end_date, journal_type,module_id):

        move_line_search_conditions = """l.account_id = a.id
                                        and a.user_type_id = act.id
                                        and act.type in ('receivable')
                                        and l.move_id = m.id
                                        and m.state in ('posted')
                                        and m.journal_id = jn.id 
                                        and jn.type not in ('post_dated_chq')
                                        
                                        
                                      """
                                      #and not l.reconciled
        if date:
           move_line_search_conditions += "and m.date >= '%s'"%date
        if end_date:
           move_line_search_conditions += "and m.date <= '%s'"%end_date
        # if not show_paid_inv :
        #    move_line_search_conditions += "and l.full_reconcile_id is NULL "

        # if show_paid_inv:
        #     move_line_search_conditions += "and m.invoice_payment_state in ('paid','in_payment','not_paid')"
        # else:
        #     move_line_search_conditions += "and m.invoice_payment_state in ('in_payment','not_paid')"

        if customer_id:
            move_line_search_conditions += "and l.partner_id = '%s'"%customer_id
        if module_id:
            move_line_search_conditions += "and l.module_id = '%s'"%module_id

        move_line_search_conditions += " order by l.debit,l.credit"
        self._cr.execute('select l.id from account_move_line l, \
        account_account_type act,account_journal jn,account_move m,account_account a where %s'
                   %move_line_search_conditions)
        line_ids = map(lambda x: x[0], self._cr.fetchall())
        move_line_ids = self.env['account.move.line'].sudo().browse(line_ids)
        if show_paid_inv:
            move_lines = move_line_ids.filtered(lambda inv: inv.move_id.invoice_payment_state in ('paid','in_payment','not_paid') or inv.move_id.type == 'entry')
            data = self.action_statement_values(move_lines)
            return data
        else:
            move_lines = move_line_ids.filtered(lambda inv: inv.move_id.invoice_payment_state in ('in_payment', 'not_paid') or inv.move_id.type == 'entry')
            data = self.action_statement_values(move_lines)
            return data

    @api.model
    def _get_report_values(self, docids,data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        result =[]
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        customer_id = docs.id
        
        dbt = False
        cdt = False
        sign = ''
        company_currency = self.env.user.company_id.currency_id
        from_date = data['form'][0].get('from_date', time.strftime(date_format))
        to_date = data['form'][0].get('to_date', time.strftime(date_format))
        show_paid_inv = data['form'][0].get('show_paid_inv',False)
        module_id = data['form'][0].get('module_id',False)
        if module_id:
            module = module_id[0]
        else:
            module = False
        customer = docs.name
        if not to_date:
            to_date = datetime.today().strftime(date_format)
        journal_type = {
            'sale':'Sales'
        }
        data_dict = {}
        open_balance = self.get_opening_balance(from_date, customer_id,show_paid_inv,module)
        check_first_move_line = True
        balance_for_line = open_balance.get('balance')
        list_data = self.get_invoice_voucher(show_paid_inv,customer_id, from_date, to_date, journal_type,module)
        list_data = sorted(list_data, key=lambda d: (d['date'])) 
        data_dict = {}
        for each in list_data:
            key = each['module_id']
            if key in data_dict:
                data_dict[key].append(each)
            else:
                data_dict.update({key:[each]})
        for module in data_dict:
            debit_sum = 0
            credit_sum = 0
            if not data_dict[module]:
                data_vals = { 
                     'ref': 'Opening Balance',
                     'journal': ' ',
                     'description':' ',
                     'debit': open_balance['debit'],
                     'credit': open_balance['credit'],
                     'due_date':'',
                     'due_days':'',
                     'open_balance': open_balance['balance'],
                     'date':'',
                     'currency_id':company_currency.id
                }
                data_dict[module].append(data_vals)
            data_vals = {}
            for each_data in data_dict[module]:
                if check_first_move_line:
                    check_first_move_line = False
                    data_vals = { 
                     'ref': 'Opening Balance',
                     'journal': ' ',
                     'description':' ',
                     'debit': open_balance['debit'],
                     'credit': open_balance['credit'],
                     'due_date':'',
                     'due_days':'',
                     'open_balance': open_balance['balance'],
                     'date':'',
                     'currency_id':company_currency.id
                     }
                    # data_dict[module].insert(0,data_vals)
                if each_data['debit'] > 0:
                    balance_for_line = balance_for_line + each_data['debit']
                    debit_sum += each_data['debit']
                if each_data['credit']>0:
                    credit_sum += each_data['credit']
                    balance_for_line = balance_for_line - each_data['credit']
                each_data.update({'open_balance':balance_for_line})
            data_dict[module].insert(0,data_vals)
            # debit_sum = 0
            # credit_sum = 0
            # data_dict ={}
            # if not list_data:
            #     data_dict = { 
            #              'ref': 'Opening Balance',
            #              'journal': ' ',
            #              'description':' ',
            #              'debit': open_balance.get('debit'),
            #              'credit': open_balance.get('credit'),
            #              'due_date':'',
            #              'due_days':'',
            #              'open_balance': open_balance.get('balance'),
            #              'date':'',
            #              'currency_id':company_currency.id
            #         }
            #     result.append(data_dict)
                
            # for each_data in list_data:
            #     if check_first_move_line:
            #         check_first_move_line = False
            #         data_dict = { 
            #              'ref': 'Opening Balance',
            #              'journal': ' ',
            #              'description':' ',
            #              'debit': open_balance.get('debit'),
            #              'credit': open_balance.get('credit'),
            #              'due_date':'',
            #              'due_days':'',
            #              'open_balance': open_balance.get('balance'),
            #              'date':'',
            #              'currency_id':company_currency.id
            #         }
            #         result.append(data_dict)
            #
            #     if each_data['debit'] > 0:
            #         balance_for_line = balance_for_line + each_data['debit']
            #         debit_sum += each_data['debit']
            #     if each_data['credit']>0:
            #         credit_sum += each_data['credit']
            #         balance_for_line = balance_for_line - each_data['credit']
            #     data_dict = {
            #         'date': each_data['date'] or '',
            #         'ref': each_data['ref'],
            #         'description':each_data['description'],
            #         'debit': each_data['debit'],
            #         'credit': each_data['credit'],
            #         'open_balance': balance_for_line,
            #         'due_date':each_data['due_date'] or '',
            #         'due_days':each_data['due_days'],
            #         'currency_id':company_currency.id
            #
            #     }
            #     result.append(data_dict)
        docargs = {
                   'doc_ids':self._ids,
                   'doc_model': model,
                   'docs': docs,
                   'server_date':DEFAULT_SERVER_DATE_FORMAT,
                   'date_format':date_format,
                   'statement_data' : data_dict,
                   'data': data['form'],
                   }
        return docargs

  
