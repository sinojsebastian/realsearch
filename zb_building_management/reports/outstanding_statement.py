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


class OutstandingStatement(models.AbstractModel):
    
    _name = 'report.zb_building_management.outstanding_statement.xlsx'
    _description = 'Outstanding Statement'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data,objs):
        
        worksheet = workbook.add_worksheet('Summary')
        
        title = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 16,'border':2,'num_format': 'dd/mm/yyyy'})
        title.set_text_wrap()
         
        title1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':1})
        title1.set_font_color('#ffffff')
        title1.set_bg_color('#00264d')
        title1.set_text_wrap()
        
        title2 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 10,'border':2})
        title2.set_text_wrap()
        title2.set_font_color('#ffffff')
        title2.set_bg_color('#193366')
#         title2.set_border_color('#000000')
        
        title3 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2})
        title3.set_font_color('#fdfefe')
        title3.set_bg_color('#193366')
        
        title4 = workbook.add_format({'align': 'right', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2,'num_format':'#,##0'})
        title4.set_font_color('#fdfefe')
        title4.set_bg_color('#193366')
        
        title5 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 12,'border':1})
        title5.set_bg_color('#ffe6cc')
        title5.set_text_wrap()
        
        title_blue = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 6,'border':1})
        title_blue.set_bg_color('#cce0ff')
        title_blue.set_text_wrap()
        
        title_green = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 6,'border':1})
        title_green.set_bg_color('#88cc00')
        title_green.set_text_wrap()
        
        percentage_format = workbook.add_format({'align': 'right', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2,'num_format':'0%'})
        percentage_format.set_font_color('#fdfefe')
        percentage_format.set_bg_color('#193366')
        
        currency_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2,'num_format':'"BHD" #,##0'})
        currency_format.set_font_color('#fdfefe')
        currency_format.set_bg_color('#193366')
        
        currency_format_right = workbook.add_format({'align': 'right', 'valign': 'vcenter',
                                                      'bold': True, 'size': 8,'border':2,'num_format':'"BHD" #,##0'})
        currency_format_right.set_font_color('#fdfefe')
        currency_format_right.set_bg_color('#193366')
        
        wrap= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0','size': 6,'valign': 'vcenter'})
        wrap.set_text_wrap()
            
        wrap1= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
        wrap1.set_text_wrap()
        
        wrap2= workbook.add_format({'align': 'left','border':1,'size': 8,'valign': 'vcenter'})
        wrap2.set_text_wrap() 
        
        wrap3= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter'})
        wrap3.set_text_wrap()
        wrap3.set_bg_color('#C6D49F')
        
        wrap4= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter','num_format':'0%'})
        wrap4.set_text_wrap()
        
        wrap5= workbook.add_format({'align': 'right','border':1,'size': 8,'valign': 'vcenter','num_format': '#,##0.000'})
        wrap5.set_text_wrap()
        
        wrap_date= workbook.add_format({'align': 'center','border':1,'num_format': 'dd/mm/yyyy','size': 8,'valign': 'vcenter'})
        wrap_date.set_text_wrap()
        
        title_black = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 9,'border':1,'num_format': '#,##0.000'})
        title_black.set_bg_color('#000000')
        title_black.set_font_color('#ffffff')
        title_black.set_text_wrap()
        
        wrap_red= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0','size': 6,'valign': 'vcenter'})
        wrap_red.set_text_wrap()
        wrap_red.set_font_color('#FFFFFF')
        wrap_red.set_bg_color('#ff0000')
        
        wrap_yellow= workbook.add_format({'align': 'center','border':1,'num_format': '#,##0','size': 6,'valign': 'vcenter'})
        wrap_yellow.set_text_wrap()
        wrap_yellow.set_bg_color('#ffff1a')

        
        wrap_date_yellow= workbook.add_format({'align': 'center','border':1,'num_format': 'dd/mm/yyyy','size': 8,'valign': 'vcenter'})
        wrap_date_yellow.set_text_wrap()
        wrap_date_yellow.set_bg_color('#ffff1a')
        
        wrap_date_red= workbook.add_format({'align': 'center','border':1,'num_format': 'dd/mm/yyyy','size': 8,'valign': 'vcenter'})
        wrap_date_red.set_text_wrap()
        wrap_date_red.set_font_color('#FFFFFF')
        wrap_date_red.set_bg_color('#ff0000')
        
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 10)
         
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
         
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 10)
        
        wrap31= workbook.add_format({'align': 'center','border':1,'size': 8,'valign': 'vcenter','num_format':'#,##0'})
        wrap31.set_text_wrap()
        wrap31.set_bg_color('#C6D49F')
        
        datestring = datetime.strftime(datetime.now(), '%d/%m/%y')
        if objs.date:
            outstanding_date = datetime.strptime(str(objs.date),'%Y-%m-%d').strftime('%m/%d/%Y')
            outstanding_date1 = datetime.strptime(str(objs.date),'%Y-%m-%d').strftime('%d %B %Y')
        else:
            outstanding_date = datetime.strftime(datetime.now(),'%m/%d/%Y')
            outstanding_date1 = datetime.strftime(datetime.now(),'%d %B %Y')

        worksheet.merge_range('A6:I6', 'Summary Statement %s'%(objs.date),title)
        worksheet.set_row(8, 40)
        
        worksheet.write('A9','Property Name',title1)   
        worksheet.write('B9', 'Potential Income',title1)
        worksheet.write('C9', 'Total Units',title1)
        worksheet.write('D9', 'Occupied',title1)
        worksheet.merge_range('E9:F9', 'Actual Monthly Recurring Income(BD)',title1)
        worksheet.write('G9', 'Total Outstanding Till %s'%(outstanding_date),title1)
#         worksheet.write('H9', 'Advance Payment',title1)
        worksheet.write('H9', 'Security Deposits',title1)
        worksheet.write('I9', 'No.of Legal cases',title1)
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        print(self.env.user.company_id)
        data=base64.b64decode(company_logo) 
        im = PILImage.open(BytesIO(data)) 
        x = im.save('logo.png') 
        worksheet.merge_range('B1:B5','')
        worksheet.merge_range('C1:F5','%s \n %s |n %s \n %s \n %s'%(cmpny.name,cmpny.street,cmpny.street2 ,cmpny.city,cmpny.country_id.name),title2)
        worksheet.insert_image('A1:B4','logo.png',{'x_scale': 0.15, 'y_scale': 0.15})
        
        
        buildings = self.env['zbbm.building'].search([('building_type','=','rent')])
        row = 9
        column = 0
        m = 0
        n =0
        for record in buildings:
            
            legal_cases = self.env['legal.cases'].search([('building_id','=',record.id),('state','=','legal')])
            rentable_units = self.env['zbbm.module'].search([('building_id','=',record.id),('state','not in',['delisted','legal'])])
            potential_income =0 
            total_units = 0
            occupied =0 
            advance = 0
            monthly_income = 0
            security_deposit = 0
            legal = 0
            monthly_percent =0
            outstanding =0
            outstanding1 =0
            lis =[]
            for item in rentable_units:
                lease = self.env['zbbm.module.lease.rent.agreement'].search([('subproperty','=',item.id),
                                                                             ('state','=','active')])
                open_inv_units = self.env['account.move'].search([('building_id','=',record.id),
                                                                     ('module_id','=',item.id),
                                                                     ('state','=','open'),
                                                                    ('invoice_date','<=',objs.date)])
                
#                 for record in lease:
#                      security_deposit += record.security_deposit
#                 print('++++++++++++++++++++++++++++leaseeeeeeeeeee++++++++++++++++++++++++++++++++++',lease)
                for records in lease:
                    security_deposit+=records.security_deposit
                for inv in open_inv_units:
                    outstanding += inv.residual
                
                potential_income += item.potential_rent
                total_units += item.contract_number
                if item.state == 'occupied':
                    occupied += item.contract_number
                monthly_income += item.monthly_rate
#                 security_deposit += item.advance
                legal = len(legal_cases)
                advance +=item.advance_paid
            for all in legal_cases:
                open_journl_item =self.env['account.move.line'].search([('partner_id','=',all.tenant_id.id),('building_id','=',all.building_id.id),('date_maturity','<=',objs.date),('account_id','=',all.tenant_id.property_account_receivable_id.id)])
                for jrnl in open_journl_item:
                    if jrnl.debit:
                        outstanding1 += jrnl.debit
                    if jrnl.credit:
                        outstanding1 -= jrnl.credit
            if potential_income and monthly_income != 0:
                monthly_percent =  monthly_income/potential_income
#             if lis == []:
#                 lis =[0]   
            worksheet.set_row(row+m, 25) 
            worksheet.write(row+m, column,record.name or '',wrap3)
            worksheet.write(row+m, column+1,potential_income,wrap31)
            worksheet.write(row+m, column+2,total_units,wrap3)
            worksheet.write(row+m, column+3,occupied,wrap1)
            worksheet.write(row+m, column+4,monthly_income,wrap31)
            worksheet.write(row+m, column+5,monthly_percent or '0%',wrap4)
            worksheet.write(row+m, column+6,outstanding+outstanding1,wrap31)
#             worksheet.write(row+m, column+7,advance,wrap31)
            worksheet.write(row+m, column+7,security_deposit,wrap31)
            worksheet.write(row+m, column+8,legal,wrap1)
            
            m += 1
        m += 1    
        worksheet.write('A%s'%(m+9), 'Total',title3)
        worksheet.write_formula('B%s'%(m+9),'{=SUM(B3:B%s)}'%(m+8),currency_format)
        worksheet.write_formula('C%s'%(m+9),'{=SUM(C3:C%s)}'%(m+8),title3)
        worksheet.write_formula('D%s'%(m+9),'{=SUM(D3:D%s)}'%(m+8),title3)
        worksheet.write_formula('E%s'%(m+9),'{=SUM(E3:E%s)}'%(m+8),currency_format)
        worksheet.write_formula('F%s'%(m+9),'{=AVERAGE(F3:F%s)}'%(m+8),percentage_format)
        worksheet.write_formula('G%s'%(m+9),'{=SUM(G3:G%s)}'%(m+8),currency_format)
#         worksheet.write_formula('H%s'%(m+9),'{=SUM(H3:H%s)}'%(m+8),currency_format)
        worksheet.write_formula('H%s'%(m+9),'{=SUM(H3:H%s)}'%(m+8),currency_format)
        worksheet.write_formula('I%s'%(m+9),'{=SUM(I3:I%s)}'%(m+8),title3)
        
        
        worksheet.merge_range('A%s:D%s'%(m+11,m+11), 'Outstanding-Segregation as of %s'%(outstanding_date1),title2)
        worksheet.set_row(m+10, 25)
        worksheet.set_row(m+11, 45)
        
        worksheet.write('A%s'%(m+12),'Property Name',title1)   
        worksheet.write('B%s'%(m+12), 'Amount Outstanding On Legal Cases',title1)
#         worksheet.write('C%s'%(m+12), 'Amount Outstanding on Antenna',title1)
        worksheet.write('C%s'%(m+12), 'Other outstanding collections',title1)
        worksheet.write('D%s'%(m+12), 'Total Outstanding (BD)',title1)
        row1 = m+12
        row2 = m+12
        
        for record in buildings:
            lis2 = []
            outstanding1 = 0
            total_outstanding =0 
            legal_outstanding = 0
            other_outstanding = 0
            antenna_outstanding = 0
           
           #Legal units with open invoice
            legal_units = self.env['legal.cases'].search([('building_id','=',record.id)])
            for item in legal_units:
                open_inv_units = self.env['account.move.line'].search([('building_id','=',record.id),
                                                     ('partner_id','=',item.tenant_id.id),
                                                     ('account_id.internal_type', '=', 'receivable')
                                                     ], order="date_maturity desc, id desc")

                for inv in open_inv_units:
                    if inv.debit:
                        legal_outstanding += inv.debit
                    elif inv.credit:
                        legal_outstanding -= inv.credit
           
           #Antenna units with open invoice
            antenna_units = self.env['zbbm.module'].search([('building_id','=',record.id),
                                                            ('type.name','=','Antenna'),('state','not in',['delisted'])])
            for item in antenna_units:
                open_inv_units = self.env['account.move'].search([('building_id','=',record.id),
                                                                     ('module_id','=',item.id),
                                                                     ('state','=','open'),
                                                                     ('type','=','out_invoice'),
                                                                     ('invoice_date','<=',objs.date)])
                for inv in open_inv_units:
                    antenna_outstanding += inv.residual
                  
            
           #Other units with open invoice 
            other_units = self.env['zbbm.module'].search([('building_id','=',record.id),
                                                          ('status','!=','legal'),('type.name','!=','Antenna'),('state','not in',['delisted','legal'])])
            
            for item in other_units:
                open_inv_units = self.env['account.move'].search([('building_id','=',record.id),
                                                                     ('module_id','=',item.id),
                                                                     ('state','=','open'),
                                                                     ('invoice_date','<=',objs.date)])
                for inv in open_inv_units:
                    other_outstanding += inv.residual
           
           #Total units with open invoice 
            rentable_units = self.env['zbbm.module'].search([('building_id','=',record.id),('state','not in',['delisted','legal'])])
            for item in rentable_units:
                open_inv_units = self.env['account.move'].search([('building_id','=',record.id),
                                                                     ('module_id','=',item.id),
                                                                     ('state','=','open'),
                                                                     ('invoice_date','<=',objs.date)])
                for inv in open_inv_units:
                    total_outstanding += inv.residual
            
            for all in legal_units:
                open_journl_item =self.env['account.move.line'].search([('partner_id','=',all.tenant_id.id),('building_id','=',all.building_id.id),('date_maturity','<=',objs.date),('account_id','=',all.tenant_id.property_account_receivable_id.id)])
                for jrnl in open_journl_item:
                    if jrnl.debit:
                        outstanding1 += jrnl.debit
                    if jrnl.credit:
#                         print("jrnl.credit---------------------",jrnl.credit)
                        outstanding1 -= jrnl.credit
                
#                 outstanding1 = 0   
            worksheet.write(row1, column,record.name or '',wrap3)
            worksheet.write(row1, column+1,legal_outstanding,wrap5)
#             worksheet.write(row1, column+2, antenna_outstanding,wrap5)
            worksheet.write(row1, column+2,other_outstanding,wrap5)   
            worksheet.write(row1, column+3,total_outstanding+outstanding1,wrap5) 
            row1 +=1
        
        worksheet.write('A%s'%(row1+1), 'Total Outstanding',title3)    
        worksheet.write_formula('B%s'%(row1+1),'{=SUM(B%s:B%s)}'%(row2,row1),currency_format_right)
#         worksheet.write_formula('C%s'%(row1+1),'{=SUM(C%s:C%s)}'%(row2,row1),currency_format_right)
        worksheet.write_formula('C%s'%(row1+1),'{=SUM(C%s:C%s)}'%(row2,row1),currency_format_right)
        worksheet.write_formula('D%s'%(row1+1),'{=SUM(D%s:D%s)}'%(row2,row1),title4)
        
        for record in buildings:
            worksheet = workbook.add_worksheet('%s.xlsx'%(record.name)) 
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 5)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 10)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 10)
            worksheet.set_column('G:G', 10)
            worksheet.set_column('H:H', 10)
            worksheet.set_column('I:I', 10)
            worksheet.set_column('J:J', 10, None, {'hidden': True})
            worksheet.set_column('K:K', 10)
            worksheet.set_column('L:L', 10)
            worksheet.set_column('M:M', 10)
            worksheet.set_column('N:N', 10, None, {'hidden': True})
            worksheet.set_column('O:O', 10, None, {'hidden': True})
            worksheet.set_column('P:P', 40)
            worksheet.set_row(0, 25)
            worksheet.set_row(1, 30)
            worksheet.merge_range('A1:P1', record.name,title5)
            worksheet.write('A2','S.N',title_blue)   
            worksheet.write('B2', 'Unit.',title_blue)
            worksheet.write('C2', 'Name',title_blue)
            worksheet.write('D2', 'Contract Status',title_blue)
            worksheet.write('E2', 'Tenant occupied',title_blue)
            worksheet.write('F2', 'Legal',title_blue)
            worksheet.write('G2', 'Lease Start',title_blue)
            worksheet.write('H2', 'Lease Start',title_blue)
            worksheet.write('I2', 'Potential Income',title_green)
            worksheet.write('J2', 'Payment Mode',title_green)
            worksheet.write('K2', 'Security Deposit',title_green)
            worksheet.write('L2', 'Monthly Recurring Income',title_green)
            worksheet.write('M2', 'Outstanding Till %s'%(outstanding_date),title_green)
            worksheet.write('N2', 'Advance Payment',title_green)
            worksheet.write('O2', 'No.of months Outstanding',title_green)
            worksheet.write('P2', 'Comments',title_green)
        
            rentable_units = self.env['zbbm.module'].search([('building_id','=',record.id),('state','not in',['delisted','legal'])])
            legal_cases = self.env['legal.cases'].search([('building_id','=',record.id),('state','=','legal')])
            m = 0
            row = 2 
            column = 0
            ############################################
            for units in rentable_units:
                lease = self.env['zbbm.module.lease.rent.agreement'].search([('subproperty','=',units.id),
                                                                             ('state','=','active')])
                open_inv_units = self.env['account.move'].search([('building_id','=',record.id),
                                                                         ('module_id','=',units.id),
                                                                         ('state','=','open'),
                                                                         ('invoice_date','<=',objs.date)])
                
                total_outstanding = 0
                for inv in open_inv_units:
                        total_outstanding += inv.residual
                
                if units.state == 'occupied':
                    occupancy = 'Yes'
                else:
                    occupancy = 'No'
                
                if not lease:
                    style,style_dt = wrap_yellow,wrap_date_yellow
#                     style2,style5 = wrap2_yellow,wrap5_yellow
                else:
                    style,style_dt = wrap,wrap_date
#                     style2,style5 = wrap2,wrap5
                
                if lease.contract_status == 'signed':
                    status = 'Lease Signed'
                elif lease.contract_status == 'no_contract':
                    status = 'No Contract'
                elif lease.contract_status == 'in_process':
                    status = 'In Process'
                elif lease.contract_status == 'notice_period':
                    status = 'On Notice Period'
                else:
                    status = ''
                    
                if lease.agreement_start_date and lease.agreement_end_date:
                    lease_start_date = datetime.strptime(str(lease.agreement_start_date),'%Y-%m-%d').strftime('%m/%d/%Y')  
                    lease_end_date = datetime.strptime(str(lease.agreement_end_date),'%Y-%m-%d').strftime('%m/%d/%Y')
                else:
                    lease_start_date =  ' '
                    lease_end_date = ' '
                    
                worksheet.set_row(row, 20)
                worksheet.write(row, column,m+1 or '',style)
                worksheet.write(row, column+1,units.name,style)
                worksheet.write(row, column+2,units.tenant_id.name or ' ',style)
                worksheet.write(row, column+3,status,style)
                worksheet.write(row, column+4,occupancy,style)
                worksheet.write(row, column+5,'No',style) 
                worksheet.write(row, column+6,lease_start_date or '',style_dt)
                worksheet.write(row, column+7,lease_end_date or '',style_dt)
                worksheet.write(row, column+8,units.potential_rent or '0',style)
                worksheet.write(row, column+9,' ',style)
                worksheet.write(row, column+10,lease.security_deposit,style)
                worksheet.write(row, column+11,units.monthly_rate,style)
                worksheet.write(row, column+12,total_outstanding,style)
                worksheet.write(row, column+13,'  ',style)
                worksheet.write(row, column+14,'  ',style)
                worksheet.write(row, column+15,'  ',style)
                row +=1
                m += 1
                    
            for units in legal_cases:
                sum = 0
#                 print(units,"legal----------------------<<<<<<<<<<<<<<<<<<",units.tenant_id.id,units.building_id.id,"ll",self.env['account.move.line'].search([('partner_id','=',units.tenant_id.id)]))
                journl_item = self.env['account.move.line'].search([('partner_id','=',units.tenant_id.id),('building_id','=',units.building_id.id),('date_maturity','<=',objs.date),('account_id','=',units.tenant_id.property_account_receivable_id.id)])
#                 print(journl_item,"jj=----------------------------------")
                for rec in journl_item:
                    if uin.debit:
                        sum += rec.debit
                    if uin.credit:
                        sum -= rec.credit    
                    
                worksheet.set_row(row, 20)
                worksheet.write(row, column,m+1 or '',wrap_red)
                worksheet.write(row, column+1,units.module_id.name,wrap_red)
                worksheet.write(row, column+2,units.tenant_id.name,wrap_red)
                worksheet.write(row, column+3,'Legal',wrap_red)
                worksheet.write(row, column+4,'',wrap_red)
                worksheet.write(row, column+5,'',wrap_red)
                worksheet.write(row, column+6,'',wrap_red)
                worksheet.write(row, column+7,'',wrap_red)
                worksheet.write(row, column+8,'',wrap_red)
                worksheet.write(row, column+9,'',wrap_red)
                worksheet.write(row, column+10,'',wrap_red)
                worksheet.write(row, column+11,'',wrap_red)
                worksheet.write(row, column+12,sum,wrap_red)
                worksheet.write(row, column+13,'',wrap_red)
                worksheet.write(row, column+14,'',wrap_red)
                worksheet.write(row, column+15,'',wrap_red)
                row +=1
                m += 1
            worksheet.set_row(row, 25)
            worksheet.merge_range('A%s:H%s'%(row+1,row+1),'Total For %s'%(record.name),title_black)
            
            worksheet.write_formula('I%s'%(row+1),'{=SUM(I3:I%s)}'%(row),title_black)
            worksheet.write(row, column+9,' ',title_black)
            worksheet.write_formula('K%s'%(row+1),'{=SUM(K3:K%s)}'%(row),title_black)
            worksheet.write_formula('L%s'%(row+1),'{=SUM(L3:L%s)}'%(row),title_black)
            worksheet.write_formula('M%s'%(row+1),'{=SUM(M3:M%s)}'%(row),title_black)
            worksheet.write_formula('N%s'%(row+1),'{=SUM(N3:N%s)}'%(row),title_black)
            worksheet.write(row, column+14,'  ',title_black)
            worksheet.write(row, column+15,'  ',title_black)
        
        
OutstandingStatement()      
