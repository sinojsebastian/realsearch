from collections import Counter,deque
from itertools import groupby
from datetime import datetime, timedelta,date
from odoo import tools
import calendar
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from operator import inv
from odoo import _, api, fields, models
# from io import BytesIO
import io
# import urllib2
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
# LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class PiechartsReport(models.AbstractModel):
    _name = 'report.zb_building_management.salesanalysis_report.xlsx'
    _description = 'Sale Analysis Report'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data,objs):
        Sheet = 'salesanalysis_report.xlsx'
        worksheet = workbook.add_worksheet(Sheet)
        
        worksheet.set_paper(9)
        worksheet.hide_gridlines(2)
#         worksheet.print_area('A1:G48')
        worksheet.fit_to_pages(1, 1) 
        worksheet.set_column('C:C', 18)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('B:B', 18)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('G:G', 18)
        worksheet.set_column('F:F', 18)
        worksheet.set_column('H:H', 18)
        bold = workbook.add_format({'bold': 1})
        title = workbook.add_format({'bold': 1,'border':2,'align':'center','bg_color':'#B4B2B6'})
        border = workbook.add_format({'bold': 1,'border':2,'align':'center'})
        border1 = workbook.add_format({'bold': 1,'border':2,'align':'center','bg_color':'#B4B2B6'})
        border1.set_bg_color('#B4B2B6')
#         border.set_align('vjustify')
        bold2 = workbook.add_format({'text_wrap':1,'border':2,'valign':'vcenter' })
#         bold2.set_align('vjustify')
        datez= workbook.add_format({'bold': 1,'num_format': 'dd/mm/yyyy','align':'left'})
        left = workbook.add_format({'align': 'left','border':2})
        leftq = workbook.add_format({'align': 'left','border':2,'num_format': '#,##0.000'}) 
        left2 = workbook.add_format({'align': 'left','border':2,'bold':1,'bg_color':'#B4B2B6'})
        left2.set_bg_color('#B4B2B6')
        
        state_book = self.env['crm.lead'].search([('probability','=',70),('date_open','>=',objs.date_from),('date_open','<=',objs.date_to)])
        state_sign = self.env['crm.lead'].search([('probability','=',90),('date_open','>=',objs.date_from),('date_open','<=',objs.date_to)])
        state_new = self.env['crm.lead'].search([('probability','=',10),('date_open','>=',objs.date_from),('date_open','<=',objs.date_to)])
        state_call = self.env['crm.lead'].search([('probability','=',15),('date_open','>=',objs.date_from),('date_open','<=',objs.date_to)])
        state_follow = self.env['crm.lead'].search([('probability','=',20),('date_open','>=',objs.date_from),('date_open','<=',objs.date_to)])
        state_wait = self.env['crm.lead'].search([('probability','=',49),('date_open','>=',objs.date_from),('date_open','<=',objs.date_to)])
        state_close = self.env['crm.lead'].search([('probability','=',100),('date_open','>=',objs.date_from),('date_open','<=',objs.date_to)])
        
        headings = ['Status', 'Count']
        data = [
            ['New','Call','Follow','Booked', 'Signing Agreement','Waiting','Closed'],
            [len(state_new),len(state_call),len(state_follow),len(state_book),len(state_sign),len(state_wait),len(state_close)],
        ]
        
#         url = 'https://www.propertyfinder.bh/images/pf_broker/logo/06b48e380f4c5f9f0c06680840f4819476691cb6/desktop'

#         image_data = BytesIO(urlopen(url).read())
#         image_data = io.BytesIO(urlopen(url).read())     
        
#         image_data2 = BytesIO(self.env.user.company_id.logo.read())
        
        
        
        
        
        worksheet.merge_range('C1:C4',' ') 
        worksheet.merge_range('B30:G30',' ',left) 
#         worksheet.insert_image('B1:B4',url,{'x_scale': .8, 'y_scale': .5,'image_data': image_data})
        worksheet.merge_range('B5:D5',self.env.user.company_id.name,bold)
        worksheet.merge_range('B6:D6',self.env.user.company_id.street)
        if self.env.user.company_id.street2:
            street2 = self.env.user.company_id.street2
        else:
            street2 = ""
        if self.env.user.company_id.city:
            city = self.env.user.company_id.city
        else:
            city = ""
        if self.env.user.company_id.zip:
            zip = self.env.user.company_id.zip
        else:
            zip = ""
        worksheet.merge_range('B7:D7',street2+city+zip)
        worksheet.merge_range('B8:D8',self.env.user.company_id.country_id.name)
        worksheet.merge_range('B9:D9',self.env.user.company_id.phone)
        worksheet.merge_range('B10:D10',self.env.user.company_id.email)
        worksheet.write_row('F15', headings, left2)
        
        worksheet.write_column('F16', data[0],left)
        worksheet.write_column('G16', data[1],left)
        
        chart1 = workbook.add_chart({'type': 'pie'})
#         chart1.set_chartarea({'fill': {'color': '#E2D5F1'}})
        chart1.set_plotarea({
                'layout': {
                    'width':  1,
                    'height': 1,
                }
            })


        chart1.add_series({
            'name': 'Pie sales data',
            'categories':  Sheet+ '!$F$16:$F$22',
            'values':      Sheet+'!$G$16:$G$22',
            'points': [
                {'fill': {'color': '#99ccff'}},
                {'fill': {'color': '#ff751a'}},
                {'fill': {'color': '#99c08a'}},
                {'fill': {'color': '#2611da'}},
                {'fill': {'color': '#d1da11'}},
                {'fill': {'color': '#ed0ffc'}}
            ],
#             'fill' : {'none' :True}   
              'border' :{'color' :'white'}              
        })

        chart3 = workbook.add_chart({'type': 'pie'})
        chart3.set_chartarea({'fill': {'color': '#E2D5F1'}})
        chart3.set_plotarea({
                'layout': {
                    'width':  1,
                    'height': 1,
                }
            })


        chart3.add_series({
            'name': 'Pie sales data',
            'categories': '$F$16:$F$22',
            'values':     '$G$16:$G$22',
            'points': [
                {'fill': {'color': '#99ccff'}},
                {'fill': {'color': '#ff751a'}},
                {'fill': {'color': '#99c08a'}},
                {'fill': {'color': '#2611da'}},
                {'fill': {'color': '#d1da11'}},
                {'fill': {'color': '#ed0ffc'}}
            ],
                           
        })
        chart1.set_title({'name': 'Sales Process'})
        chart1.set_style(1)
        chart3.set_style(2)
        
        
    
        
        worksheet.insert_chart('B13', chart1)
#         worksheet.insert_chart('H13', chart3)
        
#         headings1 = ['Unit', 'Invoice Total',]
        
        
        
        
        
        
#         worksheet.write_row('G1', headings1, bold)
        
        chart2 = workbook.add_chart({'type': 'column'})
        
        worksheet.merge_range('B28:G29', 'Customer Sales Analysis ',title)
        state_need = self.env['crm.lead'].search(['|',('probability','=',70),('probability','=',90)])
        m=0
        row =31
        column =1
        row2=0
        column2=7
        worksheet.write('B31','Customer',border1)
        worksheet.write('C31' , 'Status',border1)
        worksheet.write('D31' , 'Unit Count',border1)
        worksheet.write('E31' , 'Total Invoice',border1)
        worksheet.write('F31' , 'Paid',border1)
        worksheet.write('G31' , 'Outstanding',border1)
        total_inv =0
        lis=[]
        lis2 =[]
        dicp = {}
        dict = {}
        tot = 0
        for items in state_need:
            if(items.partner_id,items.stage_id) in dict :
                dict[items.partner_id,items.stage_id][1] += float(items.unit_id.invoice_total)
                dict[items.partner_id,items.stage_id][2] += float(items.unit_id.payment_total)
                dict[items.partner_id,items.stage_id][3] += float(items.unit_id.balance_invoice)
                dict[items.partner_id,items.stage_id][0] += 1
            else:
                
                dict[items.partner_id,items.stage_id] = [1,float(items.unit_id.invoice_total),float(items.unit_id.payment_total),float(items.unit_id.balance_invoice)]
                
            
            
        for cust,value in dict.items():
        
            customer = str(cust[0].name)
            stage = str(cust[1].name)
            unit = value[0]
            total_invoice =  value[1]
            total_inv+=total_invoice
            paid =  value[2]
            outstanding = value[3]
            worksheet.set_row(row+m, 30)
            worksheet.write(row+m, column,customer or '',bold2)
            worksheet.write(row+m, column+1,stage or '',left)
            worksheet.write(row+m, column+2,unit or '',left)
            worksheet.write(row+m, column+3,total_invoice or '',leftq)
            worksheet.write(row+m, column+4,paid or '',leftq)
            worksheet.write(row+m, column+5,outstanding or '',leftq)
            
#             worksheet.write(row2+1+m, column2,unit)
#             worksheet.write(row2+1+m, column2+1,total_invoice)
            m += 1
        worksheet.write(row+m+1,column, 'Date', bold)
        worksheet.write(row+m+1,column+1,datetime.today(),datez)
        worksheet.write(row+m+1,column+3,'Printed by' , bold)
        worksheet.write(row+m+1,column+4,self.env.user.name , bold)    
#                 print(lis,lis2,"------------------------")
        worksheet.print_area('A1:G%s'%(str(row+m+4)))  
        
        workbook.close()
        
PiechartsReport()       