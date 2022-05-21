from collections import Counter,deque
from itertools import groupby
from datetime import datetime, timedelta,date
from odoo import tools
import calendar
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from operator import inv
from odoo import _, api, fields, models
import base64 
from io import BytesIO 
from PIL import Image as PILImage
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


class OccupancySummary(models.AbstractModel):
    
    _name = 'report.zb_building_management.occupancy_summary.xlsx'
    _description = 'Occupancy Summary'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data,objs):
        
        worksheet = workbook.add_worksheet('Occupancy Summary')
        title = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 16,'border':2})
        title.set_font_color('#0000A0')
        title.set_underline()
        
        datestring = datetime.strftime(datetime.now(), '%d/%m/%y')
        title.set_text_wrap()
        title22 = workbook.add_format({'bold': True,'align': 'center', 'text_wrap': True,'border':1,'valign': 'vcenter','size': 8})
        title2 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 15,'border':2})
        title2.set_bg_color('#ffc299')
        title2.set_text_wrap()
        title3 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 12,'border':2})
        title3.set_bg_color('#e6ffff')
        title3.set_text_wrap()
        
        
        
        
        title4 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 12,'border':2})
        title4.set_bg_color('#ffcccc')
        title4.set_text_wrap()
        
        title5 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 12,'border':2})
        title5.set_bg_color('#e6ffcc')
        title5.set_text_wrap()
        
        wrap = workbook.add_format({'align': 'center','bold': True, 'size': 12,'border':2,'valign': 'vcenter'})
        wrapb = workbook.add_format({'align': 'center','bold': True, 'size': 12,'border':2,'valign': 'vcenter'})
        wrapb.set_bg_color('#e6ffff')
        wrap_right = workbook.add_format({'align': 'right','bold': True, 'size': 12,'border':2,'valign': 'vcenter'})
        wrap_rightb = workbook.add_format({'align': 'right','bold': True, 'size': 12,'border':2,'valign': 'vcenter'})
        wrap_rightb.set_bg_color('#e6ffff')
        wrap_percentage = workbook.add_format({'align': 'center','bold': True, 'size': 12,'border':2,'num_format':'0%','valign': 'vcenter'})
        wrap_percentageb = workbook.add_format({'align': 'center','bold': True, 'size': 12,'border':2,'num_format':'0%','valign': 'vcenter'})
        wrap_percentageb.set_bg_color('#e6ffff')
        wrap1 = workbook.add_format({'align': 'center','bold': True, 'size': 10,'valign': 'vcenter'})
        address_format = workbook.add_format({'align': 'left','valign': 'vcenter','bold': True,'size': 10,'text_wrap': True})

        
        title_red = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                                      'bold': True, 'size': 16})
        title_red.set_font_color('#ff0000')
        title31 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2})
#
        title6 = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                                      'bold': True, 'size': 10})
        title6.set_font_color('#ff0000')
        title6.set_bg_color('#d6d6c2')
        
        title7 = workbook.add_format({'align': 'left', 'valign': 'vcenter',
                                                      'bold': True, 'size': 12})
        title7.set_font_color('#ff0000')
        title7.set_bg_color('#99bbff')
        wrap11 = workbook.add_format({'align': 'center','bold': True, 'size': 10,'valign': 'vcenter','num_format':'#,###0.000'})
        currency_format21 = workbook.add_format({'align': 'right', 'valign': 'vcenter'
                                                      ,'size': 12,'bold':True,'border':2,'num_format':'#,##0'})
        currency_format21.set_text_wrap()
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)
        
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 10)
        worksheet.set_column('L:L', 10)
        
        worksheet.set_row(12, 30)
        worksheet.set_row(7, 30)
        
        worksheet.merge_range('A8:J9', 'Occupied And Vacant Units',title)
        worksheet.merge_range('K8:L9', datestring ,title)
        
        cmpny = self.env.user.company_id
        worksheet.merge_range('A11:L11', cmpny.name,title2)
        
        worksheet.merge_range('A12:A13', 'SN',title3)
        worksheet.merge_range('B12:B13', 'Property',title3)
        worksheet.merge_range('C12:C13', 'Total # of Units',title3)
        worksheet.merge_range('D12:D13', 'Monthly PI',title3)
        
        worksheet.merge_range('E12:H12', 'Occupied',title4)
        worksheet.write('E13','Units',title4) 
        worksheet.write('F13','% Occ.Units',title4) 
        worksheet.write('G13','Income',title4) 
        worksheet.write('H13','%/PI',title4) 
        
        worksheet.merge_range('I12:L12', 'Vacant',title5)
        worksheet.write('I13','Units',title5) 
        worksheet.write('J13','% Vac.Units',title5) 
        worksheet.write('K13','Loss Income',title5) 
        worksheet.write('L13','%/PI',title5) 
        
        company_logo = self.env.user.company_id.logo
        company = self.env.user.company_id
        
        print(self.env.user.company_id)
        if company_logo:
            logo = BytesIO(base64.b64decode(company_logo or False))
        else:
            logo = ''
            
        if company.name:
          company_name = company.name
        else:
          company_name =''
        if company.street:
          street = company.street
        else:
          street =''
        if company.street2:
          street2 = company.street2
        else:
          street2 =''
        if company.city:
          city = company.city
        else:
          city =''
        if company.country_id.name:
          country_id = company.country_id.name
        else:
          country_id =''    
        

#         worksheet.merge_range('D1:H7','%s \n %s |n %s \n %s \n %s'%(cmpny.name,cmpny.street,cmpny.street2 ,cmpny.city,cmpny.country_id.name),title22)
        worksheet.merge_range('D1:H7','%s \n %s \n %s \n %s \n %s'%(company_name,street,street2 ,city,country_id),address_format)

        worksheet.merge_range('C1:C7','')
#         worksheet.insert_image('A1:B7','logo.png',{'x_scale': 0.22, 'y_scale': 0.22})
        worksheet.insert_image('A1:B7','logo.png', {'image_data': logo,'x_offset': 0,'x_scale': 0.13, 'y_scale': 0.13})

        m=0
        row = 13
        column = 0
        buildings = self.env['zbbm.building'].search([('building_type','in',['rent','both']),('module_ids','!=',False)])
        for record in buildings:
            total_units = monthly_pi = occupied = income = occ_unit_percent = pi_percent = 0
            vacant = vacant_percent = loss_income = li = loss_pi_percent = 0
            rentable_units = self.env['zbbm.module'].search([('building_id','=',record.id),('state','not in',['delisted','legal']),('managed','=',objs.managed)])
            worksheet.set_row(row+m, 30)
            for units in rentable_units:
#                 total_units += units.contract_number
                total_units += 1
                monthly_pi += units.potential_rent
#                 income += units.monthly_rate
                if units.state == 'occupied':
                    income += units.monthly_rate
                    occupied += 1
#                     occupied += units.contract_number
                if total_units and occupied != 0:
                    occ_unit_percent =  occupied/total_units
                if monthly_pi and income != 0:
                    pi_percent = income/monthly_pi
                if units.state != 'occupied':
                    vacant += 1
                    li += units.monthly_rate
                    loss_income += units.potential_rent
#                     loss_income = units.potential_rent * vacant
                if vacant and total_units:
                    vacant_percent = vacant/total_units
#                 if units.state !='occupied':
#                     loss_income = units.potential_rent * vacant
#                 else:
#                     loss_income += 0 
                if  loss_income and monthly_pi:
                    loss_pi_percent =  loss_income/monthly_pi
             
                
            worksheet.write(row+m, column,m+1 or '',wrap)    
            worksheet.write(row+m, column+1,record.name or '',wrap)
            worksheet.write(row+m, column+2,total_units or '0',wrap)
            worksheet.write(row+m, column+3,monthly_pi or 0.000,currency_format21)
            
            worksheet.write(row+m, column+4,occupied or '0',wrap)
            worksheet.write(row+m, column+5,occ_unit_percent or '0%',wrap_percentage)
            worksheet.write(row+m, column+6,income or 0.000,currency_format21)
            worksheet.write(row+m, column+7,pi_percent or '0%',wrap_percentage)
            
            worksheet.write(row+m, column+8,vacant or '0',wrap)
            worksheet.write(row+m, column+9,vacant_percent or '0%',wrap_percentage)
            worksheet.write(row+m, column+10,loss_income or '-',currency_format21)
            worksheet.write(row+m, column+11,loss_pi_percent or '0%',wrap_percentage)
            
            m += 1
        worksheet.set_row(row+m, 30)
#    
        worksheet.write('A%s'%(row+m+1), ' ',wrapb)
        worksheet.write('B%s'%(row+m+1), 'Total',wrapb)
        worksheet.write('B%s'%(row+m+2), 'Prepared By' or '',title31)
        worksheet.write('C%s'%(row+m+2),self.env.user.name ,title31) 
        worksheet.write_formula('C%s'%(row+m+1),'{=SUM(C9:C%s)}'%(row+m),wrapb)
        worksheet.write_formula('D%s'%(row+m+1),'{=SUM(D9:D%s)}'%(row+m),currency_format21)
        worksheet.write_formula('E%s'%(row+m+1),'{=SUM(E9:E%s)}'%(row+m),wrapb)
        worksheet.write_formula('F%s'%(row+m+1),'{=AVERAGE(F9:F%s)}'%(row+m),wrap_percentageb)
        worksheet.write_formula('G%s'%(row+m+1),'{=SUM(G9:G%s)}'%(row+m),currency_format21)
        worksheet.write_formula('H%s'%(row+m+1),'{=AVERAGE(H9:H%s)}'%(row+m),wrap_percentageb)
        worksheet.write_formula('I%s'%(row+m+1),'{=SUM(I9:I%s)}'%(row+m),wrapb)
        worksheet.write_formula('J%s'%(row+m+1),'{=AVERAGE(J9:J%s)}'%(row+m),wrap_percentageb)
        worksheet.write_formula('K%s'%(row+m+1),'{=SUM(K9:K%s)}'%(row+m),currency_format21)
        worksheet.write_formula('L%s'%(row+m+1),'{=(K%s/D%s)}'%(row+m+1,row+m+1),wrap_percentageb)    
        
        
        
        worksheet = workbook.add_worksheet('Vaccant Units per system')       
        
        worksheet.set_row(2, 25)
        worksheet.set_row(3, 20)
        
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 15)
        
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 15)
        
        
        worksheet.merge_range('A3:D3', cmpny.name,title_red)
        worksheet.write('A4',' ',title6)
        worksheet.write('B4','Type',title6)
        worksheet.write('C4','Flat/Office Number',title6)
        worksheet.write('D4','Potential Rent',title6)
        
        property = self.env['zbbm.building'].search([('building_type','=',['rent','both']),('module_ids','!=',False)])
        row = 4
        col = 0
        for record in property:
            row +=1
            worksheet.write(row,col+1,' ',wrap1)
            worksheet.write(row,col+2,' ',wrap1)
            worksheet.write(row,col+3,' ',wrap1)

            worksheet.merge_range('A%s:D%s'%(row,row), record.name,title7)
            units = self.env['zbbm.module'].search([('building_id','=',record.id),('state','not in',['delisted','legal']),('managed','=',objs.managed)])
            for item in units:
                if not item.tenant_id:
                    worksheet.write(row+1,col+1,item.type.name or '',wrap1)
                    worksheet.write(row+1,col+2,item.name or '',wrap1)
                    worksheet.write(row+1,col+3,item.potential_rent or 0.000,wrap11)
                    row +=1
            row +=1       
                    
OccupancySummary()      