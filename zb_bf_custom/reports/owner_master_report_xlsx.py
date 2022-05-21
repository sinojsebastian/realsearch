from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlsxwriter

import logging
_logger = logging.getLogger(__name__)


class OwnerMasterXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_owner_master'
    _description = 'Owner Master Report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, owners):
        
       
        
        worksheet= workbook.add_worksheet('Owner Master')
         
        style = workbook.add_format({'size': 14,'bold':True,'align': 'center'})
        style1 = workbook.add_format({'size': 11,'bold':True})
        style1.set_text_wrap()
        style2 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                        'size': 10,'text_wrap':True})
        style3 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                        'size': 10})
        style3.set_text_wrap()
        title1 = workbook.add_format({'align': 'left', 'valign': 'left',
                                                       'bold': True, 'size': 10,})
        title1.set_text_wrap()
        
        cell_number_format = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                       'size': 10,
                                                  'num_format': '#,##0.00'})
        
        
        worksheet.set_row(8, 55)
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
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
        worksheet.write('A7', 'Date:', style1)
        worksheet.write('A8', 'Building:', style1)
        worksheet.write('A9', 'Sr.#', style1)
        worksheet.write('B9', 'Flat No.', style1)
        worksheet.write('C9', 'Type of the Flat', style1)
        worksheet.write('D9', 'Mgt Status', style1)
        worksheet.write('E9', 'Mgt Fees%', style1)
        worksheet.write('F9','Occupancy Status', style1) 
        worksheet.write('G9', 'Owner Name', style1)
        worksheet.write('H9', 'Owner Mobile No.', style1)
        worksheet.write('I9', 'Owner Contact No. 1', style1)
        worksheet.write('J9', 'Owner Contact No. 2', style1)
        worksheet.write('K9', 'Owner Email 1', style1)
        worksheet.write('L9', 'Owner Email 2', style1)
        worksheet.write('M9', 'Nationality',style1)
        worksheet.write('N9', 'Account Holder Name for Bank Transfer',style1)
        worksheet.write('O9', 'Bank Name',style1)
        worksheet.write('P9', 'IBAN',style1)
        worksheet.write('Q9', 'SWIFT',style1)
        worksheet.write('R9', 'Permanent Address',style1)
        worksheet.write('S9', 'Postal Address',style1)
        worksheet.write('T9', 'EWA Account No.',style1)
        worksheet.write('U9', 'Internet Line No.',style1)
        worksheet.write('V9', 'Passport No.',style1)
        worksheet.write('W9', 'CPR No.',style1)
        worksheet.merge_range('G6:H6', 'Owner Master',style)
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
#         data=base64.b64decode(company_logo) 
#         im = PILImage.open(BytesIO(data)) 
#         x = im.save('logo.png') 
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
            
        worksheet.merge_range('E1:F5','\n  %s \n %s  %s \n %s \n %s \n %s'%(cmpny_name,street,street2,city,country_id,email),title1)

        worksheet.merge_range('A1:A4','')
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.09, 'y_scale': 0.08})
      
        date = owners.date
        wiz_date = datetime.strptime(str(owners.date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        
        worksheet.write('B7',wiz_date,style2)
        building_id=owners.building_id
     
        
      
        modules = self.env['zbbm.module'].search([('create_date','<=',date),('building_id','=',building_id.id)])
        row = 7
        column=1
        
        worksheet.write(row,column,building_id.name,style2)
        column+=1
        count=1
        row = 9
        column=0
        params = self.env['ir.config_parameter'].sudo()  
        ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id')
        internet_product_id = params.get_param('zb_bf_custom.internet_product_id')
        
        for unit in modules:
    
            state = dict(self.env['zbbm.module'].fields_get(allfields=['state'])['state']['selection'])[unit.state]
            service_id = self.env['zbbm.services'].search([('module_id','=',unit.id),('product_id','=',int(ewa_product_id))])
            internet_service_id = self.env['zbbm.services'].search([('module_id','=',unit.id),('product_id','=',int(internet_product_id))])
            worksheet.write(row,column,count,style2)
            worksheet.write(row,column+1,unit.name or '',style2)
            worksheet.write(row,column+2,unit.type.name or '',style2)
            worksheet.write(row,column+3,'Managed' if unit.managed else 'Not Managed',style2)
            worksheet.write(row,column+4,unit.management_fees_percent or '',cell_number_format)
            worksheet.write(row,column+5,state or '',style2)
            worksheet.write(row,column+6,unit.owner_id.name or '',style2)
            worksheet.write(row,column+7,unit.owner_id.mobile or '',style2)
            phone = ''
            mobile = ''
            email = ''
            delivery_street = ''
            delivery_street2 = ''
            delivery_city = ''
            delivery_country= ''
            for contact in unit.owner_id.child_ids:
                if contact.type == 'contact':
                    phone += str(contact.phone) +","
                    mobile += str(contact.mobile) +","
                    email += str(contact.email) +","
                else:
                    if contact.type == 'delivery':
                        if contact.street:
                            delivery_street=contact.street
                        else:
                            delivery_street=''
                        if contact.street2:
                            delivery_street2=contact.street2
                        else:
                            delivery_street2=''
                        if contact.city:
                            delivery_city=contact.city
                        else:
                            delivery_city=''
                        if contact.country_id.name:
                            delivery_country=contact.country_id.name
                        else:
                            delivery_country=''
            worksheet.write(row,column+8,phone,style2)
            worksheet.write(row,column+9,mobile,style2)
            worksheet.write(row,column+10,unit.owner_id.email or '',style2)
            worksheet.write(row,column+11,email,style2)
            worksheet.write(row,column+12,unit.owner_id.country_id.name or '',style2)
       
            if unit.owner_id.bank_ids:
                for bank in unit.owner_id.bank_ids:
                    bankname=bank.bank_id.name
                    swift = bank.bank_id.bic
                    account_holder_name=bank.acc_holder_name
                    iban = bank.iban_no
                 
#                     bank_data=self.env['res.bank'].search[('bank_id',=',)]
#                     swift=bank.bank_id.bank_id.
#                 
                    worksheet.write(row,column+13,account_holder_name or '',style2)
                    worksheet.write(row,column+14,bankname or '',style2)
                    worksheet.write(row,column+15,iban or '',style2)
                    worksheet.write(row,column+16,swift or '',style2)
        
            if unit.owner_id:
                if unit.owner_id.street:
                    street=unit.owner_id.street
                else:
                    street=''
                if unit.owner_id.street2:
                    street2=unit.owner_id.street2
                else:
                    street2=''
                if unit.owner_id.city:
                    city=unit.owner_id.city
                else:
                    city=''
                if unit.owner_id.country_id.name:
                    country=unit.owner_id.country_id.name
                else:
                    country=''
                worksheet.write(row,column+17,'%s\n%s\n%s\n%s'%(street,street2 ,city,country),style3)
                
            if unit.building_id.street:
                street=unit.building_id.street
            else:
                street=''
            if unit.building_id.street2:
                street2=unit.building_id.street2
            else:
                street2=''
            if unit.building_id.city:
                city=unit.building_id.city
            else:
                city=''
#             if unit.building_id.country_id:
#                  country=unit.building_id.country_id.name
#             else:
#                 country=''
            worksheet.write(row,column+18,'%s  %s  %s  %s'%(delivery_street,delivery_street2 ,delivery_city,delivery_country),style3)
            worksheet.write(row,column+19,service_id.account_no if service_id and service_id.account_no else '' or  '',style2)
            worksheet.write(row,column+20,internet_service_id.account_no if internet_service_id and internet_service_id.account_no else '' or  '',style2)
            worksheet.write(row,column+21,unit.owner_id.passport or '',style2)
            worksheet.write(row,column+22,unit.owner_id.cpr or '',style2)
            
            row+=1
            count+=1
        
        
        