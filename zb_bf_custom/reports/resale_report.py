from odoo import models,_
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.exceptions import UserError,Warning

from dateutil.rrule import rrule, DAILY
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


import logging
from reportlab.lib.units import mm
_logger = logging.getLogger(__name__)



class ResaleReport(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_resale_report'
    _description = 'Resale Report'
    _inherit = 'report.report_xlsx.abstract'

    
    def generate_xlsx_report(self, workbook, data, wiz):
        
        worksheet= workbook.add_worksheet('Resale Report')
        
        title1 = workbook.add_format({'align': 'left','bold': True, 'size': 10,'text_wrap': True})
        title = workbook.add_format({'align': 'center','valign':'center','bold': True, 'size': 14,})
        heading_bold_left = workbook.add_format({'size': 10,'bold':True,'align': 'left'})
        heading_bold_right = workbook.add_format({'size': 10,'bold':True,'align': 'right'})
        text_heading_bold_left = workbook.add_format({'size': 10,'bold':True,'align': 'left'})
        text_heading_wrap = workbook.add_format({'size': 10,'bold':True,'align': 'left'})
        text_heading_wrap.set_text_wrap()
        table_value_format = workbook.add_format({'align': 'right','size': 10})
        number_format = workbook.add_format({'size': 10,'align': 'right','num_format': '#,###0.000'})
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        
        worksheet.set_row(11, 35)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
         
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
            
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        worksheet.merge_range('C1:D5','%s \n %s \n %s \n %s \n %s \n  %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.09, 'y_scale': 0.08})
        
        worksheet.merge_range('D7:E7','Resale Report',title)
        
        wiz_from_date = datetime.strptime(str(wiz.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        wiz_to_date = datetime.strptime(str(wiz.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        
        worksheet.write('A9','From Date',heading_bold_left)
        worksheet.write('B9',wiz_from_date,heading_bold_right)
        
        worksheet.write('C9','To Date',heading_bold_right)
        worksheet.write('D9',wiz_to_date,heading_bold_right)
        
        worksheet.write('A12', 'Building Name',text_heading_wrap)
        worksheet.write('B12', 'Flat No',text_heading_bold_left)
        worksheet.write('C12', 'Owner Name',text_heading_bold_left)
        worksheet.write('D12', 'Sale Value',text_heading_bold_left)
        worksheet.write('E12', 'Commission %',text_heading_bold_left)
        worksheet.write('F12', 'Commission Received Amount',text_heading_wrap)
        worksheet.write('G12', 'Direct/Agent',text_heading_bold_left)
        worksheet.write('H12', 'Property Advisor Name',text_heading_wrap)
        worksheet.write('I12', 'Agent Name',text_heading_bold_left)
        
        params = self.env['ir.config_parameter'].sudo()  
        
        resale_commsn_journal_id = params.get_param('zb_bf_custom.resale_commission_journal_id')
        
        if not resale_commsn_journal_id:
            raise Warning(_("""Please Configure Resale Commission Journal"""))
        
        moves = self.env['account.move'].search([('invoice_date','<=',wiz.to_date),('invoice_date','>=',wiz.from_date),('journal_id','=',int(resale_commsn_journal_id))])
        
        row = 13
        for line in moves:
            if line.partner_id == line.unit_id.owner_id:
                worksheet.write(row,0,line.building_id.name or '',table_value_format)
                worksheet.write(row,1,line.unit_id.name or '',table_value_format)
                worksheet.write(row,2,line.unit_id.owner_id.name or '',table_value_format)
                worksheet.write(row,3,line.unit_id.price,number_format)
                worksheet.write(row,4,line.building_id.resale_owner_commission_percent,table_value_format)
                worksheet.write(row,5,line.amount_untaxed,number_format)
                if line.unit_id.unit_agent_id:
                    worksheet.write(row,6,'Agent',table_value_format)
                else:
                    worksheet.write(row,6,'Direct',table_value_format)
                worksheet.write(row,7,line.unit_id.adviser_id.name or '',table_value_format)
                worksheet.write(row,8,line.unit_id.unit_agent_id.name or '',table_value_format)
                row+=1
            
        
        
        
        
        
        
        
        
        
        
        