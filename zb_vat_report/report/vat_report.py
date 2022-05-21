
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2020 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)
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

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract
from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)

class VATReport(models.AbstractModel):
    _name = 'report.zb_vat_report.vat_report.xlsx'    
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, wizard):
        
        ##FORMATS STARTS##
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        design_formats = {}
        design_formats['heading_format'] = workbook.add_format({'align': 'left',
                                               'valign': 'vjustify',
                                               'bold': True, 'size': 11,
                                               'font_name': 'Times New Roman',
                                               'text_wrap': True, 'shrink': True})
        design_formats['heading_format_1'] = workbook.add_format({'align': 'left',
                                               'valign': 'vjustify',
                                               'bold': False, 'size': 9,
                                               'font_name': 'Times New Roman',
                                               'text_wrap': True, 'shrink': True})
        design_formats['heading_format_2'] = workbook.add_format({'align': 'center',
                                               'valign': 'vjustify',
                                               'bold': True, 'size': 11,
                                               'font_name': 'Times New Roman',
                                               'text_wrap': True, 'shrink': True})
        design_formats['sub_heading_format'] = workbook.add_format({'align': 'right',
                                                   'valign': 'vjustify',
                                                   'bold': True, 'size': 9,
                                                   'font_name': 'Times New Roman',
                                                   'text_wrap': True, 'shrink': True})
        design_formats['sub_heading_format_left'] = workbook.add_format({'align': 'left',
                                                   'valign': 'vjustify',
                                                   'bold': True, 'size': 9,
                                                   'font_name': 'Times New Roman',
                                                   'text_wrap': True, 'shrink': True})
        design_formats['sub_heading_format_center'] = workbook.add_format({'align': 'center',
                                                   'valign': 'vjustify',
                                                   'bold': True, 'size': 9,
                                                   'font_name': 'Times New Roman',
                                                   'text_wrap': True, 'shrink': True})
        design_formats['bold'] = workbook.add_format({'bold': True, 'font_name': 'Times New Roman', 
                                                      'size': 11,
                                                      'text_wrap': True})
        design_formats['bold_center'] = workbook.add_format({'bold': True, 'font_name': 'Times New Roman', 
                                                      'size': 11,
                                                      'text_wrap': True,
                                                      'align': 'center'})
        design_formats['date_format'] = workbook.add_format({'num_format': date_format, 
                                           'font_name': 'Times New Roman', 'size': 11,
                                           'align': 'center', 'text_wrap': True})
        design_formats['normal_format'] = workbook.add_format({'font_name': 'Times New Roman',
                                            'size': 11, 'text_wrap': True})
        design_formats['normal_format_right'] = workbook.add_format({'font_name': 'Times New Roman',
                                           'align': 'right', 'size': 11, 'text_wrap': True})
        design_formats['normal_format_central'] = workbook.add_format({'font_name': 'Times New Roman',
                                            'size': 11, 'align': 'center', 'text_wrap': True})
        design_formats['amount_format'] = workbook.add_format({'num_format': '#,##0.000', 
                                         'font_name': 'Times New Roman',
                                         'align' : 'right', 'size': 11, 'text_wrap': True})
        design_formats['amount_format_1'] = workbook.add_format({'num_format': '#,##0', 
                                         'font_name': 'Times New Roman',
                                         'align' : 'right', 'size': 11, 'text_wrap': True})
        design_formats['normal_num_bold'] = workbook.add_format({'bold': True, 'num_format': '#,##0.000',
                                               'font_name': 'Times New Roman', 
                                               'align' : 'right', 'size': 11, 'text_wrap': True})
        design_formats['float_rate_format'] = workbook.add_format({'num_format': '###0.00', 
                                         'font_name': 'Times New Roman',
                                         'align' : 'right', 'size': 11, 'text_wrap': True})
        design_formats['int_rate_format'] = workbook.add_format({'num_format': '###0', 
                                         'font_name': 'Times New Roman',
                                         'align' : 'right', 'size': 11, 'text_wrap': True})
        ##FORMATS END##
        
        params = {
            'start_date' : wizard.start_date, 
            'end_date' : wizard.end_date,
        }
        
        worksheet = workbook.add_worksheet("VAT Report")
        #Title Of Sheet#
        user_id = self.env['res.users'].browse(self.env.uid)
        company_id = user_id.company_id
        company = str(user_id.company_id.name)
        company_trn = "TRN: " + str(company_id.vat)
        worksheet.set_column('A:A', 3)
        worksheet.set_column('B:B', 4)
        worksheet.set_column('C:C', 65)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 18)
        worksheet.merge_range('%s:%s'%(excel_style(1, 3),excel_style(1, 4)), "VAT Return Report", design_formats['heading_format_2'])
        worksheet.merge_range('%s:%s'%(excel_style(2, 3),excel_style(2, 4)), company, design_formats['heading_format'])
        address = ''
        if company_id.street:
            address += company_id.street
        if company_id.street2:
            address += ', ' + company_id.street2
        if company_id.city:
            address += ', ' + company_id.city
        if company_id.state_id:
            address += ', ' + company_id.state_id.name
        if company_id.zip:
            address += ', ' + company_id.zip
        if company_id.country_id:
            address += ', ' + company_id.country_id.name
        worksheet.merge_range('%s:%s'%(excel_style(3, 3),excel_style(4, 4)), address, design_formats['normal_format'])
        worksheet.write(2, 4, 'From: ' + datetime.strptime(str(wizard.start_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format), design_formats['date_format'])
        worksheet.write(2, 5, 'To: ' + datetime.strptime(str(wizard.end_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format), design_formats['date_format'])
        worksheet.merge_range('%s:%s'%(excel_style(5, 3),excel_style(5, 4)), company_trn, design_formats['normal_format'])
        worksheet.write(6, 1, 'No.', design_formats['bold_center'])
        worksheet.write(6, 2, 'Sales', design_formats['bold_center'])
        worksheet.write(6, 3, 'Amount (BHD)', design_formats['bold_center'])
        worksheet.write(6, 4, 'VAT Amount (BHD)', design_formats['bold_center'])
        worksheet.write(6, 5, 'Adjust /Apport (BHD)', design_formats['bold_center'])
        row = 8
        total_amount=0.000
        total_vat=0.000
        total_adjust=0.000
        tax_list=[]
        move_line_pool = self.env['account.move.line']
        tax_pool=self.env['account.tax'].search([('type_tax_use','=','sale')])
        for sale_tax in tax_pool:
            tax_list.append(sale_tax.id)
        starting_row = row
        # msg = 'Standard Rated Supplies sales'
        # sl_no = '1'
        # worksheet.write(row, 1, sl_no, design_formats['normal_format_central'])
        # worksheet.write(row, 2, msg, design_formats['normal_format'])
        lines = move_line_pool.search([ ('move_id.state','=','posted'),    
                                        ('date','>=',wizard.start_date),
                                        ('date','<=',wizard.end_date),
                                        ('journal_id.type','=','sale')
                                       ])
        
        # amount_diff_sales1=amount_diff_sales2 = 0.00
        # refund_tax=0.00
        # std_rate_tax=0.00
        # fixed_amt = 0.00
        # sale_fixed_amt = 0.00
        lines_list = []
        standard_vat_dict = {}
        for li in lines:
            # date = li.date.strftime('%d/%m/%Y')
            if li.tax_ids:
                for tax in li.tax_ids:
                    # tax_move_line = move_line_pool.search([ ('move_id.state','=','posted'),
                    #                     ('move_id','=',li.move_id.id),('tax_line_id','=',tax.id)
                    #                    ])
                    # print('============tax_move_line================',tax_move_line)
                    # debit_sum = 0.000
                    # credit_sum = 0.000
                    if tax.vat_report_type=='standard' and tax.id in tax_list:
                        key = tax.name
                        sql = """SELECT line.tax_line_id,COALESCE(SUM(line.debit-line.credit), 0)
                                FROM account_move_line line
                                JOIN account_journal journal ON journal.id = line.journal_id
                                JOIN account_move move ON line.move_id = move.id
                                WHERE line.date <= '%s' and line.date >= '%s'
                                AND journal.type = '%s'
                                AND line.tax_line_id = %s
                                AND move.state = '%s'
                                GROUP BY line.tax_line_id
                                """%(wizard.end_date,wizard.start_date,tax.type_tax_use,tax.id,'posted')
                        self.env.cr.execute(sql)
                        results = self.env.cr.fetchall()
                        if key in standard_vat_dict:
                            if li.name!='Discount':
                                if tax.amount_type == 'fixed':
                                    if 'sale_fixed_amt' in standard_vat_dict[key]:
                                        # sale_fixed_amt  += tax.amount
                                        standard_vat_dict[key]['sale_fixed_amt'] += tax.amount
                                    else:
                                        standard_vat_dict[key]['sale_fixed_amt'] = tax.amount
                                elif tax.amount_type == 'percent':
                                    if li.credit > 0.00:
                                        if 'amount_diff_sales1' in standard_vat_dict[key]:
                                            standard_vat_dict[key]['amount_diff_sales1'] += li.credit * (tax.amount/100)
                                        else:
                                            standard_vat_dict[key]['amount_diff_sales1'] = li.credit * (tax.amount/100)
                                        if 'std_rate_tax' in standard_vat_dict[key]:
                                            standard_vat_dict[key]['std_rate_tax'] += li.credit
                                        else:
                                            standard_vat_dict[key]['std_rate_tax'] = li.credit
                                    else:
                                        if 'amount_diff_sales2' in standard_vat_dict[key]:
                                            standard_vat_dict[key]['amount_diff_sales2'] += -(li.debit * (tax.amount/100))
                                        else:
                                            standard_vat_dict[key]['amount_diff_sales2'] = -(li.debit * (tax.amount/100))
                                        if 'refund_tax' in standard_vat_dict[key]:
                                            standard_vat_dict[key]['refund_tax'] += li.debit
                                        else:
                                            standard_vat_dict[key]['refund_tax'] = li.debit
                        else:
                            sale_fixed_amt = 0.00
                            amount_diff_sales1 = 0.00
                            std_rate_tax = 0.00
                            amount_diff_sales2 = 0.00
                            refund_tax = 0.00
                            vat_amount = 0.00
                            if tax.vat_report_type=='standard':
                                if li.name!='Discount':
                                    if tax.amount_type == 'fixed':
                                        sale_fixed_amt = tax.amount
                                    elif tax.amount_type == 'percent':
                                        if li.credit > 0.00:
                                            amount_diff_sales1 = li.credit * (tax.amount/100)
                                            std_rate_tax = li.credit
                                        else:
                                            amount_diff_sales2 = -(li.debit * (tax.amount/100))
                                            refund_tax = li.debit
                                        if results:
                                            for each in results:
                                                if tax.id == each[0]:
                                                    vat_amount = each[1]
                                standard_vat_dict.update({key:{'sale_fixed_amt':sale_fixed_amt,'vat_amount':vat_amount,'amount_diff_sales1':amount_diff_sales1,'std_rate_tax':std_rate_tax,'amount_diff_sales2':amount_diff_sales2,'refund_tax':refund_tax}})
                            
        
        # total_vat+=(amount_diff_sales1 + amount_diff_sales2)
        # total_amount+=(std_rate_tax- refund_tax)
        # total_adjust+= amount_diff_sales2
        # fixed_amt += sale_fixed_amt
        # print('======================amount_diff_sales1',amount_diff_sales1)
        # print('======================amount_diff_sales2',amount_diff_sales2)
        # print('======================sale_fixed_amt',sale_fixed_amt)
        
        msg = 'Standard Rated Supplies sales'
        sl_no = '1'
        # worksheet.write(row, 1, sl_no, design_formats['normal_format_central'])
        # worksheet.write(row, 2, msg, design_formats['normal_format'])
        alphabet_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        index = 0
        if standard_vat_dict:
            for key,value in standard_vat_dict.items():
                total_vat += value['amount_diff_sales1']+value['amount_diff_sales2']
                total_amount+=(value['std_rate_tax']- value['refund_tax'])
                total_adjust+= value['amount_diff_sales2']
                base_amt = value['std_rate_tax']- value['refund_tax']
                worksheet.write(row, 1, sl_no+'(%s)'%(alphabet_list[index]), design_formats['normal_format_central'])
                worksheet.write(row, 2, msg+' '+key, design_formats['normal_format'])
                worksheet.write(row, 3, base_amt, design_formats['amount_format'])
                if value['vat_amount']:
                    if base_amt > 0 and value['vat_amount'] < 0:
                        worksheet.write(row, 4, -(value['vat_amount']), design_formats['amount_format'])
                    elif base_amt > 0 and value['vat_amount'] > 0:
                        worksheet.write(row, 4, value['vat_amount'], design_formats['amount_format'])
                    elif base_amt < 0 and value['vat_amount'] > 0:
                        worksheet.write(row, 4, -(value['vat_amount']), design_formats['amount_format'])
                    else:
                        worksheet.write(row, 4, value['vat_amount'], design_formats['amount_format'])
                else:
                    worksheet.write(row, 4, value['sale_fixed_amt'], design_formats['amount_format'])
                worksheet.write(row, 5, value['amount_diff_sales2'], design_formats['amount_format'])
                index += 1
                row = row + 1
        else:
            worksheet.write(row, 1, sl_no, design_formats['normal_format_central'])
            worksheet.write(row, 2, msg, design_formats['normal_format'])
            worksheet.write(row, 3,0.00, design_formats['amount_format'])
            worksheet.write(row, 4, 0.00, design_formats['amount_format'])
            worksheet.write(row, 5, 0.00, design_formats['amount_format'])
            row = row + 1
        
        
        # worksheet.write(row, 3, std_rate_tax- refund_tax, design_formats['amount_format'])
        # worksheet.write(row, 4, (amount_diff_sales1 + amount_diff_sales2) if amount_diff_sales1 or amount_diff_sales2 else sale_fixed_amt, design_formats['amount_format'])
        # worksheet.write(row, 5, amount_diff_sales2, design_formats['amount_format'])
        # row = row + 1
         
        lines_zero = move_line_pool.search([
                                         ('move_id.state','=','posted'),
                                         ('date','>=',wizard.start_date),
                                         ('date','<=',wizard.end_date),
                                         ('journal_id.type','=','sale')
                                         ])
        
        zero_vat_dict = {}
        for li in lines_zero:
            if li.tax_ids:
                for vat in li.tax_ids:
                    if vat.vat_report_type=='zero':
                        key = vat.name
                        if key in zero_vat_dict:
                            if li.name!='Discount':
                                if li.credit>0.00:
                                    if 'amount_diff_zero' in zero_vat_dict[key]:
                                        zero_vat_dict[key]['amount_diff_zero'] += li.credit
                                    else:
                                        zero_vat_dict[key]['amount_diff_zero'] = li.credit
                                elif li.debit>0.00:
                                    if 'amount_diff_zero' in zero_vat_dict[key]:
                                        zero_vat_dict[key]['amount_diff_zero'] -= li.debit
                                    else:
                                        zero_vat_dict[key]['amount_diff_zero'] = li.debit
                                
                        else:
                            amount_diff_zero=0.00
                            zero_rate_amount=0.00
                            if vat.vat_report_type=='zero':
                                if li.name!='Discount':
                                    if li.credit>0.00:
                                        amount_diff_zero =li.credit
                                    elif li.debit>0.00:
                                        amount_diff_zero =li.debit
                                zero_vat_dict.update({key:{'amount_diff_zero':amount_diff_zero,'zero_rate_amount':zero_rate_amount}})
        
        
        
        sl_no = '2'
        index1 = 0
        if zero_vat_dict:
            for key,value in zero_vat_dict.items():
                total_vat += value['zero_rate_amount']
                total_amount+=value['amount_diff_zero']
                worksheet.write(row, 1, sl_no+'(%s)'%(alphabet_list[index1]), design_formats['normal_format_central'])
                worksheet.write(row, 2, 'Zero-rated domestic sales'+' '+key, design_formats['normal_format'])
                worksheet.write(row, 3, value['amount_diff_zero'], design_formats['amount_format'])
                worksheet.write(row, 4, value['zero_rate_amount'], design_formats['amount_format'])
                index1 += 1
                row = row + 1
        else:
            worksheet.write(row, 1, sl_no, design_formats['normal_format_central'])
            worksheet.write(row, 2, 'Zero-rated domestic sales', design_formats['normal_format'])
            worksheet.write(row, 3, 0.00, design_formats['amount_format'])
            worksheet.write(row, 4, 0.00, design_formats['amount_format'])
            row = row + 1
            
            
            
        exempt_vat_dict = {}
        for li in lines_zero:
            if li.tax_ids:
                for vat in li.tax_ids:
                    if vat.vat_report_type=='exempt':
                        key = vat.name
                        if key in exempt_vat_dict:
                            if li.name!='Discount':
                                if li.credit>0.00:
                                    if 'amount_exempt' in exempt_vat_dict[key]:
                                        exempt_vat_dict[key]['amount_exempt'] += li.credit
                                    else:
                                        exempt_vat_dict[key]['amount_exempt'] = li.credit
                                elif li.debit>0.00:
                                    if 'amount_exempt' in exempt_vat_dict[key]:
                                        exempt_vat_dict[key]['amount_exempt'] -= li.debit
                                    else:
                                        exempt_vat_dict[key]['amount_exempt'] = li.debit
                                
                        else:
                            amount_exempt=0.00
                            exempt_rate_amount=0.00
                            if vat.vat_report_type=='exempt':
                                if li.name!='Discount':
                                    if li.credit>0.00:
                                        amount_exempt =li.credit
                                    elif li.debit>0.00:
                                        amount_exempt =li.debit
                                exempt_vat_dict.update({key:{'amount_exempt':amount_exempt,'exempt_rate_amount':exempt_rate_amount}})
        
        
        
        sl_no = '3'
        index2 = 0
        if exempt_vat_dict:
            for key,value in exempt_vat_dict.items():
                total_vat += value['exempt_rate_amount']
                total_amount+=value['amount_exempt']
                worksheet.write(row, 1, sl_no+'(%s)'%(alphabet_list[index2]), design_formats['normal_format_central'])
                worksheet.write(row, 2, 'Exempt sales'+' '+key, design_formats['normal_format'])
                worksheet.write(row, 3, value['amount_exempt'], design_formats['amount_format'])
                worksheet.write(row, 4, value['exempt_rate_amount'], design_formats['amount_format'])
                index2 += 1
                row = row + 1
        else:
            worksheet.write(row, 1, sl_no, design_formats['normal_format_central'])
            worksheet.write(row, 2, 'Exempt sales', design_formats['normal_format'])
            worksheet.write(row, 3, 0.00, design_formats['amount_format'])
            worksheet.write(row, 4, 0.00, design_formats['amount_format'])
            index2 += 1
            row = row + 1
        
        
        # amount_diff_zero=0.00
        # zero_rate_amount=0.00
        # for li in lines_zero:
        #   for vat in li.tax_ids:
        #       if li.name != 'Discount':
        #         if vat.vat_report_type =='zero':
        #           if li.credit>0.00:
        #             amount_diff_zero +=li.credit
        #           elif li.debit>0.00:
        #             amount_diff_zero -=li.debit
        # total_amount+=amount_diff_zero
        # total_vat+=zero_rate_amount
        # worksheet.write(row, 1, 2, design_formats['normal_format_central'])
        # worksheet.write(row, 2, 'Zero-rated domestic sales', design_formats['normal_format'])
        # worksheet.write(row, 3, amount_diff_zero, design_formats['amount_format'])
        # worksheet.write(row, 4, zero_rate_amount, design_formats['amount_format'])
        # row = row + 1
        


        # amount_exempt=0.00
        # exempt_rate_amount=0.00
        # for li in lines_zero:
        #   for vat in li.tax_ids:
        #       if li.name != 'Discount':
        #         if vat.vat_report_type == 'exempt':
        #           if li.credit>0.00:
        #             amount_exempt +=li.credit
        #           elif li.debit>0.00:
        #             amount_exempt -=li.debit
        # total_amount+=amount_exempt
        # total_vat+=zero_rate_amount
        #
        # worksheet.write(row, 1, 3, design_formats['normal_format_central'])
        # worksheet.write(row, 2, 'Exempt sales', design_formats['normal_format'])
        # worksheet.write(row, 3, amount_exempt, design_formats['amount_format'])
        # worksheet.write(row, 4, zero_rate_amount, design_formats['amount_format'])
        # row = row + 1
        
        

        gcc_lines = move_line_pool.search([('date','>=',wizard.start_date),
                                       ('date','<=',wizard.end_date),
                                       ('journal_id.type','=','sale'),
#                                        ('account_id','=',tax[0][0].account_id.id),
                                       ('partner_id.country_id.gcc_vat','=',True),
                                       ('tax_line_id','!=',False)
                                       ])
        amount_diff_gcc=0.00
        refund_gcc_tax=0.00
        tax_amount=0.00
        for li in gcc_lines:
          if li.credit>0.00:
            amount_diff_gcc +=(li.credit*100)/li.tax_line_id.amount
            tax_amount += li.credit
          elif li.debit>0.00:
            amount_diff_gcc -=(li.debit*100)/li.tax_line_id.amount
            refund_gcc_tax +=li.debit
            tax_amount += li.debit
        total_amount+=amount_diff_gcc
        total_vat+=tax_amount
        total_adjust+= refund_gcc_tax
        worksheet.write(row, 1, 4, design_formats['normal_format_central'])
        worksheet.write(row, 2, 'Sales to registered taxpayers in other GCC states', design_formats['normal_format'])
        worksheet.write(row, 3, amount_diff_gcc, design_formats['amount_format'])
        worksheet.write(row, 4, tax_amount, design_formats['amount_format'])
        worksheet.write(row, 5, -refund_gcc_tax, design_formats['amount_format'])
        row = row + 1

        worksheet.write(row, 1, 5, design_formats['normal_format_central'])
        worksheet.write(row, 2, 'Total Sales', design_formats['bold'])
        worksheet.write(row, 3, total_amount, design_formats['normal_num_bold'])
        worksheet.write(row, 4, total_vat, design_formats['normal_num_bold'])
        worksheet.write(row, 5, total_adjust,design_formats['normal_num_bold'])
        row+=1
       

        tax_purchase=[]
        total_amount1=0.00
        total_vat1=0.00
        total_adjust1=0.00
        tax_pool1=self.env['account.tax'].search([('type_tax_use','=','purchase')])
        for purchase_tax in tax_pool1:
            tax_purchase.append(purchase_tax.id)
        
        purchase_lines = move_line_pool.search([
                                        ('move_id.state','=','posted'),
                                        ('date','>=',wizard.start_date),
                                         ('date','<=',wizard.end_date),
                                       ('journal_id.type','=','purchase'),
#                                        ('account_id','=',tax_purchase[0][0].account_id.id),
#                                        ('tax_line_id','!=',False)
                                       ])
        
        purchase_std_vat_dict = {}
        for li in purchase_lines:
            if li.tax_ids:
                for tax in li.tax_ids:
                    if tax.vat_report_type=='standard' and tax.id in tax_purchase:
                        key = tax.name
                        purchase_sql = """SELECT line.tax_line_id,COALESCE(SUM(line.debit-line.credit), 0)
                                FROM account_move_line line
                                JOIN account_journal journal ON journal.id = line.journal_id
                                JOIN account_move move ON line.move_id = move.id
                                WHERE line.date <= '%s' and line.date >= '%s'
                                AND journal.type = '%s'
                                AND line.tax_line_id = %s
                                AND move.state = '%s'
                                GROUP BY line.tax_line_id
                                """%(wizard.end_date,wizard.start_date,tax.type_tax_use,tax.id,'posted')
                        self.env.cr.execute(purchase_sql)
                        purchase_results = self.env.cr.fetchall()
                        if key in purchase_std_vat_dict:
                            if li.name!='Discount':
                                if tax.amount_type == 'fixed':
                                    if 'purchase_fixed_amt' in purchase_std_vat_dict[key]:
                                        # sale_fixed_amt  += tax.amount
                                        purchase_std_vat_dict[key]['purchase_fixed_amt'] += tax.amount
                                    else:
                                        purchase_std_vat_dict[key]['purchase_fixed_amt'] = tax.amount
                                elif tax.amount_type == 'percent':
                                    if li.debit > 0.00:
                                        if 'amount_diff1' in purchase_std_vat_dict[key]:
                                            # amount_diff_sales1 += li.credit * (tax.amount/100)
                                            purchase_std_vat_dict[key]['amount_diff1'] += li.debit * (tax.amount/100)
                                        else:
                                            purchase_std_vat_dict[key]['amount_diff1'] = li.debit * (tax.amount/100)
                                        if 'std_rate_tax_amount1' in purchase_std_vat_dict[key]:
                                            # std_rate_tax += li.credit
                                            purchase_std_vat_dict[key]['std_rate_tax_amount1'] += li.debit
                                        else:
                                            purchase_std_vat_dict[key]['std_rate_tax_amount1'] = li.debit
                                    else:
                                        if 'amount_diff2' in purchase_std_vat_dict[key]:
                                            # amount_diff_sales2 += -(li.debit * (tax.amount/100))
                                            purchase_std_vat_dict[key]['amount_diff2'] += -(li.credit * (tax.amount/100))
                                        else:
                                            purchase_std_vat_dict[key]['amount_diff2'] = -(li.credit * (tax.amount/100))
                                        if 'refund_tax' in purchase_std_vat_dict[key]:
                                            # refund_tax += li.debit
                                            purchase_std_vat_dict[key]['refund_tax'] += li.credit
                                        else:
                                            purchase_std_vat_dict[key]['refund_tax'] = li.credit
                        else:
                            purchase_fixed_amt = 0.00
                            amount_diff1 = 0.00
                            std_rate_tax_amount1 = 0.00
                            amount_diff2 = 0.00
                            refund_tax = 0.00
                            if tax.vat_report_type=='standard':
                                if li.name!='Discount':
                                    if tax.amount_type == 'fixed':
                                        purchase_fixed_amt = tax.amount
                                    elif tax.amount_type == 'percent':
                                        if li.debit > 0.00:
                                            amount_diff1 = li.debit * (tax.amount/100)
                                            std_rate_tax_amount1 = li.debit
                                        else:
                                            amount_diff2 = -(li.credit * (tax.amount/100))
                                            refund_tax = li.credit
                                        if purchase_results:
                                            for each in purchase_results:
                                                if tax.id == each[0]:
                                                    vat_amount = each[1]
                                purchase_std_vat_dict.update({key:{'purchase_fixed_amt':purchase_fixed_amt,'vat_amount':vat_amount,'amount_diff1':amount_diff1,'std_rate_tax_amount1':std_rate_tax_amount1,'amount_diff2':amount_diff2,'refund_tax':refund_tax}})
        
        
        # amount_diff1=amount_diff2 = 0.00
        # refund_tax1=0.00
        # std_rate_tax_amount1=0.00
        fixed_amt1 = 0.00
        # purchase_fixed_amt = 0.00
        # for li in purchase_lines:
        #     for tax in li.tax_ids:
        #         if tax.vat_report_type=='standard':
        #             if li.name!='Discount':
        #                 if tax.amount_type == 'fixed':
        #                     purchase_fixed_amt += tax.amount
        #                 elif tax.amount_type == 'percent':
        #                     if li.debit > 0.00:
        #                         amount_diff1 += li.debit * (tax.amount/100)
        #                         std_rate_tax_amount1 += li.debit
        #                     else:
        #                         amount_diff2 += -(li.credit * (tax.amount/100))
        #                         refund_tax1 += li.debit

        # total_amount1+=(std_rate_tax_amount1 - refund_tax1)
        # total_vat1+=(amount_diff1 + amount_diff2)
        # total_adjust1+= amount_diff2
        # fixed_amt1 += purchase_fixed_amt
        worksheet.write(row, 2, 'Purchases', design_formats['bold_center'])
        row = row + 1
        sl_purchase = '6'
        index3 = 0
        if purchase_std_vat_dict:
            for key,value in purchase_std_vat_dict.items():
                total_amount1+=(value['std_rate_tax_amount1'] - value['refund_tax'])
                total_vat1+=(value['amount_diff1'] + value['amount_diff2'])
                total_adjust1+= value['amount_diff2']
                fixed_amt1 += value['purchase_fixed_amt']
                purchase_base_amt = value['std_rate_tax_amount1']- value['refund_tax']
                worksheet.write(row, 1, sl_purchase+'(%s)'%(alphabet_list[index3]), design_formats['normal_format_central'])
                worksheet.write(row, 2, 'Standard rated Expenses'+' '+key, design_formats['normal_format'])
                worksheet.write(row, 3, purchase_base_amt, design_formats['amount_format'])
                if value['vat_amount']:
                    if purchase_base_amt > 0 and value['vat_amount'] < 0:
                        worksheet.write(row, 4, -(value['vat_amount']), design_formats['amount_format'])
                    elif purchase_base_amt > 0 and value['vat_amount'] > 0:
                        worksheet.write(row, 4, value['vat_amount'], design_formats['amount_format'])
                    elif purchase_base_amt < 0 and value['vat_amount'] > 0:
                        worksheet.write(row, 4, -(value['vat_amount']), design_formats['amount_format'])
                    else:
                        worksheet.write(row, 4, value['vat_amount'], design_formats['amount_format'])
                else:
                    worksheet.write(row, 4, value['purchase_fixed_amt'], design_formats['amount_format'])
                
                # if value['amount_diff1'] or value['amount_diff2']:
                #     worksheet.write(row, 4, value['amount_diff1']+value['amount_diff2'], design_formats['amount_format'])
                # else:
                #     worksheet.write(row, 4, value['purchase_fixed_amt'], design_formats['amount_format'])
                # worksheet.write(row, 4, (amount_diff1 + amount_diff2) if amount_diff1 or amount_diff2 else purchase_fixed_amt, design_formats['amount_format'])
                worksheet.write(row, 5, value['amount_diff2'], design_formats['amount_format'])
                index3 += 1
                row = row + 1
        else:
            worksheet.write(row, 1, sl_purchase, design_formats['normal_format_central'])
            worksheet.write(row, 2, 'Standard rated Expenses', design_formats['normal_format'])
            worksheet.write(row, 3, 0.00, design_formats['amount_format'])
            worksheet.write(row, 4, 0.00, design_formats['amount_format'])
            # worksheet.write(row, 4, (amount_diff1 + amount_diff2) if amount_diff1 or amount_diff2 else purchase_fixed_amt, design_formats['amount_format'])
            worksheet.write(row, 5, 0.00, design_formats['amount_format'])
            row = row + 1

      
        purchase_lines_zero = move_line_pool.search([
                                        ('move_id.state','=','posted'),
                                        ('date','>=',wizard.start_date),
                                        ('date','<=',wizard.end_date),
                                        ('journal_id.type','=','purchase')
                                       ])
        # amount_diff_zero1=0.00
        # zero_rate_tax_invoice1=0.00
        amount_diff_exempt_purchase1 = amount_diff_exempt_purchase2 = 0.00
        amount_exempt_purchase = 0.00
        amount_exempt_refund_purchase = 0.00 

        
        purchase_zero_vat_dict = {}
        for li in purchase_lines_zero:
          for vat in li.tax_ids:
            if li.name != 'Discount':
                if vat.vat_report_type in ['zero','exempt']:
                    key = vat.name
                    if key in purchase_zero_vat_dict:
                        if li.name!='Discount':
                            if li.credit>0.00:
                                if 'amount_diff_zero1' in purchase_zero_vat_dict[key]:
                                    purchase_zero_vat_dict[key]['amount_diff_zero1'] -= li.credit
                                else:
                                    purchase_zero_vat_dict[key]['amount_diff_zero1'] = li.credit
                            elif li.debit>0.00:
                                if 'amount_diff_zero1' in purchase_zero_vat_dict[key]:
                                    purchase_zero_vat_dict[key]['amount_diff_zero1'] += li.debit
                                else:
                                    purchase_zero_vat_dict[key]['amount_diff_zero1'] = li.debit
                            
                    else:
                        amount_diff_zero1=0.00
                        zero_rate_tax_invoice1=0.00
                        if vat.vat_report_type in ['zero','exempt']:
                            if li.name!='Discount':
                                if li.credit>0.00:
                                    amount_diff_zero1 =li.credit
                                elif li.debit>0.00:
                                    amount_diff_zero1 +=li.debit
                            purchase_zero_vat_dict.update({key:{'amount_diff_zero1':amount_diff_zero1,'zero_rate_tax_invoice1':zero_rate_tax_invoice1}})
        
        
        sl_no = '7'
        index4 = 0
        if purchase_zero_vat_dict:
            for key,value in purchase_zero_vat_dict.items():
                total_vat1 += value['zero_rate_tax_invoice1']
                total_amount1+=value['amount_diff_zero1']
                worksheet.write(row, 1, sl_no+'(%s)'%(alphabet_list[index4]), design_formats['normal_format_central'])
                worksheet.write(row, 2, 'Purchases from non-registered suppliers, zero-rated purchases/exempt purchases'+' '+key, design_formats['normal_format'])
                worksheet.write(row, 3, value['amount_diff_zero1'], design_formats['amount_format'])
                worksheet.write(row, 4, value['zero_rate_tax_invoice1'], design_formats['amount_format'])
                index4 += 1
                row = row + 1
        else:
            worksheet.write(row, 1, sl_no, design_formats['normal_format_central'])
            worksheet.write(row, 2, 'Purchases from non-registered suppliers, zero-rated purchases/exempt purchases', design_formats['normal_format'])
            worksheet.write(row, 3, 0.00, design_formats['amount_format'])
            worksheet.write(row, 4, 0.00, design_formats['amount_format'])
        
        
        
        # for li in purchase_lines_zero:
        #   for vat in li.tax_ids:
        #     if li.name != 'Discount':
        #         if vat.vat_report_type in ['zero','exempt']:
        #           if li.credit>0.00:
        #             amount_diff_zero1 -=li.credit
        #           elif li.debit>0.00:
        #             amount_diff_zero1 +=li.debit
        #
        #
        # # total_amount1+=amount_diff_zero1
        # # total_vat1+=zero_rate_tax_invoice1
        #
        
        # worksheet.write(row, 2, 'Purchases from non-registered suppliers, zero-rated purchases/exempt purchases', design_formats['normal_format'])
        # worksheet.write(row, 3, amount_diff_zero1, design_formats['amount_format'])
        # worksheet.write(row, 4, zero_rate_tax_invoice1 , design_formats['amount_format'])

        row = row + 1
        worksheet.write(row, 1, 8, design_formats['normal_format_central'])
        worksheet.write(row, 2, 'Total purchases', design_formats['bold'])
        worksheet.write(row, 3, total_amount1, design_formats['normal_num_bold'])
        worksheet.write(row, 4, total_vat1, design_formats['normal_num_bold'])
        worksheet.write(row, 5, total_adjust1,design_formats['normal_num_bold'])
        row+=2

        worksheet.write(row, 2, 'Net VAT Due', design_formats['bold'])
        worksheet.write(row+1, 2, 'Total value of due tax for the period', design_formats['normal_format'])
        worksheet.write(row+1, 4,  total_vat, design_formats['amount_format'])
        worksheet.write(row+2, 2, 'Total value of recoverable tax for the period ', design_formats['normal_format'])
        worksheet.write(row+2, 4,  total_vat1, design_formats['amount_format'])
        worksheet.write(row+3, 2, 'Net VAT due(or reclaimed) for the period', design_formats['normal_format'])
        worksheet.write(row+3, 4,  (total_vat-total_vat1), design_formats['amount_format'])

VATReport()
