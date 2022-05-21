from collections import Counter,deque
from itertools import groupby
from datetime import datetime, timedelta,date
from odoo import tools
import calendar
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from operator import inv
from odoo import _, api, fields, models
from xlsxwriter import worksheet
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class SellablesReport(models.AbstractModel):
    _name = 'report.zb_building_management.sellable_report.xlsx'
    _description = 'Sellable Report'

    _inherit = 'report.report_xlsx.abstract'
    
    
    
    def generate_xlsx_report(self, workbook, data,objs):
       
        worksheet = workbook.add_worksheet('sellable_report.xlsx')
        title1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                  'bold': True, 'size': 18,})
        title1.set_font_color('#CD0000')
        boldz = workbook.add_format({'bold': True,'align': 'left','border':1})
        boldz.set_bg_color('#F5F500')
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,##0.000','bg_color':'#CD0000','border':2,'align': 'center', 'valign': 'vcenter'})
        normal_num_bold.set_font_color('#ffffff')
        
        normal_num_bold2 = workbook.add_format({'bold': True, 'num_format': '#,##0.000','bg_color':'#18D41E','border':2,'align': 'center', 'valign': 'vcenter'})
        normal_num_bold.set_font_color('#ffffff')
        
        
        bold = workbook.add_format({'bold': True,'align': 'center','border':1})
        bold.set_text_wrap()
        
        bold3 = workbook.add_format({'bold': True,'align': 'center', 'border':2,})
        bold3.set_text_wrap()
        
        bold65 = workbook.add_format({'align': 'center'})
        bold65.set_text_wrap()
        
        bold82 = workbook.add_format({'align': 'center','bold': True})
        bold82.set_text_wrap()
        
        bold31 = workbook.add_format({'bold': True,'align': 'center', 'border':2,'valign': 'vcenter','bg_color':'#cbdabd'})
        bold31.set_text_wrap()
        
       
        bold32 = workbook.add_format({'bold': True,'align': 'center', 'border':2,'valign': 'vcenter','bg_color':'#FFE287'})
        bold32.set_text_wrap()
        
        bold4 = workbook.add_format({'bold': True,'align': 'center','valign': 'vcenter', 'border':2,})
        bold4.set_text_wrap()
       
        wrap= workbook.add_format({'align': 'center','num_format': '#,##0.000'})
        wrap.set_text_wrap()
       
        wrap1= workbook.add_format({'align': 'center','border':1})
        wrap1.set_text_wrap()
        
        wrapc= workbook.add_format({'align': 'center','num_format': '#,##0.000','bg_color':'#cbdabd','border':1})
        wrapc.set_text_wrap()
        
        wrapd= workbook.add_format({'align': 'center','num_format': 'dd/mm/yyyy'})
        wrapd.set_text_wrap()
        wrap2= workbook.add_format({'align': 'center','bg_color': '#CD0000','border':1,'num_format': '#,##0.000'})
        wrap2.set_text_wrap()
        
        wrap2p= workbook.add_format({'align': 'center','bg_color': '#43C447','border':1,'num_format': '#,##0.000'})
        wrap2p.set_text_wrap()
        
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 5)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('P:P', 15)
        worksheet.set_column('Q:Q', 15)
        worksheet.set_column('R:R', 15)
        worksheet.set_column('S:S', 15)
        worksheet.set_column('T:T', 15)
        worksheet.set_column('U:U', 15)
        worksheet.set_column('V:V', 15)
        worksheet.set_column('W:W', 20)
        worksheet.set_column('X:X', 20)
        worksheet.set_column('Y:Y', 30)
        worksheet.set_row(8, 35)
        
        
        cmpny = self.env.user.company_id
        title = cmpny.name + ' - PAYMENTS'
        
        worksheet.write('R4', 'PAID',bold3)
        worksheet.write('R5','Total Sold ',bold3)
        worksheet.write('T4','PAYMENTS DUE',bold3)
        worksheet.write('T5','Total Booked',bold3)
        worksheet.merge_range('V4:V5', 'Admin Fees paid ',bold3)
        worksheet.merge_range('D3:P6', title,title1)
#         worksheet.merge_range('R6:U6', 'Note: Total Paid does not include contract registration fee of 70 BHD',boldz)
        
#         worksheet.write('B7', 'Building',bold82)
        worksheet.write('A9', 'S/n',bold31)
        worksheet.write('B9', 'Unit No.',bold31)
        worksheet.write('C9', 'Floor',bold31)
        worksheet.write('D9', 'Type',bold31)
        worksheet.write('E9', 'Size sqm',bold31)
        worksheet.write('F9', 'Client Name',bold31)
        worksheet.write('G9', 'Date',bold31)
        worksheet.write('H9', 'Contract Registration Fee',bold31)
        worksheet.write('I9', 'Booking Fees ',bold31)
        worksheet.write('J9', 'Downpayment Fee',bold31)
        
        
        worksheet.write('K9', '1st ',bold32)
        worksheet.write('L9', '2nd',bold32)
        worksheet.write('M9', '3rd',bold32)
        worksheet.write('N9', '4th',bold32)
        worksheet.write('O9', '5th',bold32)
        worksheet.write('P9', '6th',bold32)
        worksheet.write('Q9', '7th',bold32)
        worksheet.write('R9', '8th',bold32)
        worksheet.write('S9', 'Final Payment',bold32)
        worksheet.write('T9', 'Total Invoiced ',bold31)
        worksheet.write('U9', 'Total Paid ',bold31)
        worksheet.write('V9', 'Total Balance (Unit price - Total Paid) ',bold31)
        worksheet.write('W9', 'Contract Unit Price ',bold31)
       
        worksheet.write('X9', 'Status',bold31)
        worksheet.write('Y9', 'Contact Details ',bold31)
        worksheet.write('Z9', 'Country ',bold31)
        sellable_units = self.env['zbbm.unit'].search([('state','in',['book','contract','sold']),('building_id.id','=',objs.building_id.id)])
        print(len(sellable_units))
       
        worksheet.merge_range('B7:C7','Building',bold82)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++',objs.building_id.name)
        

        worksheet.merge_range('D7:F7',objs.building_id.name,bold82)
        
        row = 8
        column = 0
        m = 1
        sold =0
        book =0
        cotract = 0
        for units in sellable_units:
            if units.state in ['contract','sold']:
                sold +=1
                
            else:
                book+=1    
            state = dict(units.fields_get(allfields=['state'])['state']['selection'])[units.state]
            
            worksheet.write(row+m, column,m or '',wrap1)
            worksheet.write(row+m, column+1,units.name or '',wrap)
            worksheet.write(row+m, column+2,units.floor,bold65)
            worksheet.write(row+m, column+3,units.bedroom.name or '',wrap)
            worksheet.write(row+m, column+4,units.total_area or '',wrap)
            worksheet.write(row+m, column+5,units.buyer_id.name or '',wrap)
            worksheet.write(row+m, column+6,units.contract_date or '',wrapd)
            
            if units.state in ['contract','sold']:
                worksheet.write(row+m, column+7,units.cont_prepa_fee ,wrap2p)
                cotract += units.cont_prepa_fee
            else:
                worksheet.write(row+m, column+7,units.cont_prepa_fee ,wrap)
            inst =[]
            for installment in units.installment_ids:
                inst.append(installment)
            for i in range(len(inst)):    
                if inst[i].fee_for != 'final':
                    if units.state in ['contract','sold'] and inst[i].amount > 0:
                        if inst[i].fee_for != 'installment':
                            if inst[i].state != 'Paid':
                                worksheet.write(row+m, column+8+i,inst[i].amount or '',wrap2)
                            else:
                                worksheet.write(row+m, column+8+i,inst[i].amount or '',wrap2p)
                        else:
                            if inst[i].state != 'Paid':
                                worksheet.write(row+m, column+8+i,inst[i].amount or '',wrap)
                            else:
                                worksheet.write(row+m, column+8+i,inst[i].amount or '',wrap2p)
                    else:
                        if inst[i].state != 'Paid':
                            worksheet.write(row+m, column+8+i,inst[i].amount or '',wrap)
                        else:
                            worksheet.write(row+m, column+8+i,inst[i].amount or '',wrap2p)
                else:
                    worksheet.write(row+m, column+18,inst[i].amount or '',wrap)    
                
            worksheet.write(row+m, column+19,units.invoice_total or '',wrapc)
            worksheet.write(row+m, column+20,units.payment_total or '',wrapc)
            worksheet.write(row+m, column+21,units.price - units.payment_total  or '',wrapc)
            worksheet.write(row+m, column+22,units.price or '',wrapc)
            
            if units.state in ['contract','sold']:
                worksheet.write(row+m, column+23,state or '',wrap2)
            else:
                worksheet.write(row+m, column+23,state or '',wrapc)
            worksheet.write(row+m, column+24,units.buyer_id.phone or '',wrap)
            worksheet.write(row+m, column+25,units.buyer_id.nationality.name or '',wrap)
            worksheet.write_formula('S4', '{=SUM(U10:U%s)}'%(str(row+m+1)),normal_num_bold2)
            worksheet.write_formula('U4', '{=SUM(V10:V%s)}'%(str(row+m+1)),normal_num_bold)
            worksheet.write('S5', sold,bold4)
            worksheet.write('U5', book,bold4)
#             worksheet.merge_range('W4:W5', sold*(units.building_id.cont_preparation_fee),normal_num_bold)
            
            m+=1
        worksheet.merge_range('W4:W5', cotract,normal_num_bold)
#             worksheet.write(row+m, column,m or '')
#             worksheet.write(row+m, column,m or '')
            
            
        
        
        
        
        
        
        
        
        
        



SellablesReport()        