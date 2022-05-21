from odoo import models,_
from datetime import datetime, timedelta,date
from odoo.exceptions import AccessError,UserError,Warning

import base64 
from io import BytesIO 
from PIL import Image as PILImage

class ServiceChargeCollectionXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_service_charge_report'
    _description = 'Service Charge Collection Report'
    _inherit = 'report.report_xlsx.abstract'


    
    def generate_xlsx_report(self, workbook, data,wiz):
         

        worksheet= workbook.add_worksheet('Service Charge Collection')
        
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
        
        
        worksheet.set_row(12, 50)
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
        
        worksheet.merge_range('E7:I7', 'Service Charge Outstanding - Building Wise Collection Summary',heading_format)
        worksheet.write('A9', 'From Date:',no_border)
        worksheet.write('C9', 'To Date:',no_border)
        worksheet.write('C10', 'Building Name:',no_border)
        worksheet.write('C11', 'Expense Name:',no_border)
        
        worksheet.write('A13', 'Sr.#',style)
        worksheet.write('B13', 'Flat No.',style)
        worksheet.write('C13', 'Owner Name',style)
        worksheet.write('D13', 'Status',style)
        worksheet.write('E13',"Owner's Contact Number 1",style1) 
        worksheet.write('F13', "Owner's Contact Number2",style1)
        worksheet.write('G13', "Owner's Email 1",style)
        worksheet.write('H13', "Owner's Email 2",style)
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        if company_logo:
            data=base64.b64decode(company_logo) 
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
            
        worksheet.merge_range('C1:D5','%s \n %s \n %s \n %s \n %s \n  %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.065, 'y_scale': 0.08})
        
        if wiz.from_date and wiz.to_date and wiz.building_id:
            
            from_date = datetime.strptime(str(wiz.from_date),'%Y-%m-%d').strftime('%m/%d/%Y')
            to_date = datetime.strptime(str(wiz.to_date),'%Y-%m-%d').strftime('%m/%d/%Y')
            worksheet.write('B9',from_date,title2)
            worksheet.write('D9',to_date,title2)
            worksheet.write('D10',wiz.building_id.name,title2)
            worksheet.write('D11', wiz.product_id.name,title2)
            
            owner_ids = self.env['res.partner'].search([('owner','=',True)])
            
            current_from_date = date(wiz.from_date.year,wiz.from_date.month,wiz.from_date.day)
            format_current_from_date = datetime.strptime(str(current_from_date),'%Y-%m-%d').strftime('%d/%m/%Y')
            current_to_date = date(wiz.to_date.year,wiz.to_date.month,wiz.to_date.day)
            format_current_to_date = datetime.strptime(str(current_to_date),'%Y-%m-%d').strftime('%d/%m/%Y')
            
            prev_from_date = date(wiz.from_date.year-1,wiz.from_date.month,wiz.from_date.day)
            format_prev_from_date = datetime.strptime(str(prev_from_date),'%Y-%m-%d').strftime('%d/%m/%Y')
            prev_to_date = date(wiz.to_date.year-1,wiz.to_date.month,wiz.to_date.day)
            format_prev_to_date = datetime.strptime(str(prev_to_date),'%Y-%m-%d').strftime('%d/%m/%Y')
            
            
            worksheet.write('I13', 'Current Amount (%s to %s)'%(format_current_from_date,format_current_to_date),style1)
            worksheet.write('J13', 'Previous Amount (%s to %s)'%(format_prev_from_date,format_prev_to_date),style1)
            worksheet.write('K13', 'Total Amount',style1)
            
            service_charge_invoices = self.env['account.move'].search([('building_id','=',wiz.building_id.id)],order='id desc',limit=1)
            service_from_date = ''
            service_to_date = ''
            if service_charge_invoices.from_date and service_charge_invoices.to_date:
                service_from_date = datetime.strptime(str(service_charge_invoices.from_date),'%Y-%m-%d').strftime('%d/%m/%Y')
                service_to_date = 'to %s'%(datetime.strptime(str(service_charge_invoices.to_date),'%Y-%m-%d').strftime('%d/%m/%Y'))
            worksheet.merge_range('H12:K12','Service Charge Period - %s %s'%(service_from_date,service_to_date) or '',subheading)
            
            final_data = {}
            
            # fetching current and previous period datas
            for owner in owner_ids:
                
                inv_line_ids = self.env['account.move.line'].search([('product_id','=',wiz.product_id.id),('date','>=',prev_from_date),('date','<=',current_to_date),('move_id.state','=','posted'),('move_id.building_id','=',wiz.building_id.id),('move_id.module_id.owner_id','=',owner.id)])
                current_period_inv = inv_line_ids.filtered(lambda r: r.date >= current_from_date and r.date <= current_to_date)
                prev_period_inv = inv_line_ids.filtered(lambda r: r.date >= prev_from_date and r.date <= prev_to_date)
                final_data = self.get_collected_amount(current_period_inv,'current', final_data)
                final_data = self.get_collected_amount(prev_period_inv,'previous', final_data)
                
                        
            count=1
            row = 14

            for k,v in final_data.items():
                    
                worksheet.write(row,0,count or '',style3)
                worksheet.write(row,1,k[0].name or '',style3)
                worksheet.write(row,2,k[1].name or '',style3)
                if k[0].managed:
                    worksheet.write(row,3,'Managed',style3)
                else:
                    worksheet.write(row,3,'Not Managed',style3)
                worksheet.write(row,4,k[1].phone or '',style3)
                worksheet.write(row,5,k[1].mobile or '',style3)
                worksheet.write(row,6,k[1].email or '',style3)
                worksheet.write(row,7,'',style2)
                worksheet.write(row,8,v['current_period_amt'],style2)
                worksheet.write(row,9,v['prevoius_period_amt'],style2)
                worksheet.write(row,10,v['current_period_amt']+v['prevoius_period_amt'],style2)
                row=row+1
                count=count+1
        
        
    def get_collected_amount(self,lines,type,final_data):
        '''Function to calculate collected amount'''
        
        current_period_amt=0
        prevoius_period_amt=0
        for line in lines:
            if final_data.get((line.move_id.module_id,line.move_id.module_id.owner_id)):
                if type == 'current':
                    final_data[(line.move_id.module_id,line.move_id.module_id.owner_id)]['current_period_amt'] += line.move_id.amount_total - line.move_id.amount_residual
                elif type == 'previous':
                    final_data[(line.move_id.module_id,line.move_id.module_id.owner_id)]['prevoius_period_amt'] += line.move_id.amount_total - line.move_id.amount_residual
            else:
                if type == 'current':
                   current_period_amt = line.move_id.amount_total - line.move_id.amount_residual
                elif type == 'previous':
                    prevoius_period_amt = line.move_id.amount_total - line.move_id.amount_residual
                final_data.update({(line.move_id.module_id,line.move_id.module_id.owner_id):{
                                            'current_period_amt':current_period_amt,
                                            'prevoius_period_amt':prevoius_period_amt,
                                            }})
        return final_data
        
        
        
        
        
        
        
        
        
        
        
        
        
        