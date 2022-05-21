# -*- coding: utf-8 -*-
 
 
import csv
import base64
#from StringIO import StringIO
import xlrd
from openerp import api, fields, models, _
import os
from openerp import tools as openerp_tools
from datetime import datetime, date
from itertools import product
 
import xlwt
from xlsxwriter.workbook import Workbook
from io import StringIO
from docutils.parsers.rst.directives import flag

 
class CustomerStatement(models.TransientModel):
    _name = 'wiz.customer.statement'
    
    @api.model
    def _get_partner(self):
        return self.env.context['active_id']
    
    date_from = fields.Date('From Date',required = True)
    date_to = fields.Date('To Date')
    partner_id = fields.Many2one('res.partner', string='Partner',default=_get_partner,readonly=True)
    
    
   
    

    def get_opening_balance(self):
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
        if self.date_from:
           move_line_search_conditions += "and m.date < '%s'"%self.date_from
        if self.partner_id:
            move_line_search_conditions += "and l.partner_id = '%s'"%self.partner_id.id
        move_line_search_conditions += " order by l.debit,l.credit"
        self._cr.execute('select l.id from account_move_line l, account_account_type act,account_journal jn,account_move m,account_account a where %s'
                   %move_line_search_conditions)
        line_ids = map(lambda x: x[0], self._cr.fetchall())
        move_line_ids = self.env['account.move.line'].sudo().browse(line_ids)
        debit=credit=0.0
        data_dict = {}
        count = 1
        if not move_line_ids:
            data_dict = { 
                     'sl_no':count,
                     'name': 'Opening Balance',
                     'debit':  0.000,
                     'credit': 0.000,
                     'balance': 0.000,
                     'date':False,
                     }
        for line in move_line_ids:
            debit += line.debit
            credit += line.credit
            
            data_dict = { 
                     'sl_no':count,
                     'name': 'Opening Balance',
                     'debit': debit or 0.000,
                     'credit':credit or 0.000,
                     'balance':debit-credit or 0.00,
                     'date':False,
                     }
        return (data_dict,count)

       
    def get_invoice_voucher(self,count):
        
        move_line_search_conditions = """l.account_id = a.id
                                        and a.user_type_id = act.id
                                        and act.type in ('receivable')
                                        and l.move_id = m.id
                                        and m.state in ('posted')
                                        and m.journal_id = jn.id
                                        and m.state in ('posted')
                                      """
                                  
        if self.date_from:
           move_line_search_conditions += "and m.date >= '%s'"%self.date_from
        if self.partner_id:
            move_line_search_conditions += "and l.partner_id = '%s'"%self.partner_id.id
        move_line_search_conditions += " order by l.date_maturity ASC"
        self._cr.execute('select l.id from account_move_line l, \
        account_account_type act,account_journal jn,account_move m,account_account a where %s'
                   %move_line_search_conditions)
        
        line_ids = map(lambda x: x[0], self._cr.fetchall())
        move_line_ids = self.env['account.move.line'].browse(line_ids)
        list_data = []
        count = count
        balance_for_line = 0.00
        opening_balance = self.get_opening_balance()
        if opening_balance[0].get('balance'):
            balance_for_line = float(opening_balance[0].get('balance'))
        else:
            balance_for_line = 0.00
        for line in move_line_ids:
            if line.debit > 0:
                balance_for_line = balance_for_line + line.debit
            if line.credit > 0:
                balance_for_line = balance_for_line - line.credit
            count = count + 1
            list_data.append({
            'sl_no':count,
            'date': line.move_id.date,
            'name': line.move_id.name,
            'debit': line.debit or 0.00,
            'credit': line.credit or 0.00,
            'balance': '%.3f' % balance_for_line or "0.000",
            
            })

        return list_data
    
    def update_customer_statement(self):
        state_ids = final_data = newlist = []
        balance_for_line = 0.00
        opening_balance = self.get_opening_balance()
        balance_for_line = opening_balance[0].get('balance')
        list_data = self.get_invoice_voucher(opening_balance[1])
        if opening_balance and opening_balance[0]:
            list_data.append(opening_balance[0])
        newlist = sorted(list_data, key=lambda k: k['sl_no']) 
        for each_data in newlist:
            statement_pool = self.env['customer.statement'].create(each_data)
            state_ids.append(statement_pool.id)
        tree_view_id = self.env.ref('customer_statement_onscreen.customer_statement_tree_view').id
        form_view_id = self.env.ref('customer_statement_onscreen.customer_statement_form_view').id
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Customer Statement'),
            'res_model': 'customer.statement',
            'context': dict(self.env.context),
            'domain' : [('id', '=', state_ids)],
        }
        return action
                
        
