from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
import xlsxwriter
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class TenantEWAExcessXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_tenant_ewa_excess'
    _description = 'Tenantwise EWA Excess Report'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, wiz):
        
        worksheet= workbook.add_worksheet('Tenant-wise EWA Excess Report')
        style1 = workbook.add_format({'size': 10,'bold': True,'align': 'left'})
        # date_format = workbook.add_format({'num_format': 'dd/mm/yyyy','size': 10,'align': 'center', 'valign': 'vcenter'})
        style = workbook.add_format({'align': 'center', 'valign': 'vcenter','size': 10})
        heading_format = workbook.add_format({'align': 'center','valign': 'vcenter','bold': True,'size': 14,})
        address_format = workbook.add_format({'align': 'left','valign': 'vcenter','bold': True,'size': 10,'text_wrap': True})
        wrap = workbook.add_format({'size': 10,'bold': True,'align': 'left'})
        wrap.set_text_wrap()   
        amount_format = workbook.add_format({'align': 'right', 'valign': 'vcenter','size': 10,'num_format': '#,##0.000'})                           
        
#         worksheet.set_row(0, 50)
        worksheet.set_row(4, 20)
        worksheet.set_row(9, 30)
        worksheet.set_row(12, 45)
        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 45)
        worksheet.set_column('C:C', 13)
        worksheet.set_column('D:D', 16)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        
        worksheet.merge_range('A6:E6', 'Tenant Wise Excess EWA Report', heading_format)
        worksheet.write('A8', 'From Date:',style1)
        worksheet.write('A9', 'Building:',style1)
        worksheet.write('A10', 'Flat No.:',style1)
        worksheet.write('A11', 'Area Manager:',style1)
        worksheet.write('D8', 'To Date:',style1)
        worksheet.write('D9', 'Tenant Name:',style1)
        worksheet.write('D10', 'Property Advisor Name:',wrap)
        worksheet.write('A13', 'Sr.#',style1)
        worksheet.write('B13', 'Description',style1)
        worksheet.write('C13', 'EWA Consumption',wrap)
        worksheet.write('D13', 'EWA Limited Amount',wrap)
        worksheet.write('E13', 'EWA Excess Consumption Payable',wrap)
        
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
          
        #Company Details     
        worksheet.merge_range('C1:D5','%s \n %s \n %s \n %s \n %s'%(company_name,street,street2 ,city,country_id),address_format)
        worksheet.insert_image('A1:A4','picture.png', {'image_data': logo,'x_offset': 0,'x_scale': 0.13, 'y_scale': 0.13})

        #Date details
        from_date = datetime.strptime(str(wiz.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        to_date = datetime.strptime(str(wiz.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        worksheet.write('B8',from_date,style)
        worksheet.write('E8',to_date, style)
        
        building_id = wiz.building_id
        tenant_id = wiz.tenant_id
        worksheet.write('E9',tenant_id.name or '',style)
        worksheet.write('B10',tenant_id.module_id.name, style)
#         worksheet.write('D9',)
        worksheet.write('B9',building_id.name,style)
        worksheet.write('B11',building_id.area_manager and building_id.area_manager.id or '',style)
        if tenant_id:
            lease_ids = self.env['zbbm.module.lease.rent.agreement'].search([('tenant_id','=', tenant_id.id),('building_id','=',building_id.id)])
            params = self.env['ir.config_parameter'].sudo() 
            ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id') or False
            product = self.env['product.product'].search([('id','=',ewa_product_id)])
            
            if not ewa_product_id:
                raise Warning(_("""Please configure EWA Service Product in the Accounting Settings"""))
            if len(lease_ids) > 0:
               services_raw_ids = self.env['raw.services'].search([('product_id','=',product.id),('service_date','>=', from_date),('service_date','<=',to_date),('lease_agreement_id','in',lease_ids.ids)]) 
    #            
            row=14
            count=1
            flat_list = []
            pa_list =[]
            for service in services_raw_ids:
                description = ''
                owner_share = 0
                invoice_ids = self.env['account.move'].search([('state','=','posted'),('raw_service_id.id','=',service.id),('type','in',['out_invoice','out_refund'])])
                service_config_ids = self.env['zbbm.services'].search([('product_id','=',product.id),('module_id','=',service.module_id.id)])
                    
                for inv in invoice_ids:
                    for line in inv.invoice_line_ids:
                        if inv.partner_id.owner:
                            owner_share = inv.amount_untaxed
                            if line.product_id and line.product_id.id == product.id:
                                description = line.name
                        elif inv.partner_id.is_tenant:
                            tenant_share = inv.amount_untaxed
                            if line.product_id and line.product_id.id == product.id:
                                description = line.name
                                
                if service.module_id.name not in flat_list:
                    flat_list.append(service.module_id.name)
                if service.lease_agreement_id.adviser_id and service.lease_agreement_id.adviser_id.name not in pa_list:
                    pa_list.append(service.lease_agreement_id.adviser_id.name)
                     
                month = datetime.strptime(str(service.service_date), "%Y-%m-%d").strftime('%B')
                if not description:
                    description = '%s-%s'%(month,service.amount)
                    
                if len(service_config_ids) > 0:
                   service_config_obj = service_config_ids[0]
                   owner_share = service_config_obj.owner_share
                   
                excess = owner_share - service.amount
                if excess < 0:
                    excess = excess * -1
                else:
                    excess = excess
                     
                worksheet.write('B10',','.join(flat_list), style) 
                worksheet.write('E10',','.join(pa_list),style)
   
                worksheet.write(row,0,count or '',style)
                worksheet.write(row,1,description or '',style)
                worksheet.write(row,2,service.amount or 0.0,amount_format)
                worksheet.write(row,3,owner_share or 0.0,amount_format)
                worksheet.write(row,4,excess or 0.0,amount_format)
                row=row+1
                count=count+1
        
        
        