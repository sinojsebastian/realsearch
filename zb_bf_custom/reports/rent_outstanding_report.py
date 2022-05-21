from odoo import models,_
from datetime import datetime, timedelta,date
from odoo.exceptions import AccessError,UserError,Warning
from calendar import monthrange
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class RentOutstandingXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_rent_outstanding_details'
    _description = 'Rent Outstanding Report'
    _inherit = 'report.report_xlsx.abstract'


    
    def generate_xlsx_report(self, workbook, data,wiz):
         
#         periods, product_data = self.get_aging_data(partners)

        worksheet= workbook.add_worksheet('Rent Outstanding Details')

        title1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 16,'border':2,'text_wrap': True})
        title3 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 9,'border':2,'text_wrap': True})
        
        cell_number_format = workbook.add_format({'align': 'right',
                                                  'valign': 'vcenter',
                                                  'bold': False, 'size': 12,
                                                  'num_format': '#,###0.000'})


        style = workbook.add_format({'bold': True,'align': 'center', 'text_wrap': True,'border':1,'valign': 'vcenter','size': 8})
        title2 = workbook.add_format({'bold': True,'align': 'center', 'text_wrap': True,'border':1,'valign': 'vcenter','size': 8})
        
        style2 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        style2_wrap = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter','text_wrap': True})
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        date = datetime.strptime(str(wiz.date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
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
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 25)
        worksheet.set_column('M:M', 25)
        worksheet.set_column('N:N', 12)
        worksheet.set_column('O:O', 25)
        worksheet.merge_range('E7:H7', 'Rent Outstanding',title1)
        worksheet.write('A11', 'Sr.#', title2)
        worksheet.write('B11', 'Building Name', title2)
        worksheet.write('C11', 'Flat No', title2)
        worksheet.write('D11','Tenant Name', title2)
        worksheet.write('E11', 'Telephone', title2)
        worksheet.write('F11', 'Mobile', title2)
        worksheet.write('G11', 'Email', title2)
        worksheet.write('H11', 'Property Advisor', title2)
        worksheet.write('I11', 'Area Manager', title2)
        worksheet.write('J11', 'Due Date', title2)
        worksheet.write('K11', 'Overdue  Months', title2)
        worksheet.write('L11', 'Pending Amount for Previous Months', title2)
        worksheet.write('M11', 'Pending Amount for Selected Month', title2)
        worksheet.write('N11', 'Total Balance', title2)
        worksheet.write('O11', 'Remarks', title2)
        
        worksheet.write('A9', 'As On Date:', title3)
        worksheet.write('B9', date, title2)
        worksheet.write('D9', 'Building:' , title3)
        worksheet.write('E9', wiz.building_id.name, title2)
#         company_logo = self.env.user.company_id.logo
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
        worksheet.merge_range('A1:B7','')
        worksheet.insert_image('A1:B7','logo.png',{'x_scale': 0.10, 'y_scale': 0.11,'x_offset': 40})
        count = 1
        row = 11
        column = 0
        params = self.env['ir.config_parameter'].sudo()    
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        if not rent_invoice_journal_id :
            raise UserError(_('Please Configure Rent Invoice Journal'))

        month_date = datetime.strptime(str(wiz.date), DEFAULT_SERVER_DATE_FORMAT)
        month_first_date = month_date.replace(day=1)
        prev_month_last_date = month_first_date - timedelta(days=1)
        prev_month_last_date = prev_month_last_date.date()
        month_first_date = month_first_date.date()
        month_last_date = month_date.replace(day = monthrange(month_date.year, month_date.month)[1])
        month_last_date = month_last_date.date()
#         domain = [
#             ('journal_id','=',int(rent_invoice_journal_id)),
#             ('building_id','=',wiz.building_id.id),
#             ('invoice_date','>=',str(month_first_date)),
#             ('invoice_date','<=',str(month_last_date)),
#             ('state','=','posted'),('invoice_payment_state','=','not_paid')
#         ]
#         domain = [
#             ('journal_id','=',int(rent_invoice_journal_id)),
#             ('building_id','=',wiz.building_id.id),
#             ('invoice_date_due','<=',str(month_last_date)),
#             ('state','=','posted'),('invoice_payment_state','=','not_paid')
#         ]
#         if wiz.area_manager_id:
#             domain += [('building_id.area_manager','=',wiz.area_manager_id.id)]
#         if wiz.adviser_id:
#             domain += [('lease_id.adviser_id','=',wiz.adviser_id.id)]
#         # print (domain,'>>>>>\n\n')
#         inv_ids = self.env['account.move'].search(domain)
        # print (inv_ids,'sssssss\n\n\n')
        
        oustanding_dict = {}
        tenant_ids = self.env['res.partner'].search([('is_tenant','=',True)])
#         print('=============tenant_ids=====================',tenant_ids)  
        lease_list = []
        inv_ids = ''
        if wiz.building_id:
            inv_ids = self.env['account.move'].search(['|',('type','=','out_refund'),('type','=','out_invoice'),('journal_id','=',int(rent_invoice_journal_id)),('building_id','=',wiz.building_id.id),
                                    ('partner_id.id','in',tenant_ids.ids),('invoice_date_due','<=',str(month_last_date)),('state','=','posted'),('invoice_payment_state','=','not_paid')])
        
            if wiz.area_manager_id:
                inv_ids = self.env['account.move'].search(['|',('type','=','out_refund'),('type','=','out_invoice'),('journal_id','=',int(rent_invoice_journal_id)),('building_id','=',wiz.building_id.id),
                                    ('building_id.area_manager','=',wiz.area_manager_id.id),('partner_id.id','in',tenant_ids.ids),('invoice_date_due','<=',str(month_last_date)),('state','=','posted'),('invoice_payment_state','=','not_paid')])
        else:
            inv_ids = self.env['account.move'].search(['|',('type','=','out_refund'),('type','=','out_invoice'),('journal_id','=',int(rent_invoice_journal_id)),
                                    ('partner_id.id','in',tenant_ids.ids),('invoice_date_due','<=',str(month_last_date)),('state','=','posted'),('invoice_payment_state','=','not_paid')])
        
        if wiz.adviser_id:
            inv_ids = self.env['account.move'].search(['|',('type','=','out_refund'),('type','=','out_invoice'),('journal_id','=',int(rent_invoice_journal_id)),('building_id','=',wiz.building_id.id),
                                    ('lease_id.adviser_id','=',wiz.adviser_id.id),('partner_id.id','in',tenant_ids.ids),('invoice_date_due','<=',str(month_last_date)),('state','=','posted'),('invoice_payment_state','=','not_paid')])
        
        current_period_inv = inv_ids.filtered(lambda r: r.invoice_date_due >= month_first_date and r.invoice_date_due <= month_last_date)
        prev_period_inv = inv_ids.filtered(lambda r: r.invoice_date_due <= prev_month_last_date)
        
        for inv in inv_ids:
                    
            inv_dict_key = inv.module_id,inv.partner_id
                        
            if inv_dict_key in oustanding_dict:
                                
                if inv in prev_period_inv:
                    oustanding_dict[inv_dict_key]['prev_due'] += inv.amount_residual
                                 
                elif inv in current_period_inv:
                    oustanding_dict[inv_dict_key]['current_due'] += inv.amount_residual
            else:
                if inv in prev_period_inv:
                                    prev_due = inv.amount_residual
                                    current_due=0.0
                                     
                elif inv in current_period_inv:
                                    current_due = inv.amount_residual
                                    prev_due=0.0
                oustanding_dict.update({inv_dict_key:{'prev_due':prev_due,
                                                      'current_due':current_due,
                                         }})
        
        
        
        
        for key,values in oustanding_dict.items():
            
            lease = self.env['zbbm.module.lease.rent.agreement'].search([('tenant_id','=',key[1].id),('subproperty','=',key[0].id)],order='id desc',limit=1)
            invoices = inv_ids.filtered(lambda r: r.module_id.id == key[0].id and r.partner_id.id == key[1].id).sorted(key=lambda r: r.id)
            if invoices:
                due_date = datetime.strptime(str(invoices[-1].invoice_date_due), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                due_months = (datetime.today().year - invoices[-1].invoice_date_due.year) * 12 + (datetime.today().month - invoices[-1].invoice_date_due.month)
                
#                 due_months = []
#                 for inv in invoices:
#                     if inv in prev_period_inv:
#                         print('============inv-prev====================')
#                         if not inv.invoice_date_due.strftime("%B") in due_months:
#                             due_months.append(inv.invoice_date_due.strftime("%B"))
            else:
                due_date = ''
            
                
            worksheet.write(row, column, count, style2)
            worksheet.write(row, column +1, key[0].building_id.name or '', style2)
            worksheet.write(row, column +2, key[0].name or '',style2)
            worksheet.write(row, column +3, key[1].name or '', style2_wrap)
            worksheet.write(row, column +4, key[1].phone or '',style2)
            worksheet.write(row, column +5, key[1].mobile or '', style2)
            worksheet.write(row, column +6, key[1].email or '' , style2)
            worksheet.write(row, column +7, lease.adviser_id.name if lease and lease.adviser_id else '', style2)
            worksheet.write(row, column +8, key[0].building_id.area_manager.name or '' , style2)
            worksheet.write(row, column +9, due_date, style2)
            worksheet.write(row, column +10,due_months, style2)
            worksheet.write(row, column +11, values['prev_due'] , cell_number_format)
            worksheet.write(row, column +12, values['current_due'] , cell_number_format)
            worksheet.write(row, column +13, values['prev_due'] + values['current_due'] , cell_number_format)
            worksheet.write(row, column +14, invoices[-1].narration if invoices else '' , style2_wrap)
            row+=1
            count+=1
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
#         prev_amount_dues = 0.0
#         current_due = 0.0 
#         for inv in inv_ids:
#             lease_list.append(inv.lease_id)
#             if inv in prev_period_inv:
#                 prev_amount_dues = inv.amount_residual
#                 current_due = 0.0
#             else:
#                 current_due = inv.amount_residual
#                 prev_amount_dues = 0.0
#                 
#             if inv.invoice_date_due:
#                 invoice_date_due = datetime.strptime(str(inv.invoice_date_due), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
#                 due_date = datetime.strptime(str(inv.invoice_date_due), DEFAULT_SERVER_DATE_FORMAT)
#             else:
#                 invoice_date_due = datetime.strptime(str(inv.date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
#                 due_date = datetime.strptime(str(inv.date), DEFAULT_SERVER_DATE_FORMAT)
#             current_date = datetime.now()
#             diff_month = due_date.month - current_date.month + 12*(due_date.year - current_date.year)
#             worksheet.write(row, column, count, style2)
#             worksheet.write(row, column +1, inv.building_id.name, style2)
#             worksheet.write(row, column +2, inv.module_id.name ,style2)
#             worksheet.write(row, column +3, inv.partner_id.name if inv.partner_id else '', style2_wrap)
#             worksheet.write(row, column +4, inv.partner_id.phone if inv.partner_id.phone else '',style2)
#             worksheet.write(row, column +5, inv.partner_id.mobile if inv.partner_id.mobile else '', style2)
#             worksheet.write(row, column +6, inv.partner_id.email if inv.partner_id.email else '' , style2)
#             worksheet.write(row, column +7, inv.lease_id.adviser_id.name  if inv.lease_id.adviser_id else '', style2)
#             worksheet.write(row, column +8, inv.building_id.area_manager.name if inv.building_id.area_manager else '' , style2)
#             worksheet.write(row, column +9, invoice_date_due , style2)
#             worksheet.write(row, column +10, diff_month  if diff_month >= 0 else 0, style2)
#             worksheet.write(row, column +11, prev_amount_dues , cell_number_format)
#             worksheet.write(row, column +12, current_due , cell_number_format)
#             worksheet.write(row, column +13, prev_amount_dues + current_due , cell_number_format)
#             worksheet.write(row, column +14, inv.narration if inv.narration else '' , style2_wrap)
#             row += 1
#             count += 1

        
#         lease_list = []
#         for inv in inv_ids:
#             lease_list.append(inv.lease_id)
#neha         prev_inv_ids = self.env['account.move'].search([('journal_id','=',int(rent_invoice_journal_id)),('building_id','=',wiz.building_id.id),('module_id','=',inv.module_id.id),('invoice_date_due','<',str(prev_month_last_date)),('state','=','posted'),('invoice_payment_state','=','not_paid')])
#             prev_amount_dues = 0.0
#             for res in prev_inv_ids:
#neha         prev_amount_dues += res.amount_residual
            # prev_amount_dues = 0.0
            # prev_inv_ids = self.env['account.move'].search([('journal_id','=',int(rent_invoice_journal_id)),('building_id','=',wiz.building_id.id),('invoice_date','<',wiz.date),('module_id','=',inv.module_id.id),('state','=','posted')])
            # for res in prev_inv_ids:
            #     prev_amount_dues += res.amount_residual
            

        worksheet= workbook.add_worksheet('Tenant List')
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
        worksheet.set_column('J:J', 35)
        worksheet.merge_range('E7:H7', 'Rent Outstanding',title1)
        worksheet.write('A11', 'Sr.#', title2)
        worksheet.write('B11', 'Building Name', title2)
        worksheet.write('C11', 'Flat No', title2)
        worksheet.write('D11','Tenant Name', title2)
        worksheet.write('E11', 'Telephone', title2)
        worksheet.write('F11', 'Mobile', title2)
        worksheet.write('G11', 'Email', title2)
        worksheet.write('H11', 'Property Advisor', title2)
        worksheet.write('I11', 'Area Manager', title2)
        worksheet.write('J11', 'Remarks', title2)
        worksheet.write('A9', 'As On Date:', title3)
        worksheet.write('B9', date, title2)
        worksheet.write('D9', 'Building:' , title3)
        worksheet.write('E9', wiz.building_id.name, title2)

        worksheet.merge_range('E1:H5','\n %s \n %s  %s \n %s \n %s \n %s'%(cmpny_name,street,street2 ,cmpny.city,country_id,email),title2)
        worksheet.merge_range('A1:B7','')
        worksheet.insert_image('A1:B7','logo.png',{'x_scale': 0.10, 'y_scale': 0.11,'x_offset': 40})
        count = 1
        row = 11
        column = 0
        
        for key,values in oustanding_dict.items():
            lease = self.env['zbbm.module.lease.rent.agreement'].search([('tenant_id','=',key[1].id),('subproperty','=',key[0].id)],order='id desc',limit=1)
            invoices = inv_ids.filtered(lambda r: r.module_id.id == key[0].id and r.partner_id.id == key[1].id).sorted(key=lambda r: r.id)
            worksheet.write(row, column, count, style2)
            worksheet.write(row, column +1, key[0].building_id.name, style2)
            worksheet.write(row, column +2, key[0].name ,style2)
            worksheet.write(row, column +3, key[1].name or '', style2_wrap)
            worksheet.write(row, column +4, key[1].phone or '',style2)
            worksheet.write(row, column +5, key[1].mobile or '', style2)
            worksheet.write(row, column +6, key[1].email or '' , style2)
            worksheet.write(row, column +7, lease.adviser_id.name if lease and lease.adviser_id else '', style2)
            worksheet.write(row, column +8, key[0].building_id.area_manager.name or '' , style2)
            worksheet.write(row, column +9, invoices[-1].narration if invoices else '' , style2_wrap)
            row+=1
            count+=1
        
        # inv_ids = self.env['account.move'].search([('journal_id','=',int(rent_invoice_journal_id)),('building_id','=',wiz.building_id.id),('invoice_date','>=',str(month_first_date)),('invoice_date','<=',str(month_last_date)),('state','=','posted')])
        # prev_inv_ids = self.env['account.move'].search([('journal_id','=',int(rent_invoice_journal_id)),('building_id','=',wiz.building_id.id),('invoice_date_due','<',str(prev_month_last_date)),('state','=','posted')])
        # prev_amount_dues = 0.0
        # for res in prev_inv_ids:
        #     prev_amount_dues += res.amount_residual
        
#         for lease in lease_list:
#             worksheet.write(row, column, count, style2)
#             worksheet.write(row, column +1, lease.building_id.name, style2)
#             worksheet.write(row, column +2, lease.subproperty.name ,style2)
#             worksheet.write(row, column +3, lease.tenant_id.name if lease.tenant_id else '', style2_wrap)
#             worksheet.write(row, column +4, lease.tenant_id.phone if lease.tenant_id.phone else '',style2)
#             worksheet.write(row, column +5, lease.tenant_id.mobile if lease.tenant_id.mobile else '', style2)
#             worksheet.write(row, column +6, lease.tenant_id.email if lease.tenant_id.email else '' , style2)
#             worksheet.write(row, column +7, lease.adviser_id.name  if lease.adviser_id else '', style2)
#             worksheet.write(row, column +8, lease.building_id.area_manager.name if lease.building_id.area_manager else '' , style2)
#             worksheet.write(row, column +9, lease.remarks if lease.remarks else '' , style2_wrap)
#             row += 1
#             count += 1
            # prev_amount_dues = 0.0
            # prev_inv_ids = self.env['account.move'].search([('journal_id','=',int(rent_invoice_journal_id)),('building_id','=',wiz.building_id.id),('invoice_date','<',wiz.date),('module_id','=',inv.module_id.id),('state','=','posted')])
            # for res in prev_inv_ids:
            #     prev_amount_dues += res.amount_residual
#             if inv.invoice_date_due:
#                 invoice_date_due = datetime.strptime(str(inv.invoice_date_due), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
#                 due_date = datetime.strptime(str(inv.invoice_date_due), DEFAULT_SERVER_DATE_FORMAT)
#             else:
#                 invoice_date_due = datetime.strptime(str(inv.date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
#                 due_date = datetime.strptime(str(inv.date), DEFAULT_SERVER_DATE_FORMAT)
#             current_date = datetime.now()
#             diff_month = due_date.month - current_date.month + 12*(due_date.year - current_date.year)
            



   