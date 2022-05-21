from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
import xlsxwriter
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)


class TenantMasterXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_tenant_master'
    _description = 'Tenant Master Report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, partners):
         
        worksheet= workbook.add_worksheet('Tenant Master')
        
        style = workbook.add_format({'size': 10,'bold':True})
        style1 = workbook.add_format({'size': 10,'bold':True})
        style1.set_text_wrap()
        style2 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                       'size': 10})
        style2.set_text_wrap()
        style3 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                       'size': 10})
        style3.set_text_wrap()
        title1 = workbook.add_format({'align': 'left', 'valign': 'left',
                                                      'bold': True, 'size': 10,})
        title1.set_text_wrap()
        styletext = workbook.add_format({'size': 13,'bold':True,'align': 'center'})
        
        cell_number_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                       'size': 10,
                                                  'num_format': '#,###0.000'})
        
        
        
        worksheet.merge_range('G6:H6', 'Tenant Master',styletext)
        worksheet.set_row(8, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
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
        worksheet.set_column('W:W', 15)
        worksheet.write('A7', 'Date:',style)
        worksheet.write('A8', 'Building:',style)
        worksheet.write('A9', 'Sr.#',style)
        worksheet.write('B9', 'Flat No.',style)
        worksheet.write('C9', 'Type of the Flat',style)
        worksheet.write('D9', 'Mgt Status',style)
        worksheet.write('E9','Occupancy Status',style) 
        worksheet.write('F9', 'Tenant Name',style)
        worksheet.write('G9', 'Nationality',style)
        worksheet.write('H9', 'Rent Amount',style)
        worksheet.write('I9', 'Payment Mode',style1)
        worksheet.write('J9', 'Lease Start Date',style)
        worksheet.write('K9', 'Lease End Date',style)
        worksheet.write('L9', 'Next Rent Due Date',style1)
        worksheet.write('M9', 'Tenant Contact Mobile No.',style1)
        worksheet.write('N9', 'Tenant Contact Telephone No.',style1)
        worksheet.write('O9', 'Tenant Office Email',style1)
        worksheet.write('P9', 'Tenant Personal Email',style1)
        worksheet.write('Q9', 'Date Of Vacancy',style1)
        worksheet.write('R9', 'EWA Limit',style1)
        worksheet.write('S9', 'Batelco Package Name',style1)
        worksheet.write('T9', 'Property Advisor Name',style1)
        worksheet.write('U9', 'Agent Name',style1)
        worksheet.write('V9', 'Permanent Address',style1)
        worksheet.write('W9', 'Postal Address',style1)
        worksheet.write('X9', 'Passport No.',style1)
        worksheet.write('Y9', 'CPR No.',style)
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        data = base64.b64decode(company_logo) 

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
            
        
        worksheet.merge_range('E1:F5','\n %s \n %s  %s \n %s \n %s \n %s'%(cmpny_name,street,street2 ,cmpny.city,country_id,email),title1)
        worksheet.merge_range('A1:A4','')
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.09, 'y_scale': 0.08})
        
        date = partners.date
        wiz_date = datetime.strptime(str(partners.date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        worksheet.write('B7',wiz_date,style1)
        
        building_id=partners.building_id
        lease_ids = self.env['zbbm.module.lease.rent.agreement'].search([('building_id','=',building_id.id),('agreement_start_date','<=',date),('state','=','active')])
#         ('agreement_start_date','>=',date)

        row = 7
        column=1
        worksheet.write(row,column,building_id.name,style2)
        column+=1
        count=1
        row = 9
        column=0
        for lease in lease_ids:      
            state = dict(self.env['zbbm.module'].fields_get(allfields=['state'])['state']['selection'])[lease.subproperty.state]
            
            worksheet.write(row,column,count,style2)
            worksheet.write(row,column+1,lease.subproperty.name or '',style2)
            worksheet.write(row,column+2,lease.subproperty.type and lease.subproperty.type.name or '',style2)
            worksheet.write(row,column+3,'Managed' if lease.subproperty.managed else 'Not Managed',style2)
            worksheet.write(row,column+4,state or '',style2)
            worksheet.write(row,column+5,lease.tenant_id.name or '',style2)
            params = self.env['ir.config_parameter'].sudo()  
            ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id')
            service_id = self.env['zbbm.services'].search([('module_id','=',lease.subproperty.id),('product_id','=',int(ewa_product_id))])
            worksheet.write(row,column+6,lease.tenant_id.country_id and lease.tenant_id.country_id.name or '',style2)
            worksheet.write(row,column+7,lease.monthly_rent or '',cell_number_format)
            worksheet.write(row,column+8,lease.tenant_id.payment_mode if lease.tenant_id and lease.tenant_id.payment_mode else '' or '',style2)
            if lease.agreement_start_date:
                lease_start_date = datetime.strptime(str(lease.agreement_start_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            else:
                lease_start_date = ''
            if lease.agreement_end_date:
                lease_end_date = datetime.strptime(str(lease.agreement_end_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            else:
                lease_end_date = ''
                
            dates=[]
            for date in lease.invoice_plan_ids:
                for lines in date:
                    if lines.inv_date:
                        dates.append(lines.inv_date)
            print('================dates================',dates)
            if dates:
                scheduledatelist = list(reversed(dates)) #purpose: to have earliest dates first
                date_rent = min(scheduledatelist, key=lambda s: 
                    datetime.strptime(str(s),DEFAULT_SERVER_DATE_FORMAT).date()-partners.date).strftime(date_format)
            else:
                date_rent = ''
            worksheet.write(row,column+9,lease_start_date or '',style2)
            worksheet.write(row,column+10,lease_end_date or '',style2)
            worksheet.write(row,column+11,date_rent or '',style2)
            worksheet.write(row,column+12,lease.tenant_id.mobile or '',style2)
            worksheet.write(row,column+13,lease.tenant_id.phone or '',style2)
            worksheet.write(row,column+14,lease.tenant_id.email or '',style2)
            worksheet.write(row,column+15,lease.tenant_id.email or '',style2)
            worksheet.write(row,column+16,lease_end_date or '',style2)
            worksheet.write(row,column+17,service_id.owner_share if service_id and service_id.owner_share else '' or  '',cell_number_format)
            worksheet.write(row,column+18,service_id.package_name if service_id and service_id.package_name else '' or '',style2)
            worksheet.write(row,column+19,lease.adviser_id and lease.adviser_id.name or '',style2)
            worksheet.write(row,column+20,lease.agent and lease.agent.name or '',style2)
            if lease.tenant_id:
                if lease.tenant_id.street:
                    street=lease.tenant_id.street
                else:
                    street=''
                if lease.tenant_id.street2:
                    street2=lease.tenant_id.street2
                else:
                    street2=''
                if lease.tenant_id.city:
                    city=lease.tenant_id.city
                else:
                    city=''
                if lease.tenant_id.country_id.name:
                    country=lease.tenant_id.country_id.name
                else:
                    country=''
                worksheet.write(row,column+21,'%s\n%s\n%s\n%s'%(street,street2 ,city,country),style2)
                worksheet.write(row,column+22,'%s\n%s\n%s\n%s'%(street,street2 ,city,country),style2)
            worksheet.write(row,column+23,lease.tenant_id.passport or '',style2)
            worksheet.write(row,column+24,lease.tenant_id.cpr or '',style2)
            row+=1
            count+=1

