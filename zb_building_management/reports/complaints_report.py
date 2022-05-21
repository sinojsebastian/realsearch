from collections import Counter,deque
from itertools import groupby
from datetime import datetime, timedelta,date
from odoo import tools
import calendar
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from operator import inv
from odoo import _, api, fields, models
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class ComplaintsReport(models.AbstractModel):
    _name = 'report.zb_building_management.complaintsreport.xlsx'
    _description = 'Complaints Report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data,objs):
       
        worksheet = workbook.add_worksheet('complaints_report.xlsx')
#         worksheet.set_default_column(8)
#         worksheet.set_default_column(hide_unused_columns=True)
        bold = workbook.add_format({'bold': True})
        bold3 = workbook.add_format({'bold': True})
        bold3.set_bg_color('#000000')
        bold1 = workbook.add_format({'align': 'center'})
        bold.set_bg_color('#C0C0C0')
        pro = workbook.add_format({'bold': True,'align': 'center'})
        pro.set_bg_color('#008000')
        pro.set_font_color('#FFFFFF')
        los = workbook.add_format({'bold': True,'align': 'center'})
        los.set_bg_color('#FF0000')
        los.set_font_color('#FFFFFF')
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        no_format = workbook.add_format({'num_format': '#,##0.00'})
        cell_number_format = workbook.add_format({'align': 'right',
                                                  'valign': 'vcenter',
                                                  'bold': False, 'size': 12,
                                                  'num_format': '#,##0.00'})
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,##0.00'})
        
        
        format = workbook.add_format({'bold': True,'size': 12,'align': 'center'})
        format.set_bg_color('#0000FF')
        format.set_font_color('#FFFFFF')
        white = workbook.add_format({'bold': True,'align': 'center'})
        white.set_font_color('#FFFFFF')
        white.set_bg_color('#008000')
        complains = self.env['project.task'].search([])
         
        
        
        row = 3
        column = 0
 
        worksheet.set_column('D:D',20)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('H:H', 20)
        
        worksheet.merge_range('B1:J2', 'Complaints Report ',bold1)
        worksheet.write(row, column, 'Sr No.')
        worksheet.write(row, column+1, 'Month')
        worksheet.write(row, column+2, 'Date')
        worksheet.write(row, column+3, 'Property')
        worksheet.write(row, column+4, 'Description')
        worksheet.write(row, column+5, 'Flat/Off No')
        worksheet.write(row, column+6, 'Job Type')
        worksheet.write(row, column+7, 'Sub Contractor')
        worksheet.write(row, column+8, 'Quotation No.')
        worksheet.write(row, column+9, 'Job Completion Date ')
        worksheet.write(row, column+10, 'Total Amount (BD)')
        m = 1
        for all in complains:
            if all.job_type:
                job_type = all.job_type
            else:
                job_type = ''   
            if all.partner_id:
                partner = all.partner_id.name
            else:
                partner = ''  
            date = str(all.date_assign).split(' ')[0]
            month_nme = date.split('-')[1]
            month = calendar.month_name[int(month_nme)]
            print(date,"date-------------------------><><><><><><><><><")
            worksheet.write(row+m, column,m or '')
            worksheet.write(row+m, column+1,month or '')
            worksheet.write(row+m, column+2,date or '')
            worksheet.write(row+m, column+3,all.building_id.name or '')
            worksheet.write(row+m, column+4,all.pjt_name_id.name or '')
            worksheet.write(row+m, column+5,all.module_id.name or '')
            worksheet.write(row+m, column+6,job_type or '')
            worksheet.write(row+m, column+7,partner or '')
            worksheet.write(row+m, column+8,all.quat_no or '')
            worksheet.write(row+m, column+9,all.date_done or '')
            worksheet.write(row+m, column+10,all.amount or 0)
            m +=1
       
        
    
        
ComplaintsReport()
        
        
        