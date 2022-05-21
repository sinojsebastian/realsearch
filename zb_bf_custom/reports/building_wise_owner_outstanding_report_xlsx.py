from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from distutils.command.build import build


class Building_Wise_Owner_Outstanding_Xlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_building_owner_outstanding'
    _description = 'Building Wise Owner Outstanding / Detail / Summary'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def get_residual_amount(self,lines,type,final_data):
        '''Function to calculate residual amount'''
        
        first_due =0
        second_due =0
        third_due =0
        fourth_due =0
        fifth_due =0
        sixth_due =0
        for line in lines:
            if line.partner_id == line.module_id.owner_id:
                if final_data.get((line.move_id.module_id)):
                    if type == 'first':
                        final_data[(line.move_id.module_id)]['first_due'] += line.move_id.amount_residual
                    elif type == 'second':
                        final_data[(line.move_id.module_id)]['second_due'] += line.move_id.amount_residual
                    elif type == 'third':
                        final_data[(line.move_id.module_id)]['third_due'] += line.move_id.amount_residual
                    elif type == 'forth':
                        final_data[(line.move_id.module_id)]['fourth_due'] += line.move_id.amount_residual
                    elif type == 'fifth':
                        final_data[(line.move_id.module_id)]['fifth_due'] += line.move_id.amount_residual
                    elif type == 'sixth':
                        final_data[(line.move_id.module_id)]['sixth_due'] += line.move_id.amount_residual
                else:
                    if type == 'first':
                       first_due = line.move_id.amount_residual
                    elif type == 'second':
                        second_due = line.move_id.amount_residual
                    elif type == 'third':
                        third_due = line.move_id.amount_residual
                    elif type == 'forth':
                        fourth_due = line.move_id.amount_residual
                    elif type == 'fifth':
                        fifth_due = line.move_id.amount_residual
                    elif type == 'sixth':
                        sixth_due = line.move_id.amount_residual
                    final_data.update({(line.move_id.module_id):{
                                                'first_due':first_due,
                                                'second_due':second_due,
                                                'third_due':third_due,
                                                'fourth_due':fourth_due,
                                                'fifth_due':fifth_due,
                                                'sixth_due':sixth_due,
                                                }})
        return final_data
    
    
    def get_outstanding_amount(self,lines,type,pdt_data):
        '''Function to calculate outstanding amount'''
        
        service_due_amt = 0
        maintenance_due_amt = 0
        ewa_due_amt = 0
        tabreed_due_amt = 0
        internet_due_amt = 0
        for line in lines:
            if line.partner_id == line.module_id.owner_id:
                if pdt_data.get((line.module_id)):
                    if type == 'service':
                        pdt_data[(line.module_id)]['service_due_amt'] += line.amount_residual
                    elif type == 'maintenance':
                        pdt_data[(line.module_id)]['maintenance_due_amt'] += line.amount_residual
                    elif type == 'ewa':
                        pdt_data[(line.module_id)]['ewa_due_amt'] += line.amount_residual
                    elif type == 'tabreed':
                        pdt_data[(line.module_id)]['tabreed_due_amt'] += line.amount_residual
                    elif type == 'internet':
                        pdt_data[(line.module_id)]['internet_due_amt'] += line.amount_residual
                else:
                    if type == 'service':
                        service_due_amt = line.amount_residual
                    elif type == 'maintenance':
                        maintenance_due_amt = line.amount_residual
                    elif type == 'ewa':
                        ewa_due_amt = line.amount_residual
                    elif type == 'tabreed':
                        tabreed_due_amt = line.amount_residual
                    elif type == 'internet':
                        internet_due_amt = line.amount_residual
                    pdt_data.update({(line.module_id):{
                                            'service_due_amt':service_due_amt,
                                            'maintenance_due_amt':maintenance_due_amt,
                                            'ewa_due_amt':ewa_due_amt,
                                            'tabreed_due_amt':tabreed_due_amt,
                                            'internet_due_amt':internet_due_amt}})
        
            
        return pdt_data
    
    def generate_xlsx_report(self, workbook, data,wiz):

        worksheet= workbook.add_worksheet('Outstanding Sheet 1')
        
        title1 = workbook.add_format({'align': 'left','bold': True, 'size': 10,})
        styletext = workbook.add_format({'size': 13,'bold':True,'align': 'center'})
        style = workbook.add_format({'size': 10,'bold':True,})
        style_right = workbook.add_format({'size': 10,'align': 'right','bold':True})
        wrap = workbook.add_format({'size': 10,'bold':True,})
        wrap.set_text_wrap()
        style1 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        number_format_right = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','num_format': '#,###0.000'})
        amount_format_bold = workbook.add_format({'size': 10,'align': 'right','num_format': '#,###0.000','bold':True})
        style2 = workbook.add_format({'size': 10,'bold':True,'align': 'left'})
       
        worksheet.set_row(10, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 22)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 16)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 7)
        worksheet.set_column('L:L', 7)
        worksheet.set_column('M:M', 7)
        worksheet.set_column('N:N', 7)
        worksheet.set_column('O:O', 8)
        worksheet.set_column('P:P', 8)
        
        worksheet.write('D7', 'Outstanding - Building Wise',styletext)
        worksheet.write('A9', 'As On Date:',style)
        worksheet.write('D9', 'Summary Report',styletext)
        worksheet.write('A11', 'Sr.#',style)
        worksheet.write('B11', 'Building Name:',style)
        worksheet.write('C11', 'Flat No.',style)
        worksheet.write('D11', 'Owner Name',wrap)
        worksheet.write('E11','Status',wrap) 
        worksheet.write('F11', 'Owners Contact Number 1' ,wrap)
        worksheet.write('G11', 'Owners Contact Number 2',wrap)
        worksheet.write('H11', 'Owners Email 1',wrap)
        worksheet.write('I11', 'Owners Email 2',wrap)
        worksheet.write('J11', 'Total Due Balance',wrap)
        worksheet.write('K11', '0-30 Days',wrap)
        worksheet.write('L11', '31-60 Days',wrap)
        worksheet.write('M11', '61-90 Days',wrap)
        worksheet.write('N11', '91-180 Days',wrap)
        worksheet.write('O11', '181-360 Days',wrap)
        worksheet.write('P11', 'Above 360 Days',wrap)
        
        cmpny        = self.env.user.company_id
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
            
        worksheet.merge_range('D1:E5','%s \n%s \n%s \n%s \n%s \n%s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.06, 'y_scale': 0.06})
        worksheet.merge_range('E9:F9',wiz.service_product_id.name,style)
        
        wiz_date = datetime.strptime(str(wiz.date),'%Y-%m-%d').strftime('%d-%b')
        
        worksheet.write('B9',wiz_date,style_right)
        worksheet.write('B13',wiz.building_id.name,style1)
        
        base_date = datetime.strptime(str(wiz.date), "%Y-%m-%d")
        date = base_date.strftime("%Y-%m-%d 23:59:59")
        date_to_1 = base_date.strftime("%Y-%m-%d 23:59:59")
        date_from_1 = (wiz.date - timedelta(days=30))
        date_from_2 = (wiz.date - timedelta(days=60))
        date_from_3 = (wiz.date - timedelta(days=90))
        date_from_4 = (wiz.date - timedelta(days=180))
        date_from_5 = (wiz.date - timedelta(days=360))
        
        # fetching service/maintenance/ewa/tabreed/internet O/S
        params = self.env['ir.config_parameter'].sudo() 
        service_journal = params.get_param('zb_bf_custom.service_journal_id') or False,
        maintnce_journal = params.get_param('zb_bf_custom.maintenance_journal_id') or False,
        tabreed_journal = params.get_param('zb_bf_custom.tabreed_journal_id') or False,
        ewa_journal = params.get_param('zb_bf_custom.ewa_journal_id') or False,
        internet_journal = params.get_param('zb_bf_custom.internet_journal_id') or False,
        
        journal_list = [int(service_journal[0]),int(maintnce_journal[0]),int(tabreed_journal[0]),int(ewa_journal[0]),int(internet_journal[0])]
        final_data = {}
        
        flat_list =list(wiz.building_id.module_ids.ids)
        
        if wiz.building_id:
            move_line_ids = self.env['account.move.line'].search([('product_id','=',wiz.service_product_id.id),('journal_id.id','in',journal_list),('move_id.state','=','posted'),('date','<=',wiz.date),('move_id.module_id','in',flat_list)])
        else:
            move_line_ids = self.env['account.move.line'].search([('product_id','=',wiz.service_product_id.id),('move_id.state','=','posted'),('journal_id.id','in',journal_list),('date','<=',wiz.date)])
        
        
        # fetching aging datas
        first_due_line = move_line_ids.filtered(lambda r: r.date <= wiz.date and r.date >= date_from_1) #30
        second_due_line = move_line_ids.filtered(lambda r:r.date < date_from_1 and r.date >= date_from_2)
        third_due_line = move_line_ids.filtered(lambda r: r.date < date_from_2 and r.date >= date_from_3) #30
        fourth_due_line = move_line_ids.filtered(lambda r: r.date < date_from_3 and r.date >= date_from_4) # 90
        fifth_due_line = move_line_ids.filtered(lambda r: r.date < date_from_4 and r.date >= date_from_5) # 180
        sixth_due_line = move_line_ids.filtered(lambda r: r.date < date_from_5) # above 360
        
        final_data = self.get_residual_amount(first_due_line,'first', final_data)
        final_data = self.get_residual_amount(second_due_line,'second', final_data)
        final_data = self.get_residual_amount(third_due_line,'third', final_data)
        final_data = self.get_residual_amount(fourth_due_line,'forth', final_data)
        final_data = self.get_residual_amount(fifth_due_line,'fifth', final_data)
        final_data = self.get_residual_amount(sixth_due_line,'sixth', final_data)

        
        
        first_due_total = 0
        secnd_due_total = 0
        third_due_total = 0
        forth_due_total = 0
        fifth_due_total = 0
        sixth_due_total = 0
        count=1
        row = 12
        if wiz.building_id:
            worksheet.write(row,1,wiz.building_id.name or '',style1)
        for k,v in final_data.items():
            first_due_total += v['first_due']
            secnd_due_total += v['second_due']
            third_due_total += v['third_due']
            forth_due_total += v['fourth_due']
            fifth_due_total += v['fifth_due']
            sixth_due_total += v['sixth_due']
            
            worksheet.write(row,0,count or '',style1)
            if not wiz.building_id:
                worksheet.write(row,1,k.building_id.name or '',style1)
            worksheet.write(row,2,k.name or '',style1)
            worksheet.write(row,3,k.owner_id.name or '',style1)
            if k.managed:
                worksheet.write(row,4,'Managed',style1)
            else:
                worksheet.write(row,4,'Not Managed',style1)
            worksheet.write(row,5,k.owner_id.phone or '',style1)
            worksheet.write(row,6,k.owner_id.mobile or '',style1)
            worksheet.write(row,7,k.owner_id.email or '',style1)
            worksheet.write(row,8,'',style1)
            worksheet.write_formula(row,9,'{=SUM(K%s:P%s)}'%(row+1,row+1),number_format_right)
            worksheet.write(row,10,v['first_due'],number_format_right)
            worksheet.write(row,11,v['second_due'],number_format_right)
            worksheet.write(row,12,v['third_due'],number_format_right)
            worksheet.write(row,13,v['fourth_due'],number_format_right)
            worksheet.write(row,14,v['fifth_due'],number_format_right)
            worksheet.write(row,15,v['sixth_due'],number_format_right)
#             worksheet.write(row,12,v['current_period_amt']+v['prevoius_period_amt'],style2)
            row=row+1
            count=count+1
       
        worksheet.write(row,8, 'Total' ,style2)
        worksheet.write_formula(row,9,'{=SUM(K%s:P%s)}'%(row+1,row+1),amount_format_bold)
        worksheet.write(row,10,first_due_total,amount_format_bold)
        worksheet.write(row,11,secnd_due_total,amount_format_bold)
        worksheet.write(row,12,third_due_total,amount_format_bold)
        worksheet.write(row,13,forth_due_total,amount_format_bold)
        worksheet.write(row,14,fifth_due_total,amount_format_bold)
        worksheet.write(row,15,sixth_due_total,amount_format_bold)
        
        
        worksheet= workbook.add_worksheet('Owner Details')
         
        worksheet.set_row(10, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 16)
        worksheet.set_column('H:H', 16)
        worksheet.set_column('I:I', 12)
        worksheet.set_column('J:J', 12)
        worksheet.set_column('K:K', 12)
        worksheet.set_column('L:L', 12)
        worksheet.set_column('M:M', 12)
         
        worksheet.merge_range('G7:H7', 'Outstanding - Building Wise',styletext)
        worksheet.write('A9', 'Date:',style)
        worksheet.write('C9', 'Building Name:',style)
        worksheet.write('A11', 'Sr.#',style)
        worksheet.write('B11', 'Flat No.',style)
        worksheet.write('C11', 'Owner Name',wrap)
        worksheet.write('D11','Status',wrap) 
        worksheet.write('E11', 'Owners Contact Number 1' ,wrap)
        worksheet.write('F11', 'Owners Contact Number 2',wrap)
        worksheet.write('G11', 'Owners Email 1',wrap)
        worksheet.write('H11', 'Owners Email 2',wrap)
        worksheet.write('I11', 'SC O/s',wrap)
        worksheet.write('J11', 'Maintenance O/s',wrap)
        worksheet.write('K11', 'Tabreed O/s',wrap)
        worksheet.write('L11', 'EWA O/s',wrap)
        worksheet.write('M11', 'Internet O/s',wrap)
             
        worksheet.merge_range('C1:D5','%s \n%s \n%s \n%s \n%s \n%s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.065, 'y_scale': 0.08})
         
        worksheet.write('B9',wiz_date,style_right)
        worksheet.write('D9',wiz.building_id.name or '',style1)

        pdt_data = {}
        
        if wiz.building_id:
        
            service_moves = self.env['account.move'].search([('journal_id.id','=',int(service_journal[0])),('module_id','in',flat_list),('state','=','posted'),('invoice_date','<=',wiz.date)])
            maintnce_moves = self.env['account.move'].search([('journal_id.id','=',int(maintnce_journal[0])),('module_id','in',flat_list),('state','=','posted'),('invoice_date','<=',wiz.date)])
            tabreed_moves = self.env['account.move'].search([('journal_id.id','=',int(tabreed_journal[0])),('module_id','in',flat_list),('state','=','posted'),('invoice_date','<=',wiz.date)])
            ewa_moves = self.env['account.move'].search([('journal_id.id','=',int(ewa_journal[0])),('module_id','in',flat_list),('state','=','posted'),('invoice_date','<=',wiz.date)])
            internet_moves = self.env['account.move'].search([('journal_id.id','=',int(internet_journal[0])),('module_id','in',flat_list),('state','=','posted'),('invoice_date','<=',wiz.date)])

        else:
            service_moves = self.env['account.move'].search([('journal_id','=',int(service_journal[0])),('state','=','posted'),('invoice_date','<=',wiz.date)])
            maintnce_moves = self.env['account.move'].search([('journal_id','=',int(maintnce_journal[0])),('state','=','posted'),('invoice_date','<=',wiz.date)])
            tabreed_moves = self.env['account.move'].search([('journal_id','=',int(tabreed_journal[0])),('state','=','posted'),('invoice_date','<=',wiz.date)])
            ewa_moves = self.env['account.move'].search([('journal_id','=',int(ewa_journal[0])),('state','=','posted'),('invoice_date','<=',wiz.date)])
            internet_moves = self.env['account.move'].search([('journal_id','=',int(internet_journal[0])),('state','=','posted'),('invoice_date','<=',wiz.date)])

        
        pdt_data = self.get_outstanding_amount(service_moves,'service',pdt_data)
        pdt_data = self.get_outstanding_amount(maintnce_moves,'maintenance',pdt_data)
        pdt_data = self.get_outstanding_amount(tabreed_moves,'tabreed',pdt_data)
        pdt_data = self.get_outstanding_amount(ewa_moves,'ewa',pdt_data)
        pdt_data = self.get_outstanding_amount(internet_moves,'internet',pdt_data)

        service_due_total = 0
        maitnce_due_total = 0
        ewa_due_total = 0
        tabreed_due_total = 0
        internet_due_total = 0
        
        count=1
        row = 12
        
        for k,v in pdt_data.items():
                
            service_due_total += v['service_due_amt']
            maitnce_due_total += v['maintenance_due_amt']
            ewa_due_total += v['ewa_due_amt']
            tabreed_due_total += v['tabreed_due_amt']
            internet_due_total += v['internet_due_amt']
            
            worksheet.write(row,0,count or '',style1)
            worksheet.write(row,1,k.name or '',style1)
            worksheet.write(row,2,k.owner_id.name or '',style1)
            if k.managed:
                worksheet.write(row,3,'Managed',style1)
            else:
                worksheet.write(row,3,'Not Managed',style1)
            worksheet.write(row,4,k.owner_id.phone or '',style1)
            worksheet.write(row,5,k.owner_id.mobile or '',style1)
            worksheet.write(row,6,k.owner_id.email or '',style1)
            worksheet.write(row,7,'',style1)
            worksheet.write(row,8,v['service_due_amt'],number_format_right)
            worksheet.write(row,9,v['maintenance_due_amt'],number_format_right)
            worksheet.write(row,11,v['ewa_due_amt'],number_format_right)
            worksheet.write(row,10,v['tabreed_due_amt'],number_format_right)
            worksheet.write(row,12,v['internet_due_amt'],number_format_right)

            row=row+1
            count=count+1
        
        worksheet.write(row,7, 'Total' ,style2)
        worksheet.write(row,8,service_due_total,amount_format_bold)
        worksheet.write(row,9,maitnce_due_total,amount_format_bold)
        worksheet.write(row,11,ewa_due_total,amount_format_bold)
        worksheet.write(row,10,tabreed_due_total,amount_format_bold)
        worksheet.write(row,12,internet_due_total,amount_format_bold)





        
                    
            