from odoo import models
from datetime import datetime, timedelta, date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


import logging
_logger = logging.getLogger(__name__)


class TenantDepositDetailXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_tenant_deposit_details'
    _description = 'Tenant Deposit Details Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        worksheet = workbook.add_worksheet('Tenant Deposits')
        
        title1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 16,'border':2,'text_wrap': True,'bg_color':'#34495e','font_color':'#fdfefe'})
        cell_number_format = workbook.add_format({'align': 'right',
                                                  'valign': 'vcenter',
                                                  'bold': False, 'size': 12,
                                                  'num_format': '#,###0.000'})


        style = workbook.add_format({'bold': True,'align': 'center', 'text_wrap': True,'border':1,'valign': 'vcenter','size': 8})
        title2 = workbook.add_format({'bold': True,'align': 'center', 'text_wrap': True,'border':1,'valign': 'vcenter','size': 8})
        
        style2 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        style2_wrap = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter','text_wrap': True})
        # date_format = workbook.add_format({'num_format': 'dd/mm/yyyy','size': 10,})
        
        worksheet.merge_range('A6:I6', 'Tenant Deposit Details',title1)
        worksheet.write('A8', 'From Date:',title2)
        worksheet.write('C8', 'To Date:',title2)
        worksheet.set_row(10, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 13)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.write('A11', 'Sr.#', title2)
        worksheet.write('B11', 'Date', title2)
        worksheet.write('C11', 'Tenant', title2)
        worksheet.write('D11', 'Building', title2)
        worksheet.write('E11','Flat No', title2)
        worksheet.write('F11', 'Description', title2)
        worksheet.write('G11', 'Deposit Amount', title2)
        worksheet.write('H11', 'Collected Balance', title2)
        worksheet.write('I11', 'Due Balance', title2)
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        if partners.building_id :
            domain = [('agreement_start_date','<=',partners.to_date), ('agreement_start_date','>=',partners.from_date), ('building_id', '=', partners.building_id.id),('state','=','active')]
        else:
            domain = [('agreement_start_date','<=',partners.to_date), ('agreement_start_date','>=',partners.from_date),('state','=','active')]
            
        leases = self.env['zbbm.module.lease.rent.agreement'].search(domain)
        from_date = datetime.strptime(str(partners.from_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        to_date = datetime.strptime(str(partners.to_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        
        worksheet.write('B8', from_date, title2)
        worksheet.write('D8', to_date, title2)
        cmpny = self.env.user.company_id
        if self.env.user.company_id.logo:
            data = base64.b64decode(self.env.user.company_id.logo) 
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
        worksheet.merge_range('E1:H5','\n %s \n %s  %s \n %s \n %s \n %s'%(cmpny_name,street,street2 ,cmpny.city,country_id,email),title2)
        worksheet.merge_range('A1:B4','')
        worksheet.insert_image('A1:B4','logo.png',{'x_scale': 0.06, 'y_scale': 0.06,'x_offset': 60})
        count = 1
        row = 12
        column = 0
        for rec in leases:
            date = datetime.strptime(str(rec.agreement_start_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
#             receipt_id = self.env['account.move'].search([('type','=','out_receipt'),('lease_id','=',rec.id),('state','=','posted'),('partner_id','=',rec.tenant_id.id)])
            worksheet.write(row, column, count, style2)
            worksheet.write(row, column +1, date, style2)
            worksheet.write(row, column +2, rec.tenant_id.name, style2)
            worksheet.write(row, column +3, rec.building_id.name, style2)
            worksheet.write(row, column +4, rec.subproperty.name,style2)
            worksheet.write(row, column +5, rec.voucher_move_id.deposit_jv_desc if rec.voucher_move_id and rec.voucher_move_id.state =='posted' else '', style2_wrap)
            worksheet.write(row, column +6, rec.security_deposit, cell_number_format)
            worksheet.write(row, column +7, rec.voucher_move_id.amount_total - rec.voucher_move_id.amount_residual  if rec.voucher_move_id and rec.voucher_move_id.state =='posted'  else '',cell_number_format)
            worksheet.write(row, column +8, rec.voucher_move_id.amount_residual if rec.voucher_move_id and rec.voucher_move_id.state =='posted' else '', cell_number_format)
            worksheet.write(row, column +9, '', style2)
            row += 1
            count += 1
            
            
            
            
