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
    
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)

class CustomerStatementXlsxReport(models.AbstractModel):
    _name = 'report.customer_statement_xlsx.report_customerstatement.xlsx'    
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, wiz):
        #FORMATS##
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 15})
        
        sub_heading_format = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 12})
        
        sub_heading_format1 = workbook.add_format({'align': 'left',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 11,'border':0})
        
        sub_heading_format2 = workbook.add_format({'align': 'right',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 11})
        
        number_format = workbook.add_format({ 'align': 'right',
                                              'size': 10,
                                              'bold': True,
                                              'num_format': '#,###0.000'})
        
        table_heading = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 11})
        
        bold = workbook.add_format({'bold': True, 
                                    'align': 'right',
                                    'size': 10,'num_format': '#,###0.000'
                                    })
        
        sub_menu_format = workbook.add_format({'bold': True,
                                               'align': 
                                               'left','size': 10})
        text_center = workbook.add_format({ 'align': 'center','size': 10,'bold': True})
        text_left = workbook.add_format({ 'align': 'left', 'text_wrap': True,'size': 10,'bold': True})
        text_right = workbook.add_format({ 'align': 'right','size': 10,'bold': True})
        text = workbook.add_format({ 'align': 'left','size': 13,'bold': True})
        # date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        formater = workbook.add_format({'border':1})
        
        
        worksheet = workbook.add_worksheet("Customer Statement Report")
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        if wiz.to_date:
            to_date_wiz =  datetime.strptime(str(wiz.to_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '',
        else:
            to_date_wiz = datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or ''
        from_date_wiz = ''
        if wiz.from_date:
            from_date_wiz = datetime.strptime(str(wiz.from_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '',
        name_wiz = wiz.partner_id.name
        user_id = self.env['res.users'].browse(self.env.uid)
        company_id = user_id.company_id
        street = ''
        city =''
        country = ''
        company_name = ''
        if company_id.name:
            company_name = company_id.name
        if company_id.street:
            street = company_id.street + ', '
        if company_id.street2:
            street +=  company_id.street2 
        if company_id.city:
            city +=  company_id.city + ', ' 
        if company_id.state_id:
            city +=  company_id.state_id.name + ', ' 
        if company_id.zip:
            city += company_id.zip
        if company_id.country_id:
            country += company_id.country_id.name 
        building_name = ''
        module_name = ''
        if wiz.building_id:
            building_name = wiz.building_id.name
        if wiz.module_id:
            module_name = wiz.module_id.name
            
            
        print('===========================',wiz.building_id.name)
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 35)
        worksheet.set_column('D:D', 11)
        worksheet.set_column('E:E', 11)
        worksheet.set_column('F:F', 11)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 16)
        
        worksheet.merge_range('A1:H1',company_name,text_left)
        worksheet.merge_range('A2:H2',street,text_left)
        worksheet.merge_range('A3:H3',city,text_left)
        worksheet.merge_range('A4:H4',country,text_left)
        
        worksheet.merge_range('A5:H5','Statement Of Account',heading_format)
        worksheet.merge_range('A6:H6','As On'+" "+str(to_date_wiz),sub_heading_format)
        worksheet.merge_range('A7:H7','Name: '+" "+str(name_wiz),sub_heading_format1)
        worksheet.merge_range('A8:B8','Building: '+" "+building_name,sub_heading_format1)
        worksheet.merge_range('A9:B9','Module: '+" "+module_name,sub_heading_format1)
        # if from_date_wiz:
        #     worksheet.merge_range('C8:H8','From date: '+" "+str(from_date_wiz[0]),sub_heading_format2)
        # else:
        #     worksheet.merge_range('C8:H8','From date:',sub_heading_format2)
        # worksheet.merge_range('C9:H9','To date: '+" "+str(to_date_wiz),sub_heading_format2)

        worksheet.write(10, 0, "Date", sub_heading_format1)
        worksheet.write(10, 1, "Particulars", sub_heading_format1)
        worksheet.write(10, 2, "Invoice Description", sub_heading_format1)
        worksheet.write(10, 3, "Debit", sub_heading_format1)
        worksheet.write(10, 4, "Credit", sub_heading_format1)
        worksheet.write(10, 5, "Balance", sub_heading_format1)
        worksheet.write(10, 6, "Due on", sub_heading_format1)
        worksheet.write(10, 7, "Overdue by days", sub_heading_format1)
        
        row = 11
        result =[]
        debit = credit = 0.00
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        customer_id = wiz.partner_id.id
        
        dbt = ''
        cdt = ''
        sign = ''
        company_currency = self.env.user.company_id.currency_id
        from_date = wiz.from_date
        end_date = wiz.to_date
        if not end_date:
            end_date = datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT).date()
        from_date_wiz = wiz.from_date
        show_paid_inv = wiz.show_paid_inv

        journal_type = {
            'sale':'Sales'
        }
        open_balance = self.get_opening_balance(end_date, customer_id,show_paid_inv,wiz.module_id)
        check_first_move_line = True
        balance_for_line = open_balance.get('balance')
        list_data = self.get_invoice_voucher(show_paid_inv,customer_id, from_date, end_date, journal_type,wiz.module_id)
        print('=============list_data==============',list_data)
        list_data = sorted(list_data, key=lambda d: (d['date'])) 
        debit_sum = 0
        credit_sum = 0
        data_dict ={}
        if not list_data:
            data_dict = { 
                     'ref': 'Opening Balance',
                     'journal': ' ',
                     'description':' ',
                     'debit': open_balance.get('debit'),
                     'credit': open_balance.get('credit'),
                     'due_date':'',
                     'due_days':'',
                     'open_balance': open_balance.get('balance'),
                     'date':'',
                     'currency_id':company_currency.id
                }
            result.append(data_dict)
            row = row+1
            for record in result:
                if record['debit'] >=0:
                    balance_for_line = balance_for_line - record['debit']
                    debit_sum += record['debit']
                if record['credit']>=0:
                    credit_sum += record['credit']
                    balance_for_line = balance_for_line + record['credit']
                worksheet.write(row, 0, record['date'],text_center)
                worksheet.write(row, 1, record['ref'],text_left)
                worksheet.write(row, 2, record['description'],text_left)
                worksheet.write(row, 3, record['debit'],number_format)
                worksheet.write(row, 4, record['credit'],number_format)
                worksheet.write(row, 5, record['open_balance'],number_format)
                worksheet.write(row, 6, record['due_date'],text_center)
                worksheet.write(row, 7, record['due_days'],text_center)
                worksheet.set_row(row, 25)
                row = row+1
        for each_data in list_data:
            if check_first_move_line:
                check_first_move_line = False
                data_dict = { 
                     'ref': 'Opening Balance',
                     'description':' ',
                     'journal': ' ',
                     'debit': open_balance.get('debit'),
                     'credit': open_balance.get('credit'),
                     'due_date':'',
                     'due_days':'',
                     'open_balance': open_balance.get('balance'),
                     'date':'',
                     'currency_id':company_currency.id
                }
                result.append(data_dict)
                row = row+1
                worksheet.write(row, 0, '')
                worksheet.write(row, 1, data_dict['ref'],text_left)
                worksheet.write(row, 2, data_dict['description'],text_left)
                worksheet.write(row, 3, data_dict['debit'],number_format)
                worksheet.write(row, 4, data_dict['credit'],number_format)
                worksheet.write(row, 5, data_dict['open_balance'],number_format)
                worksheet.write(row, 6, data_dict['due_date'],text_center)
                worksheet.write(row, 7, data_dict['due_days'],text_center)
                worksheet.set_row(row, 25)
                 
            if each_data['debit'] >=0:
                balance_for_line = balance_for_line - each_data['debit']
                debit_sum += each_data['debit']
            if each_data['credit']>=0:
                credit_sum += each_data['credit']
                balance_for_line = balance_for_line + each_data['credit']
            data_dict = {
                'date': each_data['date'] and datetime.strptime(str(each_data['date']), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '',
                'ref': each_data['ref'],
                'description':each_data['description'],
                'debit': each_data['debit'],
                'credit': each_data['credit'],
                'open_balance': balance_for_line,
                'due_date':each_data['due_date'] and datetime.strptime(str(each_data['due_date']), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '',
                'due_days':each_data['due_days'],
                'currency_id':company_currency.id
                 
            }
            result.append(data_dict)
            row = row+1
            worksheet.write(row, 0, data_dict['date'],text_center)
            worksheet.write(row, 1, data_dict['ref'],text_left)
            worksheet.write(row, 2, data_dict['description'],text_left)
            worksheet.write(row, 3, data_dict['debit'],number_format)
            worksheet.write(row, 4, data_dict['credit'],number_format)
            worksheet.write(row, 5, data_dict['open_balance'],number_format)
            worksheet.write(row, 6, data_dict['due_date'],text_center)
            worksheet.write(row, 7, data_dict['due_days'],text_center)
            worksheet.set_row(row, 25)
        row = row+1
        worksheet.write(row, 1, 'Balance',text)
        if debit_sum < credit_sum:
             credit = '{:,.3f}'.format(data_dict['open_balance'])
             worksheet.write(row, 4,"-"+credit+"Cr",bold)
        elif debit_sum > credit_sum:
             debit = '{:,.3f}'.format(data_dict['open_balance'])
             worksheet.write(row, 4,debit+"Dr",bold)
        elif debit_sum == 0 and credit_sum == 0:
             worksheet.write(row, 4,data_dict['open_balance'],bold)
        elif (debit_sum and credit_sum > 0) and debit_sum == credit_sum:
            worksheet.write(row, 4,debit_sum - credit_sum,bold)

    
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
        # if show_paid_inv :
        #     move_line_search_conditions += "and m.invoice_payment_state in ('paid','in_payment','not_paid')"
        # else:
        #     move_line_search_conditions += "and m.invoice_payment_state in ('in_payment','not_paid')"
        if module_id:
            move_line_search_conditions += "and l.module_id = '%s'"%module_id.id  
        move_line_search_conditions += " order by l.debit,l.credit"
        self._cr.execute('select l.id from account_move_line l, account_account_type act,account_journal jn,account_move m,account_account a where %s'
                   %move_line_search_conditions)
        line_ids = map(lambda x: x[0], self._cr.fetchall())
        move_line_ids = self.env['account.move.line'].sudo().browse(line_ids)
        if show_paid_inv:
            move_line_ids = move_line_ids.filtered(lambda inv: inv.move_id.invoice_payment_state in ('paid','in_payment','not_paid') or inv.full_reconcile_id != False)
        else:
            move_line_ids = move_line_ids.filtered(lambda inv: inv.move_id.invoice_payment_state in ('in_payment', 'not_paid') or not inv.full_reconcile_id)
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
        # if show_paid_inv :
        #     move_line_search_conditions += "and m.invoice_payment_state in ('paid','in_payment','not_paid')"
        # else:
        #     move_line_search_conditions += "and m.invoice_payment_state in ('in_payment','not_paid')"
        if customer_id:
            move_line_search_conditions += "and l.partner_id = '%s'"%customer_id  
        if module_id:
            move_line_search_conditions += "and l.module_id = '%s'"%module_id.id    
        
        move_line_search_conditions += " order by l.debit,l.credit"
        self._cr.execute('select l.id from account_move_line l, \
        account_account_type act,account_journal jn,account_move m,account_account a where %s'
                   %move_line_search_conditions)
        line_ids = map(lambda x: x[0], self._cr.fetchall())
        move_line_ids = self.env['account.move.line'].sudo().browse(line_ids)
        if show_paid_inv:
            move_line_ids = move_line_ids.filtered(lambda inv: inv.move_id.invoice_payment_state in ('paid','in_payment','not_paid') or inv.full_reconcile_id != False)
        else:
            move_line_ids = move_line_ids.filtered(lambda inv: inv.move_id.invoice_payment_state in ('in_payment', 'not_paid') or not inv.full_reconcile_id)
        data = []
        l_debt =0
        l_credit =0
        maturity = ''
        due_date = ''
        ref = ''
        for line in move_line_ids:
            description = ''
            desc_list = []
            s =''
            for all in line.move_id.line_ids:
                if all.partner_id==line.partner_id:
                    s += str(all.name) + ','
            if not line.reconciled and not line.payment_id:
                due_date = line.date_maturity
                if due_date:
                    maturity = (datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT)-datetime.strptime(str(due_date), DEFAULT_SERVER_DATE_FORMAT)).days
            l_debt += line.debit
            l_credit += line.credit
            ref = '%s: %s'%(line.move_id.name,line.name)
            for each in line.move_id.invoice_line_ids:
                desc_list.append(each.name)
            description = (','.join(desc_list))
                
            # s[:-1]
            data.append({
            'date': line.move_id.date,
            'ref': ref,
            'description':description,
            'due_date':due_date or '',
            'due_days':maturity or '',
            'debit': line.debit or 0.00,
            'credit': line.credit or 0.00,
            })
        return data
    
#      
