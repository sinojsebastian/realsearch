from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage


class SupplierStatementXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_supplier_statement'
    _description = 'Supplier Statement Report'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, wiz):
         
        
        worksheet= workbook.add_worksheet('Supplier Wise Statement Report')
        
        style = workbook.add_format({'size': 10,'bold':True})
        wrap = workbook.add_format({'size': 10,'valign': 'vcenter','align': 'center'})
        wrap.set_text_wrap()
        
        title1 = workbook.add_format({'align': 'left',
                                                      'bold': True, 'size': 10,})
        title1.set_text_wrap()
        
        styletext = workbook.add_format({'size': 13,'bold':True,'align': 'center'})
        style2 = workbook.add_format({'size': 10,'align': 'right', 'valign': 'vcenter','num_format': '#,##0.000'})
        
        worksheet.merge_range('E6:F6', 'Supplier Wise Details',styletext)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 12)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.write('A8', 'Sr.#',style)
        worksheet.write('B8', 'PO Number',style)
        worksheet.write('C8', 'Supplier Name',style)
        worksheet.write('D8', 'Nature of Expense',style)
        worksheet.write('E8', 'Approved (LPO)',style)
        worksheet.write('F8','Invoiced',style) 
        worksheet.write('G8', 'Paid',style)
        worksheet.write('H8', 'Balance Payable',style)
        worksheet.write('I8', 'Balance (LPO)',style)
        
        
        style1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                       'size': 10})
        style2 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                       'size': 10,'num_format': '#,##0.000'})
       
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
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
        worksheet.merge_range('C1:D5','%s \n %s \n %s \n %s \n %s \n %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.09, 'y_scale': 0.09})
        
        params = self.env['ir.config_parameter'].sudo()  
        journall_id=params.get_param('zb_bf_custom.vendor_journal_id') or False,
        
        if wiz.date:
            date = datetime.strptime(str(wiz.date),'%Y-%m-%d').strftime('%m/%d/%Y')
            billss = self.env['account.move'].search([('type','=','in_invoice'),('invoice_date','<=',date),('journal_id','=',int(journall_id[0]))])
            
            payments = self.env['account.payment'].search([('partner_type','=','supplier')])

            count=1
            row = 9
            column=0
            
            for bill in billss:
                purchase_id = self.env['purchase.order'].search([('name','=',bill.invoice_origin),('state','=','purchase')])

                worksheet.write(row,column,count,style1)
                if bill.invoice_origin:
                    worksheet.write(row,column+1,bill.invoice_origin or '',style1)
                    worksheet.write(row,column+4,bill.amount_total,style2)
                    worksheet.write(row,column+8,purchase_id.amount_total-bill.amount_total or 0.000,style2)
                worksheet.write(row,column+2,bill.partner_id.name,style1)
                worksheet.write(row,column+3,'',wrap)
                for pay in payments:
                    
                    if pay.method_type == 'advance':
                        for entry in pay.payment_entries():
                            
                            if bill.name == entry['number']:
                                
                                worksheet.write(row,column+6,entry['amount'] or 0.000,style2)
                    else:
                        for line in pay.payment_line_ids:
                            if bill == line.inv_id:
                                
                                worksheet.write(row,column+6,line.allocation or 0.000,style2)
                            
                worksheet.write(row,column+5,bill.amount_total or 0.000,style2)
                worksheet.write(row,column+7,bill.amount_residual or 0.000,style2)
                
                row+=1
                count+=1
                                    
                        
                
                            

            
            
                    
        
        
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                