from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.exceptions import UserError,Warning

import logging
from distutils.command.build import build
_logger = logging.getLogger(__name__)



class Building_EWA_Account_Xlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_building_ewa_account'
    _description = 'Building Wise EWA Account Report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data,wiz):
         
#         periods, product_data = self.get_aging_data(partners)

        worksheet= workbook.add_worksheet('EWA Account Summary')
        
        title1 = workbook.add_format({'align': 'left',
                                                      'bold': True, 'size': 10,})
        styletext = workbook.add_format({'size': 13,'bold':True,'align': 'center'})
        style = workbook.add_format({'size': 10,'bold':True,})
        table_value_format = workbook.add_format({'size': 10,'align': 'right'})
        wrap = workbook.add_format({'size': 10,'bold':True,})
        wrap.set_text_wrap()
        style1 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        number_format_right = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','num_format': '#,###0.000'})
        
        worksheet.set_row(10, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        
        worksheet.merge_range('C6:D6', 'EWA Account Summary',styletext)
        worksheet.write('A8', 'Building:',style)
        worksheet.write('B8',wiz.building_id.name or '',style1)
        worksheet.write('A11', 'Sr.#',style)
        worksheet.write('B11', 'Building Name',style)
        worksheet.write('C11', 'Total No.Of Flats',style)
        worksheet.write('D11', 'Mgt EWA Account Transferred',wrap)
        worksheet.write('E11','Not Mgt EWA Account Transferred',wrap) 
        worksheet.write('F11', 'Mgt EWA Account Not Transferred',wrap)
        worksheet.write('G11', 'Not Mgt EWA Account Not Transferred',wrap)
        
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
            
        worksheet.merge_range('E1:F5','%s \n %s \n %s \n %s \n %s \n  %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.065, 'y_scale': 0.08})
        
        #Fetching the EWA Service product
        params = self.env['ir.config_parameter'].sudo() 
        ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id') or False
        product = self.env['product.product'].search([('id','=',ewa_product_id)])
        if not ewa_product_id:
            raise Warning(_("""Please configure EWA Service Product in the Accounting Settings"""))
        
        #Building wise EWA data structuring
        building_ewa_data = {}
        if wiz.building_id:
            building_ids = wiz.building_id
        else:
            building_ids = self.env['zbbm.building'].search([])
        for building in building_ids:
            count_managed_ewa_transfered = 0 
            count_managed_ewa_not_transfered = 0
            count_not_managed_ewa_transfered = 0
            count_not_managed_ewa_not_transfered = 0
            for flat in building.module_ids:
                count_managed_ewa_transfered +=len(flat.service_ids.filtered(lambda r: r.product_id == product and r.trf_status == True and r.managed_by_rs == True))
                count_managed_ewa_not_transfered += len(flat.service_ids.filtered(lambda r: r.product_id == product and r.trf_status == False and r.managed_by_rs == True))
                count_not_managed_ewa_transfered += len(flat.service_ids.filtered(lambda r: r.product_id == product and r.trf_status == True and r.managed_by_rs == False))
                count_not_managed_ewa_not_transfered += len(flat.service_ids.filtered(lambda r: r.product_id == product and r.trf_status == False and r.managed_by_rs == False))
#             for flat in building.module_ids:
                if building_ewa_data.get(building.id):
                    building_ewa_data[building.id]['flat_count'] = len(building.module_ids)
                    building_ewa_data[building.id]['managed_ewa_transfered'] = count_managed_ewa_transfered
                    building_ewa_data[building.id]['managed_ewa_not_transfered'] = count_managed_ewa_not_transfered
                    building_ewa_data[building.id]['not_managed_ewa_transfered'] = count_not_managed_ewa_transfered
                    building_ewa_data[building.id]['not_managed_ewa_not_transfered'] = count_not_managed_ewa_not_transfered
                else:
                    building_ewa_data.update({ building.id:{
                                                'flat_count' : len(building.module_ids),
                                                'building':building.name,
                                                'managed_ewa_transfered' :count_managed_ewa_transfered,
                                                'managed_ewa_not_transfered':count_managed_ewa_not_transfered,
                                                'not_managed_ewa_transfered':count_not_managed_ewa_transfered,
                                                'not_managed_ewa_not_transfered':count_not_managed_ewa_not_transfered,
                        
                                                }})
#                 building_ewa_data = self.flat_ewa_amount_merge(building_ewa_data,building, product)
        
        
        row = 13
        count = 1
        for k,v in building_ewa_data.items():
            worksheet.write(row,0, count ,table_value_format)
            worksheet.write(row, 1, v['building'], table_value_format)
            worksheet.write(row, 2, v['flat_count'], table_value_format)
            worksheet.write(row, 3, v['managed_ewa_transfered'], table_value_format)
            worksheet.write(row, 4, v['not_managed_ewa_transfered'], table_value_format)
            worksheet.write(row, 5, v['managed_ewa_not_transfered'], table_value_format)
            worksheet.write(row, 6, v['not_managed_ewa_not_transfered'], table_value_format)
            count+=1
            row += 1
                    
            