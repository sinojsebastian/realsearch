from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage

from dateutil.rrule import rrule, DAILY


import logging
_logger = logging.getLogger(__name__)



class ContractCommissionDeductionReport(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_commission_deduction_contract'
    _description = 'Contract Commission Deduction Report'
    _inherit = 'report.report_xlsx.abstract'

    
    def generate_xlsx_report(self, workbook, data, wiz):
         

        worksheet= workbook.add_worksheet('Commission Deduction on Contract Termination Report')
        
        title1 = workbook.add_format({'align': 'left','bold': True, 'size': 10,})
        title1.set_text_wrap()
        left_heading_bold_format = workbook.add_format({'size': 16,'bold':True,'align': 'left'})
        heading_format = workbook.add_format({'align': 'center','size': 10,'bold':True})
        heading_bold_left = workbook.add_format({'size': 14,'bold':True,'align': 'left'})
        heading_bold_right = workbook.add_format({'size': 11,'bold':True,'align': 'right'})
        text_heading_bold_left = workbook.add_format({'size': 10,'bold':True,'align': 'left','text_wrap':True})
        text_heading_bold_center_fg1 = workbook.add_format({'size': 10,'bold':True,'align': 'center','fg_color': '#FFFF00','text_wrap':True})
        text_heading_bold_center = workbook.add_format({'align': 'center','size': 10,'bold':True})
        table_value_format_right = workbook.add_format({'align': 'right','size': 10})
        table_value_format_left = workbook.add_format({'align': 'left','size': 10})
        table_value_format_center = workbook.add_format({'align': 'center','size': 10})
        number_format = workbook.add_format({'size': 10,'align': 'right','num_format': '#,###0.000'})
        number_format_bold_right = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000'})

        formater = workbook.add_format({'border': 1})
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        
        worksheet.set_row(1, 25)
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 17)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('P:P', 25)
         
        
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
        
        logo = False
        if self.env.user.company_id.logo:
            logo = BytesIO(base64.b64decode(self.env.user.company_id.logo or False))    
        
#         worksheet.merge_range('C1:C5','%s \n %s \n %s \n %s \n %s \n  %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','logo.png', {'image_data': logo,'x_offset': 0,'x_scale': 0.13, 'y_scale': 0.13})

        
        worksheet.set_row(5, 25)
        worksheet.merge_range('A6:C6',cmpny_name,heading_bold_left)
        
        
        wiz_from_date = datetime.strptime(str(wiz.from_date),'%Y-%m-%d').strftime('%d/%m/%Y')
        wiz_to_date = datetime.strptime(str(wiz.to_date),'%Y-%m-%d').strftime('%d/%m/%Y')
        
        wiz_to_date_month = datetime.strptime(str(wiz.to_date),'%Y-%m-%d').strftime('%d-%b-%Y')
        
        worksheet.merge_range('A7:D7','Monthly report for Commission Deduction for cancelled leases for the cycle ended',text_heading_bold_left)
        worksheet.write('G7',wiz_to_date_month,table_value_format_left)
        
        
        worksheet.write('A9', 'Cycle',text_heading_bold_left)
        worksheet.merge_range('B9:C9',str(wiz_from_date)+" to "+ str(wiz_to_date),text_heading_bold_left)
        
        worksheet.merge_range('E9:F9','Tenancy Period',text_heading_bold_center)
        

        
        worksheet.set_row(9, 30)
         
        worksheet.write('A10', 'Sr No',text_heading_bold_center_fg1)
        worksheet.write('B10', 'Flat',text_heading_bold_center_fg1)
        worksheet.write('C10', 'Building Name',text_heading_bold_center_fg1)
        worksheet.write('D10', 'Tenant Name',text_heading_bold_center_fg1)
        worksheet.write('E10', 'From',text_heading_bold_center_fg1)
        worksheet.write('F10', 'To',text_heading_bold_center_fg1)
        worksheet.write('G10', 'Rent Covered Upto *',text_heading_bold_center_fg1)
        worksheet.write('H10', 'No of days refund',text_heading_bold_center_fg1)
        worksheet.write('I10', 'Commission Paid',text_heading_bold_center_fg1)
        worksheet.write('J10', 'Direct/Agent',text_heading_bold_center_fg1)
        worksheet.write('K10', '% of Commission paid -PA',text_heading_bold_center_fg1)
        worksheet.write('L10', 'Commission Deduction from PA',text_heading_bold_center_fg1)
        worksheet.write('M10', 'Agent Comm. Refund Claim',text_heading_bold_center_fg1)
        worksheet.write('N10', 'Sales Executive',text_heading_bold_center_fg1)
        worksheet.write('O10', 'Agent Name',text_heading_bold_center_fg1)
        worksheet.write('P10', 'Comments / claim on agent made ?',text_heading_bold_center_fg1)
         
         


        lease_ids = self.env['zbbm.module.lease.rent.agreement'].search([('state','=','terminate'),('termination_date','>=',wiz.from_date),('termination_date','<=',wiz.to_date)],order='agreement_start_date asc')
        row = 11
        count = 1
        invoices = []
        for lease_id in lease_ids:
            invoices = []
            if lease_id.invoice_plan_ids:
                for plan in lease_id.invoice_plan_ids:
                    if plan.move_id and plan.move_id.amount_residual == 0.000:
                        invoices.append(plan.move_id.id)
            if invoices:
                latest_dates = []
                for inv in invoices:
                    move = self.env['account.move'].browse(inv)
                    payment_ids = self.env['account.payment'].search([('state','=','posted'),('lease_id','=',move.lease_id.id)])
                    for payment in payment_ids:
                        for invoice in payment.reconciled_invoice_ids:
                            if inv == invoice.id:
                                latest_dates.append(payment.payment_date)
                rent_covered_upto = datetime.strptime(str(max(latest_dates)),'%Y-%m-%d').strftime('%d-%m-%Y')
            else:
                rent_covered_upto = ''
            
            agreement_start_date = datetime.strptime(str(lease_id.agreement_start_date),'%Y-%m-%d').strftime('%d-%m-%Y')
            agreement_end_date = datetime.strptime(str(lease_id.agreement_end_date),'%Y-%m-%d').strftime('%d-%m-%Y')
            
            cmpny_refund_commission = 0.000
            refund_cmpny_no_of_days = (datetime.strptime(str(lease_id.termination_date), '%Y-%m-%d')-datetime.strptime(str(lease_id.agreement_start_date), '%Y-%m-%d')).days + 1
            no_of_days_refund = (datetime.strptime(str(lease_id.agreement_end_date), '%Y-%m-%d')-datetime.strptime(str(lease_id.termination_date), '%Y-%m-%d')).days 
            refund_commission = 0.000
            if not lease_id.total_commission_percent and lease_id.commission_percent:
                if no_of_days_refund < 365:
                    refund_commission = (lease_id.monthly_rent *(lease_id.commission_percent/100))/365 * no_of_days_refund   
                if refund_cmpny_no_of_days < 365:
                    cmpny_refund_commission = (lease_id.monthly_rent *(lease_id.commission_percent/100))/365 * refund_cmpny_no_of_days
            else:
                if lease_id.total_commission_percent and lease_id.commission_percent:
                    rs_commission = lease_id.commission_percent *(lease_id.total_commission_percent/100)
                    if no_of_days_refund < 365:
                        refund_commission = (lease_id.monthly_rent *(rs_commission/100))/365 * no_of_days_refund  
                    if refund_cmpny_no_of_days < 365:
                        cmpny_refund_commission = (lease_id.monthly_rent *(rs_commission/100))/365 * refund_cmpny_no_of_days
            
            worksheet.write(row,0,count,table_value_format_center)
            worksheet.write(row,1,lease_id.subproperty.name,table_value_format_center)
            worksheet.write(row,2,lease_id.subproperty.building_id.name,table_value_format_left)
            worksheet.write(row,3,lease_id.tenant_id.name,table_value_format_left)
            worksheet.write(row,4,agreement_start_date,table_value_format_center)
            worksheet.write(row,5,agreement_end_date,table_value_format_center)
            worksheet.write(row,6,rent_covered_upto,table_value_format_center)
            worksheet.write(row,7,no_of_days_refund,table_value_format_center)
            worksheet.write(row,8,cmpny_refund_commission,number_format)
            worksheet.write(row,9,'Agent' if lease_id.agent else 'Direct',table_value_format_center)
            worksheet.write(row,10,str(int(lease_id.commission_percent))+"%",table_value_format_center)
            worksheet.write(row,11,lease_id.agent_commission_amount,number_format)
            worksheet.write(row,12,refund_commission,number_format)
            worksheet.write(row,13,lease_id.adviser_id.name or '',number_format)
            worksheet.write(row,14,lease_id.agent.name or '',number_format)
            worksheet.write(row,15,lease_id.notes or '',number_format)
            
            count+=1
            row+=1
            
        

        row +=1 
        
        worksheet.merge_range('B%s:D%s'%(row,row),'* Include period up to which rental is covered',table_value_format_left)
        
        row+=3
        
        worksheet.write(row,0,'Accounts',left_heading_bold_format)
        
        row+=3
        worksheet.merge_range('A%s:C%s'%(row,row),'Already Finished One Year',left_heading_bold_format)
        
        
        row+=1
        worksheet.set_row(row, 30)
         
        worksheet.write('A%s'%(row), 'Sr No',text_heading_bold_center_fg1)
        worksheet.write('B%s'%(row), 'Flat',text_heading_bold_center_fg1)
        worksheet.write('C%s'%(row), 'Building Name',text_heading_bold_center_fg1)
        worksheet.write('D%s'%(row), 'Tenant Name',text_heading_bold_center_fg1)
        worksheet.write('E%s'%(row), 'From',text_heading_bold_center_fg1)
        worksheet.write('F%s'%(row), 'To',text_heading_bold_center_fg1)
        worksheet.write('G%s'%(row), 'Rent Covered Upto *',text_heading_bold_center_fg1)
        worksheet.write('H%s'%(row), 'No of days refund',text_heading_bold_center_fg1)
        worksheet.write('I%s'%(row), 'Commission Paid',text_heading_bold_center_fg1)
        worksheet.write('J%s'%(row), 'Direct/Agent',text_heading_bold_center_fg1)
        worksheet.write('K%s'%(row), '% of Commission paid -PA',text_heading_bold_center_fg1)
        worksheet.write('L%s'%(row), 'Commission Deduction from PA',text_heading_bold_center_fg1)
        worksheet.write('M%s'%(row), 'Agent Comm. Refund Claim',text_heading_bold_center_fg1)
        worksheet.write('N%s'%(row), 'Sales Executive',text_heading_bold_center_fg1)
        worksheet.write('O%s'%(row), 'Agent Name',text_heading_bold_center_fg1)
        worksheet.write('P%s'%(row), 'Comments / claim on agent made ?',text_heading_bold_center_fg1)
        
        
        
        lease_agreement_ids = self.env['zbbm.module.lease.rent.agreement'].search([('state','in',['active','terminate']),('agreement_start_date','>=',wiz.from_date),('agreement_start_date','<=',wiz.to_date)],order='agreement_start_date asc')
        
        lease_plan_dates = []
        count = 1
        for lease in lease_agreement_ids:
            
            lease_plan_dates = []
            if lease.invoice_plan_ids:
                for plan in lease.invoice_plan_ids:
                    if plan.move_id and plan.move_id.amount_residual == 0.000:
                        lease_plan_dates.append(plan.inv_date)
            if lease_plan_dates:
                lease_rent_covered_upto = max(lease_plan_dates)
                lease_rent_covered_upto = datetime.strptime(str(lease_rent_covered_upto),'%Y-%m-%d').strftime('%d-%m-%Y')
            else:
                lease_rent_covered_upto = ''
            
            agreement_start_date = datetime.strptime(str(lease.agreement_start_date),'%Y-%m-%d').strftime('%d-%m-%Y')
            agreement_end_date = datetime.strptime(str(lease.agreement_end_date),'%Y-%m-%d').strftime('%d-%m-%Y')
            
            lease_no_of_days_refund = 0.000
            lease_refund_cmpny_no_of_days = 0.000
            
            if lease.termination_date and lease.termination_date >= lease.agreement_end_date and lease.termination_date >= wiz.from_date and lease.termination_date <= wiz.to_date:
                lease_no_of_days_refund = (datetime.strptime(str(lease.agreement_end_date), '%Y-%m-%d')-datetime.strptime(str(lease.termination_date), '%Y-%m-%d')).days + 1
                lease_refund_cmpny_no_of_days = (datetime.strptime(str(lease.termination_date), '%Y-%m-%d')-datetime.strptime(str(lease.agreement_start_date), '%Y-%m-%d')).days + 1
            else:
                if date.today() >= lease.agreement_end_date:
                    lease_no_of_days_refund = (datetime.strptime(str(date.today()), '%Y-%m-%d')-datetime.strptime(str(lease.agreement_start_date), '%Y-%m-%d')).days + 1
                    lease_refund_cmpny_no_of_days = (datetime.strptime(str(date.today()), '%Y-%m-%d')-datetime.strptime(str(lease.agreement_start_date), '%Y-%m-%d')).days + 1

            lease_cmpny_refund_commission = 0.000
            lease_refund_commission = 0.000
            if not lease.total_commission_percent and lease.commission_percent:
                if lease_no_of_days_refund >= 365:
                    lease_refund_commission = lease.monthly_rent *(lease.commission_percent/100)   
                if lease_refund_cmpny_no_of_days >= 365:
                    lease_cmpny_refund_commission = lease.monthly_rent *(lease.commission_percent/100)   
            else:
                if lease.total_commission_percent and lease.commission_percent:
                    rs_commission = lease.commission_percent *(lease.total_commission_percent/100)
                    if lease_no_of_days_refund >= 365:
                         lease_refund_commission = lease.monthly_rent *(rs_commission/100)  
                    if lease_refund_cmpny_no_of_days >= 365:
                        lease_cmpny_refund_commission = lease.monthly_rent *(rs_commission/100)    
            
            
            
            worksheet.write(row,0,count,table_value_format_center)
            worksheet.write(row,1,lease.subproperty.name,table_value_format_center)
            worksheet.write(row,2,lease.subproperty.building_id.name,table_value_format_left)
            worksheet.write(row,3,lease.tenant_id.name,table_value_format_left)
            worksheet.write(row,4,agreement_start_date,table_value_format_center)
            worksheet.write(row,5,agreement_end_date,table_value_format_center)
            worksheet.write(row,6,lease_rent_covered_upto,table_value_format_center)
            worksheet.write(row,7,lease_no_of_days_refund,table_value_format_center)
            worksheet.write(row,8,lease_cmpny_refund_commission,number_format)
            worksheet.write(row,9,'Agent' if lease.agent else 'Direct',table_value_format_center)
            worksheet.write(row,10,str(int(lease.commission_percent))+"%",table_value_format_center)
            worksheet.write(row,11,lease.agent_commission_amount,number_format)
            worksheet.write(row,12,lease_refund_commission,number_format)
            worksheet.write(row,13,lease.adviser_id.name or '',number_format)
            worksheet.write(row,14,lease.agent.name or '',number_format)
            worksheet.write(row,15,lease.notes or '',number_format)
            
            count+=1
            row+=1

        
        
        
