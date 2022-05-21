from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class LeasingDetailsXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_leasing_details'
    _description = 'Leasing Details Report'
    _inherit = 'report.report_xlsx.abstract'


    
    def generate_xlsx_report(self, workbook, data, partners):
         
#         periods, product_data = self.get_aging_data(partners)

        worksheet= workbook.add_worksheet('Leasing Details')
        
        title1 = workbook.add_format({'align': 'left',
                                                      'bold': True, 'size': 10,})
        
        style = workbook.add_format({'size': 10,'bold':True,})
        styletext = workbook.add_format({'size': 13,'bold':True,'align': 'center'})
        style1 = workbook.add_format({'size': 10,'bold':True})
        style1.set_text_wrap()
        style2 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        style3 = workbook.add_format({'size': 10,'align': 'right', 'valign': 'vcenter','num_format': '#,##0.000'})
        style4 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        style4.set_text_wrap()
        
       
        worksheet.merge_range('G6:H6', 'Leasing Details',styletext)
        worksheet.write('A8', 'From Date:',style)
        worksheet.write('C8', 'To Date:',style)
        worksheet.set_row(10, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 13)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 12)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 12)
        worksheet.set_column('K:K', 12)
        worksheet.set_column('L:L', 10)
        worksheet.set_column('M:M', 12)
        worksheet.set_column('N:N', 18)
        worksheet.write('A11', 'Sr.#',style)
        worksheet.write('B11', 'Building Name',style)
        worksheet.write('C11', 'Flat No.',style)
        worksheet.write('D11', 'Property Advisor Name',style1)
        worksheet.write('E11','Lease Start Date',style) 
        worksheet.write('F11', 'Lease End Date',style1)
        worksheet.write('G11', 'Monthly Rent Amount',style1)
        worksheet.write('H11', 'Tenant Name',style)
        worksheet.write('I11', 'Mgt Status',style)
        worksheet.write('J11', 'Direct/Agent',style)
        worksheet.write('K11', 'Agent Name',style)
        worksheet.write('L11', 'Agent Commission Amount',style1)
        worksheet.write('M11','Renting Commission to the Owner',style1) 
        worksheet.write('N11', 'Remarks',style)
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        data=base64.b64decode(company_logo) 
        im = PILImage.open(BytesIO(data)) 
        x = im.save('logo.png') 
        if cmpny.name:
            cmpny_name = cmpny.name
        else:
            cmpny_name =''
        if cmpny.street:
            street = cmpny.street
        else:
            street =''
        if cmpny.street2:
            street2 = cmpny.street2
        else:
            street2 =''
        if cmpny.city:
            city = cmpny.city
        else:
            city =''
        if cmpny.country_id.name:
            country_id = cmpny.country_id.name
        else:
            country_id =''
        if cmpny.email:
            email = 'Email:%s'%(cmpny.email)
        else:
            email =''
            
        worksheet.merge_range('E1:F5','%s \n %s \n %s \n %s \n %s \n  %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.07, 'y_scale': 0.09})
        
        
        
        if partners.from_date and partners.to_date:
            
            from_date = datetime.strptime(str(partners.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            to_date = datetime.strptime(str(partners.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            leases = self.env['zbbm.module.lease.rent.agreement'].search([('agreement_start_date','<=',to_date),('agreement_start_date','>=',from_date)])
    
            worksheet.write('B8',from_date,style2)
            worksheet.write('D8',to_date,style2)
        
        
       # worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.15, 'y_scale': 0.15})

            count=1
            row = 12
            column=0
            if leases:
                for rec in leases:
                    if rec.subproperty.managed:
                        worksheet.write(row,column+8,'Managed',style2)
                    else:
                        worksheet.write(row,column+8,'Not Managed',style2)
                    worksheet.write(row,column,count,style2)
                    worksheet.write(row,column+1,rec.building_id.name or '',style2)
                    worksheet.write(row,column+2,rec.subproperty.name or '',style2)
                    worksheet.write(row,column+3,rec.adviser_id.name or '',style2)
                    lease_start_date = datetime.strptime(str(rec.agreement_start_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                    lease_end_date = datetime.strptime(str(rec.agreement_end_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                    worksheet.write(row,column+4,lease_start_date or '',style2)
                    worksheet.write(row,column+5,lease_end_date or '',style2)
                    worksheet.write(row,column+6,rec.monthly_rent or 0.0,style3)
                    worksheet.write(row,column+7,rec.tenant_id.name or '',style2)
                   
                    if rec.agent:
                        worksheet.write(row,column+9,'Agent',style2)
                    else:
                        worksheet.write(row,column+9,'Direct',style2)
                    worksheet.write(row,column+10,rec.agent.name or '',style2)
                    worksheet.write(row,column+11,rec.agent_commission_amount or 0.0,style3)
                    worksheet.write(row,column+12,rec.commission_percent_amount or 0.0,style3)
                    worksheet.write(row,column+13,rec.remarks or '',style4)
                    row+=1
                    count+=1
        

            
            
                    
        
        
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                