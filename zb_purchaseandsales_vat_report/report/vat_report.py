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

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract
from odoo import _, api, fields, models
from datetime import datetime
import math
import operator
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import collections

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)
class VATReport(models.AbstractModel):
    _name = 'report.zb_purchaseandsales_vat_report.report_vat.xlsx'    
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, wizard):
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        design_formats = {}
        design_formats['bold_center'] = workbook.add_format({'bold': True, 'font_name': 'Times New Roman', 
                                                      'size': 11,
                                                      'text_wrap': True,
                                                      'align': 'center'})
        design_formats['bold_center1'] = workbook.add_format({'bold': True, 'font_name': 'Times New Roman', 
                                                      'size': 15,
                                                      'text_wrap': True,
                                                      'align': 'center'})
        design_formats['date_format'] = workbook.add_format({'num_format': date_format, 
                                           'font_name': 'Times New Roman', 'size': 11,
                                           'align': 'center', 'text_wrap': True})
        design_formats['normal_format'] = workbook.add_format({'font_name': 'Times New Roman',
                                            'size': 11, 'text_wrap': True,'align': 'center'})
        design_formats['amount_format'] = workbook.add_format({'num_format': '#,##0.000', 
                                         'font_name': 'Times New Roman',
                                         'align' : 'center', 'size': 11, 'text_wrap': True})
        design_formats['float_rate_format'] = workbook.add_format({'num_format': '###0.000', 
                                         'font_name': 'Times New Roman',
                                         'align' : 'right', 'size': 11, 'text_wrap': True,'bold': True})
        ##FORMATS END##
        
        
        start_date = wizard.start_date
        end_date = wizard.end_date
        type = wizard.type
        
        params = {
            'start_date' : wizard.start_date, 
            'end_date' : wizard.end_date,
        }
        
        worksheet1 = workbook.add_worksheet("Purchase Register")
        worksheet2 = workbook.add_worksheet("Sales Register")
        #Title Of Sheet#
        user_id = self.env['res.users'].browse(self.env.uid)
        company_id = user_id.company_id
        company = str(user_id.company_id.name)
        worksheet1.set_column('A:A', 25)
        worksheet1.set_column('B:B', 15)
        worksheet1.set_column('C:C', 15)
        worksheet1.set_column('D:D', 20)
        worksheet1.set_column('E:E', 60)
        worksheet1.set_column('F:F', 25)
        worksheet1.set_column('G:G', 60)
        worksheet1.set_column('H:H', 25)
        worksheet1.set_column('I:J', 15)
        worksheet1.set_column('J:J', 15)
        
        worksheet2.set_column('A:A', 25)
        worksheet2.set_column('B:B', 15)
        worksheet2.set_column('C:C', 40)
        worksheet2.set_column('D:D', 25)
        worksheet2.set_column('E:E', 60)
        worksheet2.set_column('F:F', 25)
        worksheet2.set_column('G:G', 15)
        worksheet2.set_column('H:H', 15)
        
        
        worksheet1.write(2, 0, 'From: ' + datetime.strptime(str(wizard.start_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format), design_formats['date_format'])
        worksheet1.write(2, 1, 'To: ' + datetime.strptime(str(wizard.end_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format), design_formats['date_format'])
        worksheet1.set_row(5,25)
        worksheet1.write(5, 0, 'Bill Number.', design_formats['bold_center'])
        worksheet1.write(5, 1, 'Bill Date', design_formats['bold_center'])
        worksheet1.write(5, 2, 'Accounting Date', design_formats['bold_center'])
        worksheet1.write(5, 3, 'Reference', design_formats['bold_center'])
        worksheet1.write(5, 4, 'Supplier Name', design_formats['bold_center'])
        worksheet1.write(5, 5, 'VAT Account Number', design_formats['bold_center'])
        worksheet1.write(5, 6, 'Purchase Description', design_formats['bold_center'])
        worksheet1.write(5, 7, 'Purchase Value', design_formats['bold_center'])
        worksheet1.write(5, 8, 'VAT Amount Paid', design_formats['bold_center'])
        worksheet1.write(5, 9, 'VAT', design_formats['bold_center'])
        row1 = 7
        worksheet2.write(2, 0, 'From: ' + datetime.strptime(str(wizard.start_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format), design_formats['date_format'])
        worksheet2.write(2, 1, 'To: ' + datetime.strptime(str(wizard.end_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format), design_formats['date_format'])
        worksheet2.set_row(5,25)
        worksheet2.write(5, 0, 'Invoice Number.', design_formats['bold_center'])
        worksheet2.write(5, 1, 'Invoice Date', design_formats['bold_center'])
        worksheet2.write(5, 2, 'Customer Name', design_formats['bold_center'])
        worksheet2.write(5, 3, 'VAT Account Number', design_formats['bold_center'])
        worksheet2.write(5, 4, 'Sales Description', design_formats['bold_center'])
        worksheet2.write(5, 5, 'Sales Value(Exclusive Of VAT)', design_formats['bold_center'])
        worksheet2.write(5, 6, 'VAT Amount', design_formats['bold_center'])
        worksheet2.write(5, 7, 'VAT', design_formats['bold_center'])
        row2 =7
            
        move_line_obj = self.env['account.move.line']
#         voucher_obj = self.env['account.voucher']
#         invoice_tax_obj = self.env['account.invoice.tax']
        account_tax_purchase_obj = self.env['account.tax'].search([('type_tax_use','=','purchase')])
        account_tax_sale_obj = self.env['account.tax'].search([('type_tax_use','=','sale')])
        
        sale_move = move_line_obj.search([
                                        # ('partner_id.state_id','=',states.id),
                                        ('move_id.state','=','posted'),
                                        ('date','>=',wizard.start_date),
                                        ('date','<=',wizard.end_date),
                                        ('journal_id.type','=','sale')
                                        ])
        vals = []
        sale_dict = {}
        ret_dict = {}
        sale_amt = 0.00
        sale_vat = 0.00
        for sale in sale_move:
            if sale.tax_ids:
                sale_fixed_amt = 0.00
                sale_percent_amt = 0.00
                for tax in sale.tax_ids:
                    if tax.type_tax_use == 'sale':
                        if sale.name!='Discount':
                            if tax.amount_type == 'fixed':
                                sale_fixed_amt = tax.amount
                            elif tax.amount_type == 'percent':
                                if sale.credit > 0.00:
        #                             if sale.label == 'Discount':
                                    sale_percent_amt = sale.credit * (tax.amount/100)
                                else:
                                    sale_percent_amt = -(sale.debit * (tax.amount/100))
    #                     sale_base_amount = (sale.credit*100)/sale.tax_line_id.amount
                            vals = {
                                'invoice_number':sale.move_id.name,
                                'invoice_date':sale.move_id.invoice_date if sale.move_id.invoice_date else sale.move_id.date,
                                'partner':sale.partner_id.name,
                                'tax':sale.move_id.partner_id.vat,
                                'description': sale.name,
                                'total':sale.credit if sale.credit else sale.debit,
                                'vat':sale_percent_amt if sale_percent_amt else sale_fixed_amt,
                                'vat_name':tax.name
                            }
                            if vals['vat'] >= 0.00:
                                if not tax.vat_report_type in sale_dict:
                                        sale_dict.update({
                                            tax.vat_report_type:[vals]
                                            })
                                else:
                                    sale_dict[tax.vat_report_type].append(vals)
                            elif vals['vat'] < 0.00:
                                if not tax.vat_report_type in ret_dict:
                                        ret_dict.update({
                                            tax.vat_report_type:[vals]
                                            })
                                else:
                                    ret_dict[tax.vat_report_type].append(vals)
                            

        if sale_dict:
            worksheet2.write(row2,0 ,'Sales',design_formats['bold_center1'])
            row2 += 1       
            for key in sale_dict.items():
                if key[0] == 'standard':
                    worksheet2.write(row2,0 ,'Standard Related Sales',design_formats['bold_center'])
                    row2+=1
                else:
                    if key[0] == 'zero':
                        worksheet2.write(row2,0 ,'Zero Rated Sales',design_formats['bold_center'])
                        row2+=1
                worksheet2.set_row(row2,25)
                total = 0
                vat = 0
                for vals in sorted(key[1],key = lambda l : l['invoice_date']):
                    total += vals['total']
                    vat += vals['vat']
                    worksheet2.write(row2, 0,vals['invoice_number'],design_formats['normal_format'])
                    worksheet2.write(row2, 1,datetime.strptime(str(vals['invoice_date']),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),design_formats['normal_format'])
                    if vals['partner']:
                        worksheet2.write(row2, 2,vals['partner'],design_formats['normal_format'])
                    else:
                        worksheet2.write(row2, 2,' ',design_formats['normal_format'])
                    if vals['tax']:
                        worksheet2.write(row2, 3, vals['tax'],design_formats['normal_format'])
                    else:
                        worksheet2.write(row2, 3, '',design_formats['normal_format'])
                    if vals['description']:
                        worksheet2.write(row2, 4, vals['description'],design_formats['normal_format'])
                    else:
                        worksheet2.write(row2, 4, '' ,design_formats['normal_format'])
                    worksheet2.write(row2, 5, vals['total'],design_formats['amount_format'])
                    worksheet2.write(row2, 6, vals['vat'],design_formats['amount_format'])
                    worksheet2.write(row2, 7, vals['vat_name'],design_formats['normal_format'])
                    row2+=1
                    worksheet2.set_row(row2,25)
                worksheet2.set_row(row2,25)
                worksheet2.write(row2, 5, total ,design_formats['float_rate_format'])
                worksheet2.write(row2, 6, vat ,design_formats['float_rate_format'])
                row2 +=1
        
        row2 +=2
        if ret_dict:
            worksheet2.write(row2,0 ,'Return Sales',design_formats['bold_center1'])
            row2 += 1
            for key in ret_dict.items():
                if key[0] == 'standard':
                    worksheet2.write(row2,0 ,'Standard Related Sales',design_formats['bold_center'])
                    row2+=1
                else:
                    if key[0] == 'zero':
                        worksheet2.write(row2,0 ,'Zero Rated Sales',design_formats['bold_center'])
                    row2+=1
                worksheet2.set_row(row2,25)
                total = 0
                vat = 0
                for vals in sorted(key[1],key = lambda l : l['invoice_date']):
                    total += -vals['total']
                    vat += vals['vat']
                    worksheet2.write(row2, 0,vals['invoice_number'],design_formats['normal_format'])
                    worksheet2.write(row2, 1,datetime.strptime(str(vals['invoice_date']),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),design_formats['normal_format'])
                    if vals['partner']:
                        worksheet2.write(row2, 2,vals['partner'],design_formats['normal_format'])
                    else:
                        worksheet2.write(row2, 2,' ',design_formats['normal_format'])
                    if vals['tax']:
                        worksheet2.write(row2, 3, vals['tax'],design_formats['normal_format'])
                    else:
                        worksheet2.write(row2, 3, '',design_formats['normal_format'])
                    if vals['description']:
                        worksheet2.write(row2, 4, vals['description'],design_formats['normal_format'])
                    else:
                        worksheet2.write(row2, 4, '' ,design_formats['normal_format'])
                    worksheet2.write(row2, 5, -vals['total'],design_formats['amount_format'])
                    worksheet2.write(row2, 6, vals['vat'],design_formats['amount_format'])
                    worksheet2.write(row2, 7, vals['vat_name'],design_formats['normal_format'])
                    row2+=1
                    worksheet2.set_row(row2,25)
        #                 row2 +=1
                worksheet2.set_row(row2,25)
                worksheet2.write(row2, 5, total ,design_formats['float_rate_format'])
                worksheet2.write(row2, 6, vat ,design_formats['float_rate_format'])
                row2 +=1
                 
        purchase_move = move_line_obj.search([
                                               # ('partner_id.state_id','=',states.id),
                                                ('move_id.state','=','posted'),
                                                ('date','>=',wizard.start_date),
                                                ('date','<=',wizard.end_date),
                                                ('journal_id.type','=','purchase'),
                                                ])
        
        purchase_vals = []
        purchase_dict = {}
        ret_purchase_dict = {}
        purchase_amt = 0.00
        purchase_vat = 0.00
        for purchase in purchase_move:
            if purchase.tax_ids:
                fixed_amt = 0.00
                percent_amt = 0.00
                for tax in purchase.tax_ids:
                    if tax.type_tax_use == 'purchase':
                        if purchase.name!='Discount':
                            if tax.amount_type == 'fixed':
                                fixed_amt = tax.amount
                            elif tax.amount_type == 'percent':
                                if purchase.debit > 0.00:
                                    percent_amt = purchase.debit * (tax.amount/100)
                                else:
                                    percent_amt = -(purchase.credit * (tax.amount/100))
    #                     sale_base_amount = (sale.credit*100)/sale.tax_line_id.amount
                            purchase_vals = {
                                'invoice_number':purchase.move_id.name,
                                'invoice_date':purchase.move_id.invoice_date if purchase.move_id.invoice_date else purchase.move_id.date,
                                'partner':purchase.partner_id.name,
                                'tax':purchase.move_id.partner_id.vat,
                                'description': purchase.name,
                                'total':purchase.debit if purchase.debit else purchase.credit,
                                'vat': percent_amt if percent_amt else fixed_amt,
                                'vat_name':tax.name,
                                'accounting_date':purchase.move_id.date,
                                'ref':purchase.move_id.ref or ''
                            }
                            if purchase_vals['vat'] >= 0.00:
                                if not tax.vat_report_type in purchase_dict:
                                        purchase_dict.update({
                                            tax.vat_report_type:[purchase_vals]
                                            })
                                else:
                                    purchase_dict[tax.vat_report_type].append(purchase_vals)
                            elif purchase_vals['vat'] < 0.00:
                                if not tax.vat_report_type in ret_purchase_dict:
                                        ret_purchase_dict.update({
                                            tax.vat_report_type:[purchase_vals]
                                            })
                                else:
                                    ret_purchase_dict[tax.vat_report_type].append(purchase_vals)
        if purchase_dict:
            worksheet1.write(row1,0 ,'Purchases',design_formats['bold_center1'])
            row1 += 1                   
            for key in purchase_dict.items():
                if key[0] == 'standard':
                    worksheet1.write(row1,0 ,'Standard Related Purchases',design_formats['bold_center'])
                    row1+=1
                else:
                    if key[0] == 'zero':
                        worksheet1.write(row1,0 ,'Zero Rated Purchases',design_formats['bold_center'])
                        row1+=1
                worksheet1.set_row(row1,25)
                total = 0
                vat = 0
                for vals in sorted(key[1],key = lambda l : l['invoice_date']):
                    total += -vals['total']
                    vat += vals['vat']
                    worksheet1.write(row1, 0,vals['invoice_number'],design_formats['normal_format'])
                    worksheet1.write(row1, 1,datetime.strptime(str(vals['invoice_date']),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),design_formats['normal_format'])
                    worksheet1.write(row1, 2,datetime.strptime(str(vals['accounting_date']),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),design_formats['normal_format'])
                    worksheet1.write(row1, 3,vals['ref'],design_formats['normal_format'])
                    if vals['partner']:
                        worksheet1.write(row1, 4,vals['partner'],design_formats['normal_format'])
                    else:
                        worksheet1.write(row1, 4,'',design_formats['normal_format'])
                    if vals['tax']:
                        worksheet1.write(row1, 5, vals['tax'],design_formats['normal_format'])
                    else:
                        worksheet1.write(row1, 5, '',design_formats['normal_format'])
                    if vals['description']:
                        worksheet1.write(row1, 6, vals['description'],design_formats['normal_format'])
                    else:
                        worksheet1.write(row1, 6, '' ,design_formats['normal_format'])
                    worksheet1.write(row1, 7, vals['total'],design_formats['amount_format'])
                    worksheet1.write(row1, 8, vals['vat'],design_formats['amount_format'])
                    worksheet1.write(row1, 9, vals['vat_name'] or '',design_formats['normal_format'])
                    row1+=1
                    worksheet1.set_row(row1,25)
    #                 row1 +=1
                worksheet1.set_row(row1,25)
                worksheet1.write(row1, 5, total ,design_formats['float_rate_format'])
                worksheet1.write(row1, 6, vat ,design_formats['float_rate_format'])
                row1+=1
        row1 +=2
        if ret_purchase_dict:
            worksheet1.write(row1,0 ,'Return Purchases',design_formats['bold_center1'])
            row1 += 1
            for key in ret_purchase_dict.items():
                if key[0] == 'standard':
                    worksheet1.write(row1,0 ,'Standard Related Purchases',design_formats['bold_center'])
                    row1+=1
                else:
                    if key[0] == 'zero':
                        worksheet1.write(row1,0 ,'Zero Rated Purchases',design_formats['bold_center'])
                    row1+=1
                worksheet1.set_row(row1,25)
                total = 0
                vat = 0
                vat_dict = {}
                for vals in sorted(key[1],key = lambda l : l['invoice_date']):
                    total += -vals['total']
                    vat += vals['vat']
                    worksheet1.write(row1, 0,vals['invoice_number'],design_formats['normal_format'])
                    worksheet1.write(row1, 1,datetime.strptime(str(vals['invoice_date']),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),design_formats['normal_format'])
                    worksheet1.write(row1, 2,datetime.strptime(str(vals['accounting_date']),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),design_formats['normal_format'])
                    worksheet1.write(row1, 3,vals['ref'],design_formats['normal_format'])
                    if vals['partner']:
                        worksheet1.write(row1, 4,vals['partner'],design_formats['normal_format'])
                    else:
                        worksheet1.write(row1, 4,'',design_formats['normal_format'])
                    if vals['tax']:
                        worksheet1.write(row1, 5, vals['tax'],design_formats['normal_format'])
                    else:
                        worksheet1.write(row1, 5, '',design_formats['normal_format'])
                    if vals['description']:
                        worksheet1.write(row1, 6, vals['description'],design_formats['normal_format'])
                    else:
                        worksheet1.write(row1, 6, '' ,design_formats['normal_format'])
                    worksheet1.write(row1, 7, -vals['total'],design_formats['amount_format'])
                    worksheet1.write(row1, 8, vals['vat'],design_formats['amount_format'])
                    worksheet1.write(row1, 9, vals['vat_name'] or '',design_formats['normal_format'])
                    row1+=1
                    worksheet1.set_row(row1,25)
        #                 row2 +=1
                worksheet1.set_row(row1,25)
                worksheet1.write(row1, 7, total ,design_formats['float_rate_format'])
                worksheet1.write(row1, 8, vat ,design_formats['float_rate_format'])
                row1 +=1
#         
VATReport()       
# VATReport('report.report.vat.xlsx','wizard.vat.report')