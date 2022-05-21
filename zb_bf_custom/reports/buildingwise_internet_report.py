from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from dateutil.rrule import rrule, DAILY


import logging
_logger = logging.getLogger(__name__)



class BuildingInternetReport(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_building_internet_report'
    _description = 'BuildingWise Internet Report'
    _inherit = 'report.report_xlsx.abstract'

    
    def generate_xlsx_report(self, workbook, data, wiz):
         

        worksheet= workbook.add_worksheet('BuildingWise Internet Report')
        
        title1 = workbook.add_format({'align': 'left','bold': True, 'size': 10,})
        title1.set_text_wrap()
        heading_format = workbook.add_format({'align': 'center','size': 14,'bold':True})
        heading_bold_left = workbook.add_format({'size': 11,'bold':True,'align': 'left'})
        heading_bold_right = workbook.add_format({'size': 11,'bold':True,'align': 'right'})
        text_heading_bold_left = workbook.add_format({'size': 10,'bold':True,'align': 'left','text_wrap':True})
        text_heading_bold_left_fg1 = workbook.add_format({'size': 10,'bold':True,'align': 'left','fg_color': '#FFA500'})
        text_heading_bold_center = workbook.add_format({'align': 'center','size': 10,'bold':True})
        number_format = workbook.add_format({'size': 10,'align': 'right','num_format': '#,###0.000'})
        table_value_format = workbook.add_format({'align': 'left','size': 10})
        number_format_bold_right = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000'})
        number_format_bold_right_fg = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000','fg_color': '#FFFF00'})
        number_format_bold_right_fg1 = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000','fg_color': '#FFA500'})

        formater = workbook.add_format({'border': 1})
        
        cmpny = self.env.user.company_id
        
        worksheet.set_row(1, 25)
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 20)
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
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
         
        
#         data=base64.b64decode(company_logo) 
#         im = PILImage.open(BytesIO(data)) 
#         x = im.save('logo.png') 

        logo = False
        if cmpny.logo:
            logo = BytesIO(base64.b64decode(cmpny.logo or False))
        
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
            
        worksheet.merge_range('C1:C7','%s \n %s \n %s \n %s \n %s \n %s'%(cmpny_name,street,street2,city,country_id,email),title1)
#         worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.60, 'y_scale': 0.60})
        worksheet.insert_image('A1:A4','picture.png', {'image_data': logo,'x_offset': 0,'x_scale': 0.13, 'y_scale': 0.13})

            
        

        wiz_building = wiz.building_id
        
        worksheet.merge_range('E8:G8','Building Wise Internet Report',heading_format)
        worksheet.write('A10','Building',title1)
        worksheet.write('B10',wiz_building.name,title1)
        
        worksheet.set_row(12, 45)
        
        worksheet.write('A13', 'Sr.#',text_heading_bold_left)
        worksheet.write('B13', 'Flat No',text_heading_bold_left)
        worksheet.write('C13', 'Internet Line Registered Contact Name',text_heading_bold_left)
        worksheet.write('D13', 'Internet Line Number',text_heading_bold_left)
        worksheet.write('E13', 'Mgt Status',text_heading_bold_left)
        worksheet.write('F13', 'Occupancy Status',text_heading_bold_left)
        worksheet.write('G13', 'Internet Package Amount',text_heading_bold_left)
        worksheet.write('H13', 'Tenant Limit Amount',text_heading_bold_left)
        worksheet.write('I13', 'Tenant Upgrade Request date',text_heading_bold_left)
        worksheet.write('J13', 'OSN Package/Extra Charge',text_heading_bold_left)
        worksheet.write('K13', 'Initial Connection Date',text_heading_bold_left)
        worksheet.write('L13', 'Disconnected Date',text_heading_bold_left)
        worksheet.write('M13', 'Reconnected Date',text_heading_bold_left)
        
        
        params = self.env['ir.config_parameter'].sudo()  
        internet_product_id = params.get_param('zb_bf_custom.internet_product_id')
        
        
        row =14
        count =1
        for module_id in wiz_building.module_ids:
            
            lease_ids = self.env['zbbm.module.lease.rent.agreement'].search([('subproperty','=',module_id.id),('state','=','active')])
            if len(lease_ids) > 0:
                internet_service_id = self.env['zbbm.services.agreement'].search([('module_id','=',module_id.id),('lease_id','=',lease_ids[0].id),('product_id','=',int(internet_product_id))])
                internet_service_ids = self.env['raw.services'].search([('module_id','=',module_id.id),('lease_agreement_id','=',lease_ids[0].id),('product_id','=',int(internet_product_id))])

            else:
                internet_service_id = self.env['zbbm.services'].search([('module_id','=',module_id.id),('product_id','=',int(internet_product_id))])
                internet_service_ids = self.env['raw.services'].search([('module_id','=',module_id.id),('product_id','=',int(internet_product_id))])
                
            owner = module_id.owner_id and module_id.owner_id.name or ''
            package_amount = 0.000
            if internet_service_id:
                for serv_id in internet_service_id:
                    package_amount += (serv_id.owner_share + serv_id.tenant_share)
                
                if internet_service_id.tenant_upgrade_date:
                    tenant_upgrade_date = datetime.strptime(str(internet_service_id.tenant_upgrade_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                else:
                    tenant_upgrade_date = ''
                if internet_service_id.initial_connection_date:
                    initial_connection_date = datetime.strptime(str(internet_service_id.initial_connection_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                else:
                    initial_connection_date = ''
                if internet_service_id.from_date:
                    from_date = datetime.strptime(str(internet_service_id.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                else:
                    from_date = ''
                if internet_service_id.to_date:
                    to_date = datetime.strptime(str(internet_service_id.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                else:
                    to_date = ''
                        
                worksheet.write(row,0,count,table_value_format)
                worksheet.write(row,1,module_id.name,table_value_format)
                worksheet.write(row,2,owner,table_value_format)
                worksheet.write(row,3,internet_service_id.account_no if internet_service_id and internet_service_id.account_no else '',table_value_format)
                worksheet.write(row,4,'Managed' if module_id.managed else 'Not Managed',table_value_format)
                worksheet.write(row,5,module_id.state,table_value_format)
                worksheet.write(row,6,package_amount if package_amount else '',number_format)
                worksheet.write(row,7,internet_service_id.tenant_share if internet_service_id and internet_service_id.tenant_share else '',number_format)
                worksheet.write(row,8,tenant_upgrade_date,table_value_format)
                worksheet.write(row,9,internet_service_id.osn_extra_charge or '',number_format)
                worksheet.write(row,10,initial_connection_date,table_value_format)
                worksheet.write(row,11,from_date,table_value_format)
                worksheet.write(row,12,to_date,table_value_format)
                count+=1
                row+=1
        
#         Commented as per bhumi's feedback on 11/01/2021

#         building_internet_service = wiz_building.service_ids.filtered(lambda r: r.product_id.id == int(internet_product_id))
#         if building_internet_service:
#             next_row = row
#             next_count = count
#             for service in building_internet_service:
#                 if service.area:
#                     worksheet.write(next_row,0,next_count,table_value_format)
#                     worksheet.write(next_row,1,service.area,table_value_format)
#                     next_count+=1
#                     next_row+=1
            
        
        
            

        
        
        
        
        
        
        
        
        
        
    
        
        
        
        