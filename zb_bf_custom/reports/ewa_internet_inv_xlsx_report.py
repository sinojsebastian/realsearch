from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
import xlsxwriter


import logging
_logger = logging.getLogger(__name__)


class EWAInternetInvXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_ewa_internet_inv'
    _description = 'EWA / Batelco Internet Invoice Report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, wiz):
        print(wiz,data,self._context,'ppppppppppppp')
        
        worksheet= workbook.add_worksheet('EWA / Batelco Internet Invoice Report')
        bold = workbook.add_format({'size': 10,'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy','size': 10})
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
        
        worksheet.merge_range('A5:H5', 'Journal Voucher', heading_format)
    
        worksheet.write('A6', 'Voucher Number:',bold)
        worksheet.write('A7', 'Date:',bold)
        worksheet.write('A8', 'Building Name:',bold)
        worksheet.write('A9', 'Vendor:',bold)
        worksheet.write('A10', 'Payment Amount:',bold)
        worksheet.write('A11', 'Reference:',bold)
        
        worksheet.write('A13', 'Flat No.',bold)
        worksheet.write('B13','Party Name',bold) 
        worksheet.write('C13', 'Mgt Status',bold)
        worksheet.write('D13', 'Occupancy Status',bold)
        worksheet.write('E13', 'Paid by',bold)
        worksheet.write('F13','Billed to',bold) 
        worksheet.write('G13', 'Internet Line No.',bold)
        worksheet.write('H13', 'Invoice No.',bold)
        worksheet.write('I13','Invoice Date',bold) 
        worksheet.write('J13', 'Description',bold)
        worksheet.write('K13', 'Amount',bold)

        
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
        worksheet.insert_image(0,0,'picture.png', {'image_data': logo,'x_offset': 0,'x_scale': 0.75, 'y_scale': 0.75})

#         date = datetime.strptime(str(wiz.date),'%Y-%m-%d').strftime('%m/%d/%Y')
#         worksheet.write('B7',date,date_format)
#         building_id=wiz.building_id
#         worksheet.write('B8',building_id.name,style)
        
        params = self.env['ir.config_parameter'].sudo()  
        ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id')
        if not ewa_product_id:
            raise Warning(_("""Please configure EWA Service Product in the Accounting Settings"""))
        
        internet_product_id = params.get_param('zb_bf_custom.internet_product_id')
        if not internet_product_id:
            raise Warning(_("""Please configure Internet Service Product in the Accounting Settings"""))
        
        #EWA Section 
        ewa_obj = self.env['product.product'].browse(ewa_product_id[0])
        print('pppppppppp',ewa_obj)
        if ewa_obj.service_product_partner_id:
            if wiz.pv_id.partner_id.id == ewa_obj.service_product_partner_id.id:
               service_ids = self.env['zbbm.services'].search([('service_id','=',ewa_obj.id),('module_id','=',wiz.module_id.id)])
               
        #Internet Section      
        internet_obj = self.env['product.product'].browse(internet_product_id[0])
        if internet_obj.service_product_partner_id:
            if wiz.pv_id.partner_id.id == ewa_obj.service_product_partner_id.id:
               service_ids = self.env['zbbm.services'].search([('service_id','=',internet_obj.id),('module_id','=',wiz.module_id.id)])
               
        if len(service_ids) >0:
            acc_no = service_ids[0].account_no 
            if service_ids[0].trf_status:
               bill_to = wiz.module_id.owner_id and wiz.module_id.owner_id.id or ''
               paid_by = wiz.module_id.owner_id and wiz.module_id.owner_id.id or ''
            else:
                bill_to = 'Real Search'
                paid_by = 'Real Search'
        row=14
        for pv_line in wiz.pv_id.payment_line_ids:
            description = ''
            for inv_line in pv_line.inv_id:
                description += inv_line.name
            
            worksheet.write(row,0,pv_line.inv_id.module_id and pv_line.invoice_id.module_id.name  or '',style)
            worksheet.write(row,1,pv_line.inv_id.partner_id and pv_line.invoice_id.partner_id.name or '',style)
            worksheet.write(row,2,'Yes' if pv_line.inv_id.module_id and pv_line.inv_id.module_id.managed  else 'No',style)
            worksheet.write(row,3,pv_line.inv_id.module_id and pv_line.inv_id.module_id.state,style)
            worksheet.write(row,4, bill_to,style)
            worksheet.write(row,5,paid_by,style)
            worksheet.write(row,7,acc_no or '',style)
            worksheet.write(row,4,pv_line.inv_id.number ,style)
            worksheet.write(row,4,pv_line.inv_id.invoice_date ,style)
            worksheet.write(row,4,description ,style)
            worksheet.write(row,4,pv_line.allocation ,style)
            
            row=row+1
        
        
        