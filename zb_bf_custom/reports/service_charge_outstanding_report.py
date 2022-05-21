from odoo import models,_
from datetime import datetime, timedelta,date
from odoo.exceptions import AccessError,UserError,Warning

import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ServiceChargeOutstandingXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.service_charge_outstanding_report'
    _description = 'Service Charge Outstanding Report'
    _inherit = 'report.report_xlsx.abstract'


    
    def generate_xlsx_report(self, workbook, data,wiz):
         
#         periods, product_data = self.get_aging_data(partners)

        worksheet= workbook.add_worksheet('Building-Wise Service Charge Outstanding Analysis')
        
        title1 = workbook.add_format({'align': 'left',
                                                      'bold': True, 'size': 10,})
        heading_format = workbook.add_format({'bold':True,'align':'center','valign': 'vcenter','size': 13})
        subheading = workbook.add_format({'bold':True,'align':'center','valign': 'vcenter','size': 10,'border':1})
        style = workbook.add_format({'size': 10,'bold':True,'border':1})
        style1 = workbook.add_format({'size': 10,'bold':True,'border':1})
        style1.set_text_wrap()
        style2 = workbook.add_format({'size': 10,'align': 'right', 'valign': 'vcenter','num_format': '#,##0.000'})
        title2 =workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        style3 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        no_border = workbook.add_format({'size': 10,'bold':True})
#         border2 = workbook.add_format({'size': 10,'bold':True,'border':1})
#         border2.set_text_wrap()
        
        
        worksheet.set_row(11, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 17)
        worksheet.set_column('D:D', 17)
        worksheet.set_column('E:E', 16)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 17)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 17)
        worksheet.set_column('J:J', 17)
        worksheet.set_column('K:K', 13)
        worksheet.set_column('L:L', 17)
        worksheet.set_column('M:M', 17)
        worksheet.set_column('Q:Q', 17)
        worksheet.set_column('P:P', 17)
        worksheet.set_column('Q:Q', 17)
        worksheet.set_column('S:S', 13)
        
        worksheet.merge_range('E7:I7', 'Service Charge Outstanding Movement Analysis - Building wise',heading_format)
        worksheet.write('A9', 'From Date:',no_border)
        worksheet.write('A10', 'To Date:',no_border)
        worksheet.write('C9', 'Building Name:',no_border)
        worksheet.write('C10', 'Expense Name:',no_border)
        worksheet.write('D10', 'Service Charge',title2)
        worksheet.merge_range('I11:K11','Opening Balance',subheading)
        worksheet.merge_range('L11:O11','Receipts',subheading)
        worksheet.merge_range('P11:S11','Closing Balance',subheading)
        
        worksheet.write('A12', 'Sr.#',style)
        worksheet.write('B12', 'Flat No.',style)
        worksheet.write('C12', 'Owner Name',style)
        worksheet.write('D12', 'Mgt Status',style)
        worksheet.write('E12',"Owner's Contact Number 1",style1) 
        worksheet.write('F12', "Owner's Contact Number2",style1)
        worksheet.write('G12', "Owner's Email 1",style)
        worksheet.write('H12', "Owner's Email 2",style)
        worksheet.write('K12','Admin Fees',style)
        worksheet.write('N12', 'Admin Fees',style1)
        worksheet.write('O12','Total Collection',style1) 
        worksheet.write('R12', 'Admin Fees',style1)
        worksheet.write('S12', 'Total O/S',style)
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        data=base64.b64decode(company_logo) 
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
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
            
        worksheet.merge_range('C1:D5','%s \n %s \n %s \n %s \n %s \n  %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.065, 'y_scale': 0.08})
        
        params = self.env['ir.config_parameter'].sudo()  
        journall_id=params.get_param('zb_bf_custom.service_journal_id') or False,
        
        admin_fee_journal_id=params.get_param('zb_bf_custom.admin_fee_journal_id') or False,
#         if not journall_id[0]:
#             raise Warning(_("""Please configure service journal in the Accounting Settings"""))
        
        admin_fee_pdt_id = params.get_param('zb_bf_custom.admin_fee_product_id') or False,
#         if admin_fee_pdt_id[0] == False:
#             raise Warning(_("""Please configure Admin Fees Product in the Accounting Settings"""))
        
        servic_prod = params.get_param('zb_bf_custom.service_product_id') or False,
        
#         if not servic_prod:
#                 raise Warning(_("""Please configure Service Product in the Accounting Settings"""))
        
        
        
        if wiz.from_date and wiz.to_date and wiz.building_id:
            
            from_date = datetime.strptime(str(wiz.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            to_date = datetime.strptime(str(wiz.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            worksheet.write('B9',from_date,title2)
            worksheet.write('B10',to_date,title2)
            worksheet.write('D9',wiz.building_id.name,title2)
            
            owner_ids = self.env['res.partner'].search([('owner','=',True)])
            
            
            current_from_date = date(wiz.from_date.year,wiz.from_date.month,wiz.from_date.day)
            format_current_from_date = datetime.strptime(str(current_from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            current_to_date = date(wiz.to_date.year,wiz.to_date.month,wiz.to_date.day)
            format_current_to_date = datetime.strptime(str(current_to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            
            prev_from_date = date(wiz.from_date.year-1,wiz.from_date.month,wiz.from_date.day)
            format_prev_from_date = datetime.strptime(str(prev_from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            prev_to_date = date(wiz.to_date.year-1,wiz.to_date.month,wiz.to_date.day)
            format_prev_to_date = datetime.strptime(str(prev_to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            
            worksheet.write('I12', 'Current Amount (%s to %s)'%(format_current_from_date,format_current_to_date),style1)
            worksheet.write('J12', 'Previous Amount (%s to %s)'%(format_prev_from_date,format_prev_to_date),style1)
#             worksheet.write('L12', 'Current VAT Amount (%s to %s)'%(format_current_from_date,format_current_to_date),style1)
#             worksheet.write('M12','Previous VAT Amount (%s to %s)'%(format_prev_from_date,format_prev_to_date),style1) 
            worksheet.write('L12', 'Current Amount (%s to %s)'%(format_current_from_date,format_current_to_date),style1)
            worksheet.write('M12', 'Previous Amount (%s to %s)'%(format_prev_from_date,format_prev_to_date),style1)
#             worksheet.write('Q12', 'Current VAT Amount (%s to %s)'%(format_current_from_date,format_current_to_date),style1)
#             worksheet.write('R12', 'Previous VAT Amount (%s to %s)'%(format_prev_from_date,format_prev_to_date),style1)
            worksheet.write('P12', 'Current Amount (%s to %s)'%(format_current_from_date,format_current_to_date),style1)
            worksheet.write('Q12', 'Previous Amount (%s to %s)'%(format_prev_from_date,format_prev_to_date),style1)
#             worksheet.write('W12', 'Current VAT Amount (%s to %s)'%(format_current_from_date,format_current_to_date),style1)
#             worksheet.write('X12', 'Previous VAT Amount (%s to %s)'%(format_prev_from_date,format_prev_to_date),style1)
            
            owner_service_dict = {}
            
            
            for owner in owner_ids:
                service_invoice_ids = self.env['account.move'].search(['|',('type','=','out_refund'),('type','=','out_invoice'),('module_id.owner_id','=',owner.id),('journal_id','in',[int(journall_id[0]),int(admin_fee_journal_id[0])]),('building_id','=',wiz.building_id.id),
                                                    ('state','=','posted'),('invoice_date','>=',prev_from_date),('invoice_date','<=',current_to_date)])
                
                current_period_inv = service_invoice_ids.filtered(lambda r: r.invoice_date >= current_from_date and r.invoice_date <= current_to_date)
                
                prev_period_inv = service_invoice_ids.filtered(lambda r: r.invoice_date >= prev_from_date and r.invoice_date <= prev_to_date)
                
                for inv in service_invoice_ids:
#                     service_dict_key = inv.module_id.name,inv.module_id.owner_id.name
                    service_dict_key = inv.module_id,inv.module_id.owner_id
                    
                    for line in inv.invoice_line_ids:
                        
                        
                        if line.product_id.id == int(servic_prod[0]) and line.journal_id.id == int(journall_id[0]):
                            if service_dict_key in owner_service_dict:
                                
                                if inv in prev_period_inv:
                                    owner_service_dict[service_dict_key]['prev_period_sc'] += line.price_total
#                                     owner_service_dict[service_dict_key]['prev_period_vat'] += (inv.amount_tax)
                                    owner_service_dict[service_dict_key]['prev_period_receipt'] += (inv.amount_total-inv.amount_residual)
                                 
                                elif inv in current_period_inv:
                                    owner_service_dict[service_dict_key]['current_period_sc'] += line.price_total
#                                     owner_service_dict[service_dict_key]['current_period_vat'] += (inv.amount_tax)
                                    owner_service_dict[service_dict_key]['current_period_receipt'] += (inv.amount_total-inv.amount_residual)
                            else:
                                if inv in prev_period_inv:
                                    previous_amt = line.price_total
#                                     previous_vat = (inv.amount_tax)
                                    previous_receipt = (inv.amount_total-inv.amount_residual)
                                    current_amt=0.0
#                                     current_vat=0.0
                                    current_receipt = 0.0
                                     
                                elif inv in current_period_inv:
                                    current_amt = line.price_total
#                                     current_vat = (inv.amount_tax)
                                    current_receipt = (inv.amount_total-inv.amount_residual)
                                    previous_amt=0.0
#                                     previous_vat = 0.0
                                    previous_receipt = 0.0
                                owner_service_dict.update({service_dict_key:{'prev_period_sc':previous_amt,
                                                                            'current_period_sc':current_amt,
#                                                                             'current_period_vat':current_vat,
#                                                                             'prev_period_vat':previous_vat,
                                                                            'prev_period_receipt':previous_receipt,
                                                                            'current_period_receipt':current_receipt,
                                                                            'opening_admin_fee':0.0,
                                                                            'receipt_admin_fee':0.0}})
                       
                        elif line.product_id.id == int(admin_fee_pdt_id[0]) and line.journal_id.id == int(admin_fee_journal_id[0]):
                            
                            if service_dict_key in owner_service_dict:
                                if inv.invoice_date >= wiz.from_date and inv.invoice_date <= wiz.to_date:
                                    owner_service_dict[service_dict_key]['opening_admin_fee'] += (line.price_total)
                                    owner_service_dict[service_dict_key]['receipt_admin_fee'] += (inv.amount_total - inv.amount_residual)
                            else:
                                if inv.invoice_date >= wiz.from_date and inv.invoice_date <= wiz.to_date:
                                    opening_bal_admin_fee = (line.price_total)
                                    receipt_admin_fee = (inv.amount_total - inv.amount_residual)
                                 
                                    owner_service_dict.update({service_dict_key:{'opening_admin_fee':opening_bal_admin_fee,
                                                                                 'receipt_admin_fee':receipt_admin_fee
                                                                            }})
                    
                    
                
            count=1
            row = 13
            column=0
            for key,values in owner_service_dict.items():
                worksheet.write(row,column,count,style3)
                worksheet.write(row,column+1,key[0].name,style3)
                worksheet.write(row,column+2,key[1].name,style3)
                if key[0].managed:
                    worksheet.write(row,column+3,'Managed',style3)
                else:
                    worksheet.write(row,column+3,'Not Managed',style3)
                worksheet.write(row,column+4,key[1].phone or '',style3)
                worksheet.write(row,column+5,key[1].mobile or '',style3)
                worksheet.write(row,column+6,key[1].email or '',style3)
                worksheet.write(row,column+7,'',style2)
                worksheet.write(row,column+8,values['current_period_sc'],style2)
                worksheet.write(row,column+9,values['prev_period_sc'],style2)
                worksheet.write(row,column+10,values['opening_admin_fee'],style2)
#                 worksheet.write(row,column+11,values['current_period_vat'],style2)
#                 worksheet.write(row,column+12,values['prev_period_vat'],style2)
                worksheet.write(row,column+11,values['current_period_receipt'],style2)
                worksheet.write(row,column+12,values['prev_period_receipt'],style2)
                worksheet.write(row,column+13,values['receipt_admin_fee'],style2)
#                 worksheet.write(row,column+16,0,style2)
#                 worksheet.write(row,column+17,0,style2)
                worksheet.write_formula(row,column+14,'{=SUM(L%s:N%s)}'%(row+1,row+1),style2)
                worksheet.write(row,column+15,values['current_period_sc']-values['current_period_receipt'],style2)
                worksheet.write(row,column+16,values['prev_period_sc']-values['prev_period_receipt'],style2)
                worksheet.write(row,column+17,values['opening_admin_fee']-values['receipt_admin_fee'],style2)
#                 worksheet.write(row,column+22,values['current_period_vat']-0,style2)
#                 worksheet.write(row,column+23,values['prev_period_vat']-0,style2)
                worksheet.write_formula(row,column+18,'{=SUM(P%s:R%s)}'%(row+1,row+1),style2)
                row+=1
                count+=1
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        