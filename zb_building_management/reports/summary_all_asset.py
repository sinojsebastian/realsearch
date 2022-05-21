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


class SummaryAllAssets(models.AbstractModel):
    _name = 'report.zb_building_management.summary_all_assets.xlsx'
    _description= 'Summary All Assets Excel'
    
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data,objs):
        
        #Summary worksheet
        
        worksheet = workbook.add_worksheet('Summary All Assets')
        title1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 16,'border':2})
        title1.set_font_color('#fdfefe')
        title1.set_bg_color('#34495e')
        
        title2 = workbook.add_format({'bold': True,'align': 'center', 'text_wrap': True,'border':1,'valign': 'vcenter','size': 8})
        
        title3 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2})
        title3.set_font_color('#fdfefe')
        title3.set_bg_color('#34495e')
        
        title31 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2})
#         title31.set_font_color('#fdfefe')
        
        percentage_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2,'num_format':'0%'})
        percentage_format.set_font_color('#fdfefe')
        percentage_format.set_bg_color('#34495e')
        
        currency_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2,'num_format':'"BHD" #,##0'})
        currency_format.set_font_color('#fdfefe')
        currency_format.set_bg_color('#34495e')
        
        wrap1= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
        wrap1.set_text_wrap()
        
        wrap2= workbook.add_format({'align': 'left','border':1,'size': 8,'valign': 'vcenter'})
        wrap2.set_text_wrap() 
        
        wrap3= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
        wrap3.set_text_wrap()
        wrap3.set_bg_color('#A2D296')
        currency_format2 = workbook.add_format({'align': 'center', 'valign': 'vcenter'
                                                      , 'size': 8,'border':1,'num_format':'#,##0'})
        currency_format2.set_text_wrap()
        currency_format2.set_bg_color('#A2D296')
        currency_format21 = workbook.add_format({'align': 'center', 'valign': 'vcenter'
                                                      , 'size': 8,'border':1,'num_format':'#,##0'})
        currency_format21.set_text_wrap()
        wrap4= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter','num_format':'0%'})
        wrap4.set_text_wrap()
        
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 10)
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
#         print(self.env.user.company_id)
        data=base64.b64decode(company_logo) 
        im = PILImage.open(BytesIO(data)) 
        x = im.save('logo.png') 
        worksheet.write('E1',cmpny.name,title2) 
        worksheet.write('E2',cmpny.street,title2) 
        worksheet.write('E3',cmpny.street2,title2) 
        worksheet.write('E4',cmpny.city,title2) 
        worksheet.write('E5',cmpny.country_id.name,title2) 
        worksheet.merge_range('B1:E5','%s \n %s |n %s \n %s \n %s'%(cmpny.name,cmpny.street,cmpny.street2 ,cmpny.city,cmpny.country_id.name),title2)
        worksheet.insert_image('A1:B4','logo.png',{'x_scale': 0.15, 'y_scale': 0.15})
        
        worksheet.merge_range('A6:H6', 'Summary Statement - %s'%(fields.Date.today()),title1)
        worksheet.write('A7','Property Name',title2)   
        worksheet.write('B7', 'Potential Income (BD)',title2)
        worksheet.write('C7', 'Total Units',title2)
        worksheet.write('D7', 'Occupied',title2)
        worksheet.merge_range('E7:F7', 'Actual Monthly Recurring Income(BD)',title2)
        worksheet.write('G7', 'Security Deposits',title2)
        worksheet.write('H7', 'Legal cases',title2)
        worksheet.set_row(5, 30)
        worksheet.set_row(6, 35)
        worksheet.set_row(13, 30)
        
        
        buildings = self.env['zbbm.building'].search([('building_type','in',['rent','both']),('module_ids','!=',False)])
        legal_records = self.env['legal.cases'].search([])
        row = 7
        column = 0
        m = 0

        for record in buildings:
            rentable_units = self.env['zbbm.module'].search([('building_id','=',record.id),('state','not in',['delisted','legal'])])
            legal_cases = self.env['legal.cases'].search([('building_id','=',record.id),('state','=','legal')])
            potential_income = total_units = occupied = 0
            monthly_income = security_deposit = legal = monthly_percent = 0
            for item in rentable_units:
                lease = self.env['zbbm.module.lease.rent.agreement'].search([('subproperty','=',item.id),('state','=','active')])
                potential_income += item.potential_rent
                total_units += item.contract_number
                if item.state == 'occupied':
                    occupied += item.contract_number
                    monthly_income += item.monthly_rate
                    security_deposit += lease.security_deposit
                legal = len(legal_cases)
            if potential_income and monthly_income != 0:
                monthly_percent =  monthly_income/potential_income
            worksheet.set_row(row+m, 25)
                
            worksheet.write(row+m, column,record.name or '',wrap3)
            worksheet.write(row+m, column+1,potential_income,currency_format2)
            worksheet.write(row+m, column+2,total_units,wrap3)
            worksheet.write(row+m, column+3,occupied,wrap1)
            worksheet.write(row+m, column+4,monthly_income,currency_format21)
            worksheet.write(row+m, column+5,monthly_percent or '0%',wrap4)
            worksheet.write(row+m, column+6,security_deposit,currency_format21)
            worksheet.write(row+m, column+7,legal,wrap1)
            
            m += 1
        
        worksheet.write('A%s'%(m+8), 'Total',title3)
        worksheet.write_formula('B%s'%(m+8),'{=SUM(B3:B%s)}'%(m+7),currency_format)
        worksheet.write_formula('C%s'%(m+8),'{=SUM(C3:C%s)}'%(m+7),title3)
        worksheet.write_formula('D%s'%(m+8),'{=SUM(D3:D%s)}'%(m+7),title3)
        worksheet.write_formula('E%s'%(m+8),'{=SUM(E3:E%s)}'%(m+7),currency_format)
        worksheet.write_formula('F%s'%(m+8),'{=AVERAGE(F3:F%s)}'%(m+7),percentage_format)
        worksheet.write_formula('G%s'%(m+8),'{=SUM(G3:G%s)}'%(m+7),currency_format)
        worksheet.write_formula('H%s'%(m+8),'{=SUM(H3:H%s)}'%(m+7),title3)
        worksheet.write('A%s'%(m+10), 'Prepared by : ',title31)
        worksheet.write('B%s'%(m+10),self.env.user.name ,title31)       
        
        
        #Building Worksheet
        
        for record in buildings:
            
            total_units = vacant = occupied = occupancy_rate = legal = 0
                
            worksheet = workbook.add_worksheet('%s.xlsx'%(record.name))
            title1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 16,'border':2})
            title2 = workbook.add_format({'bold': True,'align': 'center', 'border':1,'valign': 'vcenter','bg_color':'#8cb3d9','size': 10})
            
            title3 = workbook.add_format({'bold': True,'align': 'left', 'border':1,'valign': 'vcenter','size': 10,'bg_color':' #98AFC7'})
            
            wrap= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap.set_text_wrap()
             
            wrap1= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
            wrap1.set_text_wrap()
            
            wrap2= workbook.add_format({'align': 'left','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap2.set_text_wrap() 
           
            wrap3= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter','num_format': '0%'})
            wrap3.set_text_wrap()
            
            wrap4= workbook.add_format({'align': 'left','num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            
            wrap5= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.00','size': 8,'valign': 'vcenter'})
            wrap5.set_text_wrap()
            
            wrap_date= workbook.add_format({'align': 'center','border':1,'num_format': 'dd/mm/yyyy','size': 8,'valign': 'vcenter'})
            wrap_date.set_text_wrap()
            
            wrap_bold= workbook.add_format({'bold': True,'num_format':'#,##0.000','align': 'center','border':1,'size': 8,'valign': 'vcenter'})
            wrap_bold.set_text_wrap()
            
            
            wrap_bold_left= workbook.add_format({'bold': True,'align': 'left','border':1,'size': 8,'valign': 'vcenter'})
            wrap_bold_left.set_text_wrap()
            
#             wrap= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
#             wrap.set_text_wrap()
            
            wrap_yellow = workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap_yellow.set_text_wrap()
            wrap_yellow.set_bg_color('#ffff1a')
            
            wrap_yellow1 = workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap_yellow1.set_text_wrap()
            wrap_yellow1.set_bg_color('#ffd699')
            
            wrap_green1 = workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap_green1.set_text_wrap()
            wrap_green1.set_bg_color('#99e600')
            
            wrap_red = workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap_red.set_text_wrap()
            wrap_red.set_font_color('#FFFFFF')
            wrap_red.set_bg_color('#ff0000')
            
            wrap1_yellow= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
            wrap1_yellow.set_text_wrap()
            wrap1_yellow.set_bg_color('#ffff1a')
            
            wrap1_yellow1= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
            wrap1_yellow1.set_text_wrap()
            wrap1_yellow1.set_bg_color('#ffd699')
            
            wrap1_green1= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
            wrap1_green1.set_text_wrap()
            wrap1_green1.set_bg_color('#99e600')
            
            wrap1_red= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
            wrap1_red.set_text_wrap()
            wrap1_red.set_font_color('#FFFFFF')
            wrap1_red.set_bg_color('#ff0000')
            
            wrap2_yellow= workbook.add_format({'align': 'left','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap2_yellow.set_text_wrap() 
            wrap2_yellow.set_bg_color('#ffff1a')
            
            wrap2_yellow1= workbook.add_format({'align': 'left','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap2_yellow1.set_text_wrap() 
            wrap2_yellow1.set_bg_color('#ffd699')
            
            wrap2_green1= workbook.add_format({'align': 'left','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap2_green1.set_text_wrap() 
            wrap2_green1.set_bg_color('#99e600')
            
            wrap2_red= workbook.add_format({'align': 'left','border':1,'num_format': '#,##0.000','size': 8,'valign': 'vcenter'})
            wrap2_red.set_text_wrap() 
            wrap2_red.set_font_color('#FFFFFF')
            wrap2_red.set_bg_color('#ff0000')
            
            wrap5_yellow= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.00','size': 8,'valign': 'vcenter'})
            wrap5_yellow.set_text_wrap()
            wrap5_yellow.set_bg_color('#ffff1a')
            
            wrap5_yellow1= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.00','size': 8,'valign': 'vcenter'})
            wrap5_yellow1.set_text_wrap()
            wrap5_yellow1.set_bg_color('#ffd699')
            
            wrap5_red= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.00','size': 8,'valign': 'vcenter'})
            wrap5_red.set_text_wrap()
            wrap5_red.set_font_color('#FFFFFF')
            wrap5_red.set_bg_color('#ff0000')
            
            wrap5_green1= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0.00','size': 8,'valign': 'vcenter'})
            wrap5_green1.set_text_wrap()
#             wrap5_green1.set_font_color('#FFFFFF')
            wrap5_green1.set_bg_color('#99e600')
            
            wrap_date_yellow= workbook.add_format({'align': 'center','border':1,'num_format': 'dd/mm/yyyy','size': 8,'valign': 'vcenter'})
            wrap_date_yellow.set_text_wrap()
            wrap_date_yellow.set_bg_color('#ffff1a')
            
            wrap_date_yellow1= workbook.add_format({'align': 'center','border':1,'num_format': 'dd/mm/yyyy','size': 8,'valign': 'vcenter'})
            wrap_date_yellow1.set_text_wrap()
            wrap_date_yellow1.set_bg_color('#ffd699')
            
            wrap_date_red= workbook.add_format({'align': 'center','border':1,'num_format': 'dd/mm/yyyy','size': 8,'valign': 'vcenter'})
            wrap_date_red.set_text_wrap()
            wrap_date_red.set_font_color('#FFFFFF')
            wrap_date_red.set_bg_color('#ff0000')
            
            wrap_date_green1= workbook.add_format({'align': 'center','border':1,'num_format': 'dd/mm/yyyy','size': 8,'valign': 'vcenter'})
            wrap_date_green1.set_text_wrap()
            wrap_date_green1.set_bg_color('#99e600')
            
            
            color_red= workbook.add_format({})
            color_red.set_bg_color('#ff0000')
            color_green= workbook.add_format({})
            color_green.set_bg_color('#c1f0c1')
            color_green1= workbook.add_format({})
            color_green1.set_bg_color('#99e600')
            color_yellow= workbook.add_format({})
            color_yellow.set_bg_color('#ffff1a')
            color_yellow1= workbook.add_format({})
            color_yellow1.set_bg_color('#ffd699')
            
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 10)
            worksheet.set_column('C:C', 40)
            worksheet.set_column('D:D', 25)
            worksheet.set_column('E:E', 25)
            worksheet.set_column('F:F', 10)
            worksheet.set_column('G:G', 10)
            worksheet.set_column('H:H', 15)
            worksheet.set_column('I:I', 15)
            worksheet.set_column('J:J', 15)
            worksheet.set_column('K:K', 15)
            worksheet.set_column('L:L', 15)
            worksheet.set_column('M:M', 20)
            worksheet.set_column('N:N', 20)
            worksheet.set_column('O:O', 20)
            worksheet.set_column('P:P', 20)
            worksheet.set_column('Q:Q', 30)
           
            worksheet.set_row(5, 25)
            
            worksheet.merge_range('A2:P3', record.name,title1)
            worksheet.merge_range('A5:A6','S/N',title2)   
            worksheet.merge_range('B5:B6', 'Unit No.',title2)
            worksheet.merge_range('C5:C6', 'Tenants Name',title2)
            worksheet.merge_range('D5:D6', 'Contact Nos.',title2)
            worksheet.merge_range('E5:E6', 'Email Id',title2)
            worksheet.merge_range('F5:G5', 'Occupied',title2)
            worksheet.write('F6','Yes',title2)
            worksheet.write('G6','No',title2)
            worksheet.merge_range('H5:H6', 'Type',title2)
            worksheet.merge_range('I5:I6', 'Bedroom (No)',title2)
            worksheet.merge_range('J5:J6', 'Size of unit M2',title2)
            worksheet.merge_range('K5:K6', 'Lease Start Date',title2)
            worksheet.merge_range('L5:L6', 'Lease End Date',title2)
            worksheet.merge_range('M5:M6', 'Security Deposit(BD)',title2)
            worksheet.merge_range('N5:N6', 'Potential Rent',title2)
            worksheet.merge_range('O5:O6', 'Actual Monthly Rent(BD)',title2)
            worksheet.merge_range('P5:P6', 'Contract Status',title2)
            worksheet.merge_range('Q5:Q6', 'Remarks',title2)
            
            rentable_units = self.env['zbbm.module'].search([('building_id','=',record.id),('state','not in',['delisted','legal'])])
            
            legal_cases = self.env['legal.cases'].search([('building_id','=',record.id),('state','=','legal')])
            row = 5
            column = 0
            m = 1
            monthly_income = 0
            potential_income = 0
            for units in rentable_units:
                total_units += units.contract_number
                lease = self.env['zbbm.module.lease.rent.agreement'].search([('subproperty','=',units.id),('state','=','active')])
                
                monthly_income += units.monthly_rate
                potential_income += units.potential_rent
                
                yes = 'Yes' if units.state == 'occupied' else ''
                no = '' if units.state == 'occupied' else 'No'
                status = ''
#                 if units.rental_start_date and units.rental_end_date:
                if not lease:
#                     if not units.tenant_id:
                    vacant += 1
                    name = 'VACANT'
                    phone = 'VACANT'
                    email = 'VACANT'
                    status = 'No Contract'
                    style,style1,style_dt = wrap_yellow,wrap1_yellow,wrap_date_yellow
                    style2,style5 = wrap2_yellow,wrap5_yellow
                else:
                    name = lease.tenant_id.name or ''
                    phone = lease.tenant_id.phone or ''
                    email = lease.tenant_id.email or ''
                    style,style1,style_dt = wrap,wrap1,wrap_date
                    style2,style5 = wrap2,wrap5
                
                
                if lease.contract_status == 'signed':
                    status = 'Lease Signed'
                elif lease.contract_status == 'no_contract':
                    status = 'No Contract'
                elif lease.contract_status == 'in_process':
                    status = 'In Process'
                elif lease.contract_status == 'notice_period':
                    status = 'On Notice Period'
                    style,style1,style_dt = wrap_yellow1,wrap1_yellow1,wrap_date_yellow1
                    style2,style5 = wrap2_yellow1,wrap5_yellow1
                else:
                    pass
                
                if lease.agreement_start_date and lease.agreement_end_date:
                    lease_start_date = datetime.strptime(str(lease.agreement_start_date),'%Y-%m-%d').strftime('%m/%d/%Y')  
                    lease_end_date = datetime.strptime(str(lease.agreement_end_date),'%Y-%m-%d').strftime('%m/%d/%Y')
                    lease_st = datetime.strptime(str(lease.agreement_start_date),'%Y-%m-%d')
                    if lease_st.month == date.today().month and lease_st.year == date.today().year:
                        style,style1,style_dt = wrap_green1,wrap1_green1,wrap_date_green1
                        style2,style5 = wrap2_green1,wrap5_green1
                else:
                    lease_start_date =  ' '
                    lease_end_date = ' '
                
                    
                occupied = total_units - vacant
                legal = len(legal_cases)
                        
#                 monthly_income += item.monthly_rate
#                 security_deposit += item.advance
                if occupied and total_units:
                    occupancy_rate = occupied/total_units
                    
                worksheet.set_row(row+m, 25)
                worksheet.write(row+m, column,m or '',style1)
                worksheet.write(row+m, column+1,units.name or '',style1)
                worksheet.write(row+m, column+2,name,style2)
                worksheet.write(row+m, column+3,phone,style)
                worksheet.write(row+m, column+4,email,style)
                worksheet.write(row+m, column+5,yes,style)
                worksheet.write(row+m, column+6,no ,style)
                worksheet.write(row+m, column+7,units.type.name or '',style)
                
                worksheet.write(row+m, column+8,int(units.bed_room) or '',style1)
                worksheet.write(row+m, column+9,units.floor_area or '',style)
                worksheet.write(row+m, column+10,lease_start_date or '',style_dt)
                worksheet.write(row+m, column+11,lease_end_date or '',style_dt)
                worksheet.write(row+m, column+12,lease.security_deposit or '',style)
                worksheet.write(row+m, column+13,units.potential_rent or '0.000',style)
                worksheet.write(row+m, column+14,units.monthly_rate or '0.000',style)
                worksheet.write(row+m, column+15,status,style)
                worksheet.write(row+m, column+16,' ' or '',style)
                m+=1
            
            if legal_cases:
                for units in legal_cases:
                    worksheet.write(row+m, column,m or '',wrap1_red)
                    worksheet.write(row+m, column+1,units.module_id.name or '',wrap_red)
                    worksheet.write(row+m , column+2,units.tenant_id.name or '',wrap2_red)
                    worksheet.write(row+m , column+3,units.tenant_id.phone or '',wrap_red)
                    worksheet.write(row+m , column+4,'',wrap_red)  
                    worksheet.write(row+m , column+5,'',wrap_red)  
                    worksheet.write(row+m , column+6,'',wrap_red)  
                    worksheet.write(row+m , column+7,'',wrap_red)  
                    worksheet.write(row+m , column+8,'',wrap_red)  
                    worksheet.write(row+m , column+9,'',wrap_red)  
                    worksheet.write(row+m , column+10,'',wrap_red)  
                    worksheet.write(row+m , column+11,'',wrap_red)  
                    worksheet.write(row+m , column+12,'',wrap_red)  
                    worksheet.write(row+m , column+13,'0',wrap_red)  
                    worksheet.write(row+m , column+14,'0',wrap_red) 
                    worksheet.write(row+m , column+15,units.state or '',wrap_red) 
                    worksheet.write(row+m , column+16,' ',wrap_red)  
                    m+=1
                    
            rented_by = 'CURRENTLY RENTED BY ' + cmpny.name
            start_col = 'A'+str(row+m+1)
            end_col = 'M'+str(row+m+1)
            worksheet.merge_range('%s:%s'%(start_col,end_col),'TOTAL',wrap_bold)
            start_col1 = 'N'+str(row+m+1)
            start_col2 = 'O'+str(row+m+1)
            col = row+m
            
#             worksheet.write_formula('%s'%(start_col1), '{=SUM(N7:N%s)}'%(col),wrap_bold)
#             worksheet.write_formula('%s'%(start_col2), '{=SUM(O7:O%s)}'%(col),wrap_bold)
            
#             worksheet.write_formula('%s'%(start_col1), potential_income,wrap_bold)
#             worksheet.write_formula('%s'%(start_col2), monthly_income,wrap_bold)
            worksheet.write(row+m , column+13,potential_income,wrap_bold)  
            worksheet.write(row+m , column+14,monthly_income,wrap_bold)  
            
            worksheet.write(row+m , column+15,' ',wrap)  
            worksheet.write(row+m , column+16,' ',wrap)  
            
            start_col1 = 'A'+str(row+m+6)
            end_col1 = 'D'+str(row+m+6)
            end_col2 = 'F'+str(row+m+6)
            worksheet.merge_range('%s:%s'%(start_col1,end_col1),'Summary',title2)
#             worksheet.write(row+m+6,5,'',color_green)
            worksheet.write(row+m+8,5,'',color_yellow)
            worksheet.write(row+m+10,5,'',color_yellow1)
            worksheet.write(row+m+12,5,'',color_green1)
            worksheet.write(row+m+14,5,'',color_red)
             
#             worksheet.write(row+m+6,6,'Revised Lease Dates',wrap4)
            worksheet.write(row+m+8,6,'VACANT',wrap4)
            worksheet.write(row+m+10,6,'Notice Period',wrap4)
            worksheet.write(row+m+12,6,'New Tenant',wrap4)
            worksheet.write(row+m+14,6,'Legal',wrap4) 
             
            # Summary Table
            worksheet.write(row+m+6, column,'1' or '',wrap1) 
            worksheet.write(row+m+7, column,'2' or '',wrap1)
            worksheet.write(row+m+8, column,'3' or '',wrap1) 
            worksheet.write(row+m+9, column,'4' or '',wrap1)     
            worksheet.write(row+m+10, column,'5' or '',wrap1)
            worksheet.write(row+m+11, column,'6' or '',wrap1)     
            worksheet.write(row+m+12, column,'7' or '',wrap1) 
             
            worksheet.merge_range('B%s:C%s'%(str(row+m+7),str(row+m+7)),'TOTAL UNITS' or '',wrap2)
            worksheet.merge_range('B%s:C%s'%(str(row+m+8),str(row+m+8)),'NUMBER OF VACANT UNIT' or '',wrap2)
            worksheet.merge_range('B%s:C%s'%(str(row+m+9),str(row+m+9)),'NUMBER OF UNITS OCCUPIED' or '',wrap2)
            worksheet.merge_range('B%s:C%s'%(str(row+m+10),str(row+m+10)),'OCCUPANCY RATE' or '',wrap2)
            worksheet.merge_range('B%s:C%s'%(str(row+m+11),str(row+m+11)),'LEGAL CASES' or '',wrap2)
            worksheet.merge_range('B%s:C%s'%(str(row+m+12),str(row+m+12)),rented_by or '',wrap2)
            worksheet.merge_range('B%s:C%s'%(str(row+m+13),str(row+m+13)),'TOTAL PARKING SLOTS' or '',wrap2)
              
            worksheet.write(row+m+6, column+3,total_units or '0',wrap1) 
            worksheet.write(row+m+7, column+3,vacant or '0',wrap1)
            worksheet.write(row+m+8, column+3,occupied or '0',wrap1) 
            worksheet.write(row+m+9, column+3,occupancy_rate or '0%',wrap3)     
            worksheet.write(row+m+10, column+3,legal or '0',wrap1)
            worksheet.write(row+m+11, column+3,' ',wrap1)     
            worksheet.write(row+m+12, column+3,' ',wrap1) 
            
            
            
SummaryAllAssets()      
