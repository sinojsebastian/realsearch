from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
import xlsxwriter
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


import logging
_logger = logging.getLogger(__name__)


class EWAMasterXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_ewa_master'
    _description = 'EWA Master Report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, wiz):
        
        worksheet= workbook.add_worksheet('EWA Master Report')
        bold = workbook.add_format({'size': 10,'bold': True})
        # date_format = workbook.add_format({'num_format': 'dd/mm/yyyy','size': 10})
        style = workbook.add_format({'align': 'center', 'valign': 'vcenter','size': 10})
        heading_format = workbook.add_format({'align': 'center','valign': 'vcenter','bold': True,'size': 14,})
        address_format = workbook.add_format({'align': 'center','valign': 'vcenter','bold': True,'size': 10,'text_wrap': True})
                                              
        worksheet.set_row(0, 50)
        worksheet.set_row(4, 20)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:D', 16)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        
        worksheet.merge_range('A5:H5', 'EWA Master', heading_format)
    
        worksheet.write('A7', 'Date:',bold)
        worksheet.write('A8', 'Building:',bold)
        worksheet.write('A10', 'Sr.#',bold)
        worksheet.write('B10', 'Flat No.',bold)
        worksheet.write('C10', 'Owner Name',bold)
        worksheet.write('D10', 'Trf Status',bold)
        worksheet.write('E10', 'Paid By Rs',bold)
        worksheet.write('F10','EWA Account No.',bold) 
        worksheet.write('G10', 'Mgt Status',bold)
        worksheet.write('H10', 'Occupancy Status',bold)
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        company = self.env.user.company_id
        logo = False
        if self.env.user.company_id.logo:
            logo = BytesIO(base64.b64decode(self.env.user.company_id.logo or False))

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
             
        worksheet.merge_range('C1:D2','%s \n %s \n %s \n %s \n %s'%(company_name,street,street2 ,city,country_id),address_format)
        worksheet.insert_image(0,0,'picture.png', {'image_data': logo,'x_offset': 0,'x_scale': 0.1, 'y_scale': 0.1})

        date = datetime.strptime(str(wiz.date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        worksheet.write('B7',date,style)
        building_id=wiz.building_id
        worksheet.write('B8',building_id.name,style)
        
        params = self.env['ir.config_parameter'].sudo()  
        ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id')
        
        row=10
        count=1
        for flat in building_id.module_ids:
            for line in flat.service_ids:
                if line.product_id.id == int(ewa_product_id):
                    if line.create_date.date() <= wiz.date:
                        worksheet.write(row,0,count or '',style)
                        worksheet.write(row,1,flat.name or '',style)
                        worksheet.write(row,2,flat.owner_id.name or '',style)
                        worksheet.write(row,3,'Yes' if line.trf_status else 'No',style)
                        worksheet.write(row,4,'Yes' if line.managed_by_rs else 'No',style)
                        worksheet.write(row,5,line.account_no or '',style)
                        worksheet.write(row,6,'Managed' if flat.managed else 'Not Managed',style)
                        worksheet.write(row,7,flat.state or '',style)
                        row=row+1
                        count=count+1
        
        
        