from odoo import models,_
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.exceptions import UserError,Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from dateutil.rrule import rrule, DAILY


import logging
from reportlab.lib.units import mm
_logger = logging.getLogger(__name__)



class CollectionReport(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_colection_report'
    _description = 'Collection Report'
    _inherit = 'report.report_xlsx.abstract'

    
    def generate_xlsx_report(self, workbook, data, wiz):
         

        worksheet= workbook.add_worksheet('Collection Report')
        
        title1 = workbook.add_format({'align': 'left','bold': True, 'size': 10,})
        title1.set_text_wrap()
        title = workbook.add_format({'align': 'center','valign':'center','bold': True, 'size': 14,})
        heading_format = workbook.add_format({'align': 'center','size': 20,'bold':True})
        heading_bold_left = workbook.add_format({'size': 11,'bold':True,'align': 'left'})
        heading_bold_right = workbook.add_format({'size': 11,'bold':True,'align': 'right'})
        text_heading_bold_left = workbook.add_format({'size': 10,'bold':True,'align': 'left'})
        text_heading_bold_left_fg1 = workbook.add_format({'size': 10,'bold':True,'align': 'left','fg_color': '#FFA500'})
        text_heading_bold_center = workbook.add_format({'align': 'center','size': 10,'bold':True})
        number_format = workbook.add_format({'size': 10,'align': 'right','num_format': '#,###0.000'})
        table_value_format = workbook.add_format({'align': 'right','size': 10})
        number_format_bold_right = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000'})
        number_format_bold_right_fg = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000','fg_color': '#FFFF00'})
        number_format_bold_right_fg1 = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000','fg_color': '#FFA500'})

        formater = workbook.add_format({'border': 1})
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        
        worksheet.set_row(1, 25)
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
         
        
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
            
        
        worksheet.merge_range('D1:E5','%s \n %s \n %s \n %s \n %s \n  %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.09, 'y_scale': 0.09})
            
        
#         worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.60, 'y_scale': 0.60})

        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        wiz_from_date = datetime.strptime(str(wiz.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        wiz_to_date = datetime.strptime(str(wiz.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        wiz_building = wiz.building_id
        
        worksheet.merge_range('D7:E7','Collection Report',title)
        
        worksheet.write('A9','From Date',heading_bold_left)
        worksheet.write('B9',wiz_from_date,heading_bold_right)
        
        worksheet.write('E9','To Date',heading_bold_right)
        worksheet.write('F9',wiz_to_date,heading_bold_right)
        
        worksheet.write('A10','Building',heading_bold_left)
        worksheet.write('B10',wiz_building.name,heading_bold_right)
        
        
        
        
        worksheet.write('A12', 'Sr.#',text_heading_bold_left)
        worksheet.write('B12', 'Building Name',text_heading_bold_left)
        worksheet.write('C12', 'Flat No',text_heading_bold_left)
        worksheet.write('D12', 'Service Charges',text_heading_bold_left)
        worksheet.write('E12', 'Tabreed',text_heading_bold_left)
        worksheet.write('F12', 'EWA',text_heading_bold_left)
        worksheet.write('G12', 'Internet',text_heading_bold_left)
        worksheet.write('H12', 'Rent',text_heading_bold_left)
        worksheet.write('I12', 'Maintenance',text_heading_bold_left)
        worksheet.write('J12', 'Renting Commission',text_heading_bold_left)
        worksheet.write('K12', 'Resale Commission',text_heading_bold_left)
        worksheet.write('L12', 'Mgt Fees',text_heading_bold_left)
        worksheet.write('M12', 'Other',text_heading_bold_left)
        worksheet.write('N12', 'Total',text_heading_bold_left)
        
        
       
        
        params = self.env['ir.config_parameter'].sudo()  
        
        ewa_journal_id = params.get_param('zb_bf_custom.ewa_journal_id')
        internet_journal_id = params.get_param('zb_bf_custom.internet_journal_id')
        service_journal_id = params.get_param('zb_bf_custom.service_journal_id')
        tabreed_journal_id = params.get_param('zb_bf_custom.tabreed_journal_id')
#         osn_journal_id = params.get_param('zb_bf_custom.osn_product_id')
        
        commission_journal_id = params.get_param('zb_bf_custom.commission_journal_id')
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id')
        resale_commission_journal_id = params.get_param('zb_bf_custom.resale_commission_journal_id')
        maintenance_journal_id = params.get_param('zb_bf_custom.maintenance_journal_id')
        management_fee_journal_id = params.get_param('zb_bf_custom.management_fee_journal_id')
        
        account_excluded = params.get_param('zb_bf_custom.collection_excluded_account_ids')
        
#         product_list = [int(ewa_product_id),int(internet_product_id),int(service_product_id),int(tabreed_product_id)]
        
        account_list=[]
        if account_excluded:
            account=account_excluded[1:-1].split(',')
            
            for rec in account:
                if rec:
                    account_list.append(int(rec))
        
        if not account_list:
            raise Warning(_("""Please Configure Account Types To Be Excluded """))
    
        self._cr.execute('''
        SELECT line.id 
        FROM account_move_line line
        JOIN account_move move ON move.id = line.move_id
        JOIN account_account ac ON ac.id = line.account_id
        JOIN account_account_type type ON type.id = ac.user_type_id AND ac.user_type_id NOT IN %s
        WHERE move.state = 'posted' 
        AND line.date >= %s and line.date <= %s
        AND move.building_id in (select id from zbbm_building where id=%s)
        
         ''',[tuple(account_list),wiz_from_date,wiz_to_date,wiz_building.id])
        moves=self._cr.fetchall()
        refund = 0.000
        service_charge = 0.000
        tabreed = 0.000
        ewa = 0.000
        internet = 0.000
        line_dict = {}
        line_list =[]
        commission = 0.000
        resale_commission = 0.000
        rent = 0.000
        maintenance = 0.000
        other = 0.000
        management = 0.000
        
        for line in moves:
            line_id  = self.env['account.move.line'].browse(line[0])
            service_charge = 0.000
            tabreed = 0.000
            ewa = 0.000
            internet = 0.000
            commission = 0.000
            resale_commission = 0.000
            rent = 0.000
            maintenance = 0.000
            other = 0.000
            management = 0.000
            key =line_id.move_id.building_id.name,line_id.move_id.module_id.name
#             if line_id.product_id:
            if line_id.journal_id.id == int(service_journal_id):
                if line_id.move_id.type == 'out_refund':
                    service_charge = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    service_charge = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                     service_charge = (line_id.debit if line_id.debit >0.000 else line_id.credit)
            elif line_id.journal_id.id == int(tabreed_journal_id):
                if line_id.move_id.type == 'out_refund':
                    tabreed = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    tabreed = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                     tabreed = (line_id.debit if line_id.debit >0.000 else line_id.credit)
            elif line_id.journal_id.id == int(ewa_journal_id):
                if line_id.move_id.type == 'out_refund':
                    ewa = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    ewa = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                     ewa = (line_id.debit if line_id.debit >0.000 else line_id.credit)
            elif line_id.journal_id.id == int(internet_journal_id):
                if line_id.move_id.type == 'out_refund':
                    internet = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    internet = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                         internet = (line_id.debit if line_id.debit >0.000 else line_id.credit)

            elif line_id.journal_id.id  == int(rent_invoice_journal_id):
                if line_id.move_id.type == 'out_refund':
                    rent = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    rent = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                 rent = line_id.debit if line_id.debit >0.000 else line_id.credit
            elif line_id.journal_id.id  == int(commission_journal_id):
                if line_id.move_id.type == 'out_refund':
                    commission = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    commission = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                 commission = line_id.debit if line_id.debit >0.000 else line_id.credit
            elif line_id.journal_id.id  == int(resale_commission_journal_id):
                if line_id.move_id.type == 'out_refund':
                    resale_commission = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    resale_commission = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                 resale_commission = line_id.debit if line_id.debit >0.000 else line_id.credit
            elif line_id.journal_id.id  == int(maintenance_journal_id):
                if line_id.move_id.type == 'out_refund':
                    maintenance = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    maintenance = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                 maintenance = line_id.debit if line_id.debit >0.000 else line_id.credit
            elif line_id.journal_id.id  == int(management_fee_journal_id):
                if line_id.move_id.type == 'out_refund':
                    management = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    management = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                 management = line_id.debit if line_id.debit >0.000 else line_id.credit
            else:
                if line_id.move_id.type == 'out_refund':
                    other = -(line_id.move_id.amount_total-line_id.move_id.amount_residual)
                else:
                    other = line_id.move_id.amount_total-line_id.move_id.amount_residual
#                 other = line_id.debit if line_id.debit >0.000 else line_id.credit
            
            
            
            if key in line_dict:
                line_dict[key]['building'] = line_id.move_id.building_id.name
                line_dict[key]['module'] = line_id.move_id.module_id.name or ''
                line_dict[key]['service_charge'] += service_charge
                line_dict[key]['tabreed'] += tabreed
                line_dict[key]['EWA'] += ewa
                line_dict[key]['Internet'] += internet
                line_dict[key]['rent'] += rent
                line_dict[key]['commission'] += commission
                line_dict[key]['resale_commission'] += resale_commission
                line_dict[key]['maintenance'] += maintenance
                line_dict[key]['management'] += management
                line_dict[key]['other'] += other
            else:
                line_dict[key] = {
                                'building':line_id.move_id.building_id.name,
                                'module':line_id.move_id.module_id.name or '',
                                'service_charge':service_charge,
                                'tabreed':tabreed,
                                'EWA':ewa,
                                'Internet':internet,
                                'rent':rent,
                                'commission':commission,
                                'resale_commission':resale_commission,
                                'maintenance':maintenance,
                                'management':management,
                                'other':other,}
                
        line_list.append(line_dict)
        
        row=12
        
        for vals in line_list:
            count = 1
            total = 0.000
            for dicts in vals.values():
                worksheet.write(row,0,count,table_value_format)
                worksheet.write(row,1,dicts.get('building'),table_value_format)
                worksheet.write(row,2,dicts.get('module'),table_value_format)
                worksheet.write(row,3,dicts.get('service_charge'),number_format)
                worksheet.write(row,4,dicts.get('tabreed'),number_format)
                worksheet.write(row,5,dicts.get('EWA'),number_format)
                worksheet.write(row,6,dicts.get('Internet'),number_format)
                worksheet.write(row,7,dicts.get('rent'),number_format)
                worksheet.write(row,8,dicts.get('maintenance'),number_format)
                worksheet.write(row,9,dicts.get('commission'),number_format)
                worksheet.write(row,10,dicts.get('resale_commission'),number_format)
                worksheet.write(row,11,dicts.get('management'),number_format)
                worksheet.write(row,12,dicts.get('other'),number_format)
                total = dicts.get('service_charge') + dicts.get('tabreed') + dicts.get('EWA') + dicts.get('Internet') + dicts.get('rent') + dicts.get('maintenance')+ dicts.get('commission') + dicts.get('resale_commission') + dicts.get('management') + dicts.get('other')
                worksheet.write(row,13,total,number_format)
                count+=1
                row+=1
                
        
        
        
        
        
                
                
                
            
            
            
