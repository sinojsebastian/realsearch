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

# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract
from odoo import models
from datetime import datetime
import math
import operator
import collections

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)

class ReconciliationReport(models.AbstractModel):
    _name = 'report.zb_bank_reconcilation.reconcilation_report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, obj): 
        
        
        heading_format = workbook.add_format({'align': 'centre','valign': 'vcenter', 'bold': True, 'size': 12,'border':1})
        sub_heading_format = workbook.add_format({'align': 'center','valign': 'vcenter', 'bold': True, 'size': 10,'num_format': '#,###0.000'})
        sub_heading_format1 = workbook.add_format({'align': 'center','valign': 'vcenter','bold': True, 'size': 10,'num_format': '#,###0'})
        label_format = workbook.add_format({'bold': True,'align': 'center','size': 8, 'text_wrap': True})
        data_format2 = workbook.add_format({'bold': False,'align': 'center','size': 8, 'num_format': '#,###0.000','text_wrap':True})
        text_format2 = workbook.add_format({'bold': False,'align': 'center','size': 8, 'text_wrap':True})
        number_format =workbook.add_format({'bold': False,'align': 'right','size': 8, 'num_format': '#,###0.000'})
        worksheet = workbook.add_worksheet('Bank Reconciliation Report')
        
        start_date_new = ''
        date_to_new = ''
        if obj.from_date:
            date_start = datetime.strptime(str(obj.from_date), '%Y-%m-%d')
            start_date_new = date_start.date()
            start_date_new = start_date_new.strftime("%d/%m/%Y")
        if obj.to_date:
            date_to = datetime.strptime(str(obj.to_date), '%Y-%m-%d')
            date_to_new = date_to.date()
            date_to_new = date_to_new.strftime("%d/%m/%Y")
        
        
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 25)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 12)
        
        worksheet.merge_range('A1:I2','Bank Reconciliation',heading_format)
        worksheet.merge_range('A3:I3','%s'%(self.env.user.company_id.name),sub_heading_format)
        worksheet.write(3,0,obj.name, sub_heading_format)
        journal_id = obj.journal_id.name
        worksheet.write(4,0,'Journal', sub_heading_format)
        worksheet.write(4,1,journal_id, data_format2)
        worksheet.write(4,4,'BNK Balance', sub_heading_format)
        worksheet.write(4,5,obj.closing_balance_stmt, number_format)
        
        worksheet.set_row(5, 20)
        worksheet.write(5,0,'Account', sub_heading_format)
        account_id = obj.bank_account_id.name
        worksheet.write(5,1,account_id, data_format2)
        
        worksheet.write(6,0,'Date From', sub_heading_format)
        worksheet.write(6,1,start_date_new, data_format2)
        
        
        worksheet.write(5,4,'Debit', sub_heading_format)
        worksheet.write(5,5,obj.debit, number_format)
        
        worksheet.write(6,4,'Credit', sub_heading_format)
        worksheet.write(6,5,obj.credit, number_format)
        
        worksheet.write(7,0,'Date To', sub_heading_format)
        worksheet.write(7,1,date_to_new, data_format2)
        
        worksheet.write(7,4,'GL Closing Balance', sub_heading_format)
        worksheet.write(7,5,obj.closing_balance, number_format)
        
        worksheet.write(8,4,'Difference', sub_heading_format)
        worksheet.write(8,5,obj.difference, number_format)
        
        
        worksheet.set_row(10, 20)
        worksheet.write(10,0, 'Date',label_format)
        worksheet.write(10,1, 'Document No',label_format)
        worksheet.write(10,2, 'Partner',label_format)
        worksheet.write(10,3, 'Cheque No',label_format)
        worksheet.write(10,4, 'Ref',label_format)
        worksheet.write(10,5, 'Debit',label_format)
        worksheet.write(10,6, 'Credit',label_format)
        worksheet.write(10,7, 'Reconciled',label_format)
        worksheet.write(10,8, 'Reconciled Date',label_format)
        row=11
        for lines in obj.reconcileline_ids:
            worksheet.set_row(row, 20)
            date = ''
            if lines.date:
                date1 = datetime.strptime(str(lines.date), '%Y-%m-%d').date()
                date =  date1.strftime("%d/%m/%Y")
            worksheet.write(row, 0,date,data_format2)
            worksheet.write(row, 1,lines.document_no,text_format2)
            if lines.partner_id:
                partner =lines.partner_id.name
            else:
                partner =' '    
            worksheet.write(row, 2,partner,text_format2)
            if lines.cheque_no:
                cheque =lines.cheque_no
            else:
                cheque =' '   
            worksheet.write(row, 3,cheque,text_format2) 
            worksheet.write(row, 4,lines.reference,text_format2)
            worksheet.write(row, 5,lines.debit,number_format)
            worksheet.write(row, 6,lines.credit,number_format)
            if lines.reconciled ==False:
                value =' '                
            else:
                value ='X' 
            if lines.rec_date:
                rec_date1 = datetime.strptime(str(lines.rec_date), '%Y-%m-%d').date()
                rec_date = rec_date1.strftime("%d/%m/%Y")
            else:
                rec_date =' '        
            worksheet.write(row, 7,value,data_format2)
            worksheet.write(row, 8,rec_date,data_format2)

            row = row + 1

        
       
        
 
 
 
 
# ReconciliationReport('report.reconciliation_report','bank.reconciliation')

