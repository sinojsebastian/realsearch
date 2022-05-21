from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage

from dateutil.rrule import rrule, DAILY


import logging
_logger = logging.getLogger(__name__)



class BuildingIncomeStatement(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_building_income_statement'
    _description = 'Building Wise Income Statement Report'
    _inherit = 'report.report_xlsx.abstract'

    
    def generate_xlsx_report(self, workbook, data, wiz):
         

        worksheet= workbook.add_worksheet('Building Wise Income Statement Report')
        
        title1 = workbook.add_format({'align': 'left','bold': True, 'size': 10,})
        title1.set_text_wrap()
        heading_format = workbook.add_format({'align': 'center','size': 20,'bold':True})
        heading_bold_left = workbook.add_format({'size': 11,'bold':True,'align': 'left'})
        heading_bold_right = workbook.add_format({'size': 11,'bold':True,'align': 'right'})
        text_heading_bold_left = workbook.add_format({'size': 10,'bold':True,'align': 'left','fg_color': '#FFFF00'})
        text_heading_bold_left_fg1 = workbook.add_format({'size': 10,'bold':True,'align': 'left','fg_color': '#FFA500'})
        text_heading_bold_center = workbook.add_format({'align': 'center','size': 10,'bold':True,'fg_color': '#FFFF00'})
        number_format = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','num_format': '#,###0.000'})
        table_value_format = workbook.add_format({'align': 'right','size': 10})
        number_format_bold_right = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000'})
        number_format_bold_right_fg = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000','fg_color': '#FFFF00'})
        number_format_bold_right_fg1 = workbook.add_format({'size': 10,'align': 'right', 'valign': 'right','bold':True,'num_format': '#,###0.000','fg_color': '#FFA500'})

        formater = workbook.add_format({'border': 1})
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        
        worksheet.set_row(1, 25)
        worksheet.set_column('A:A', 50)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        
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
        
        worksheet.merge_range('B1:C5','%s \n %s \n %s \n %s \n %s \n  %s'%(cmpny_name,street,street2,city,country_id,email),title1)
        worksheet.insert_image('A1:A4','picture.png', {'image_data': logo,'x_offset': 0,'x_scale': 0.13, 'y_scale': 0.13})

        wiz_from_date = datetime.strptime(str(wiz.from_date),'%Y-%m-%d').strftime('%m/%d/%Y')
        wiz_to_date = datetime.strptime(str(wiz.to_date),'%Y-%m-%d').strftime('%m/%d/%Y')
        wiz_building = wiz.building_id
        wiz_product = wiz.service_product_id
        
        worksheet.merge_range('A6:C6',cmpny_name,heading_format)
        
        worksheet.merge_range('A8:C8','Building - ' + str(wiz_building.name),heading_bold_left)
        worksheet.write('A9','Building Wise Profit & Loss A/c- ' + str(wiz_building.name),heading_bold_left)
        worksheet.write('A10','Reporting Period',heading_bold_left)
        worksheet.write('B10',wiz_from_date,heading_bold_right)
        worksheet.write('C10',wiz_to_date,heading_bold_right)
        
        
        worksheet.write('A11', 'Income',text_heading_bold_left)
        worksheet.write('B11', 'Actual',text_heading_bold_left)
        worksheet.write('C11', 'Budget',text_heading_bold_center)
        
        
        income_account_ids = self.env['account.account'].search([('user_type_id.id','=',13)])
        expense_account_ids = self.env['account.account'].search([('user_type_id.id','=',15)])
        
        analytic_account_id = self.env['account.analytic.account'].search([('building_id','=',wiz_building.id)])
        budget_line_ids = self.env['crossovered.budget.lines'].search([('analytic_account_id','=',analytic_account_id.id)])
        
        params = self.env['ir.config_parameter'].sudo()
        service_income_ids = params.get_param('zb_bf_custom.income_account_ids')
        income_list=[]
        if service_income_ids:
            inv=service_income_ids[1:-1].split(',')
            for income in inv:
                if income:
                    income_list.append(int(income))
        
        wiz_days = ((wiz.to_date - wiz.from_date).days)+1
        row = 12
        total_income = 0.000
        total_budget = 0.000
        worksheet.write('A12', 'Income',heading_bold_left)
        for account_id in income_account_ids:
            if account_id.id in income_list:
                worksheet.write(row,0,account_id.name,table_value_format)
                move_line_ids = self.env['account.move.line'].search([('analytic_account_id','=',wiz.building_id.analytic_account_id.id),('account_id','=',account_id.id),('date','>=',wiz.from_date),('date','<=',wiz.to_date),('move_id.building_id','=',wiz_building.id),('move_id.state','=','posted'),('product_id','=',wiz_product.id)])
                income_actual_amount = 0.000
                column =1
                for line_id in move_line_ids:
                    income_actual_amount = income_actual_amount +(-(line_id.debit-line_id.credit))
                    worksheet.write(row,column,income_actual_amount,number_format)
                total_income += income_actual_amount
                
                budget_amount = 0.000
                amount_budget = 0.000
                for budget_line in budget_line_ids:
                    if wiz.from_date >= budget_line.date_from and wiz.from_date <= budget_line.date_to and wiz.to_date >= budget_line.date_from and wiz.to_date <= budget_line.date_to:
                        if budget_line.general_budget_id and budget_line.general_budget_id.account_ids:
                            for account in budget_line.general_budget_id.account_ids:
                                if account.code == account_id.code:
                                    budget_from_date = budget_line.date_from
                                    budget_to_date = budget_line.date_to
                                    delta = budget_to_date - budget_from_date
                                    budget_days = delta.days
                                    amount_budget = (budget_line.planned_amount/budget_days) * wiz_days
                                    budget_amount += amount_budget
                                    total_budget+=amount_budget
                worksheet.write(row,2,budget_amount if budget_amount else '',number_format)
                row+=1
        
        row+=1
        
        worksheet.write(row, 0,'Income (A)',heading_bold_left)
        worksheet.write(row, 1,total_income,number_format_bold_right)
        worksheet.write(row, 2,total_budget,number_format_bold_right)
        
        
        other_total_income = 0.000
        other_total_budget = 0.000
        if wiz.report_for == 'management':
            row+=2
            worksheet.write(row, 0,'Other Income (B)',heading_bold_left)
            row+=1
            for account_id in income_account_ids:
                if account_id.id not in income_list:
                    worksheet.write(row,0,account_id.name,table_value_format)
                    move_line_ids = self.env['account.move.line'].search([('analytic_account_id','=',wiz.building_id.analytic_account_id.id),('account_id','=',account_id.id),('date','>=',wiz.from_date),('date','<=',wiz.to_date),('move_id.building_id','=',wiz_building.id),('move_id.state','=','posted'),('product_id','=',wiz_product.id)])
                    other_income_actual_amount = 0.000
                    column =1
                    for line_id in move_line_ids:
                        other_income_actual_amount = other_income_actual_amount +(-(line_id.debit-line_id.credit))
                        worksheet.write(row,column,other_income_actual_amount,number_format)
                    other_total_income += other_income_actual_amount
                    
                    other_budget_amount = 0.000
                    other_amount_budget = 0.000
                    for budget_line in budget_line_ids:
                        if wiz.from_date >= budget_line.date_from and wiz.from_date <= budget_line.date_to and wiz.to_date >= budget_line.date_from and wiz.to_date <= budget_line.date_to:
                            if budget_line.general_budget_id and budget_line.general_budget_id.account_ids:
                                for account in budget_line.general_budget_id.account_ids:
                                    if account.code == account_id.code:
                                        budget_from_date = budget_line.date_from
                                        budget_to_date = budget_line.date_to
                                        delta = budget_to_date - budget_from_date
                                        budget_days = delta.days
                                        other_amount_budget += (budget_line.planned_amount/budget_days) * wiz_days
                                        other_budget_amount = other_amount_budget
                                        other_total_budget += other_amount_budget
                    
                    worksheet.write(row,2,other_budget_amount if other_budget_amount else '',number_format)
                    row+=1
            row+=1
            worksheet.write(row, 0,' Total Income ( C )',heading_bold_left)
            worksheet.write(row, 1,other_total_income+total_income,number_format_bold_right)
            worksheet.write(row, 2,other_total_budget+total_budget,number_format_bold_right)
            
        
        row+=2
        worksheet.write(row, 0,'Expenses',heading_bold_left)
        row+=1
        total_expense = 0.000
        expense_total_budget= 0.000
        for account_id in expense_account_ids:
            worksheet.write(row,0,account_id.name,table_value_format)
            move_line_ids = self.env['account.move.line'].search([('analytic_account_id','=',wiz.building_id.analytic_account_id.id),('account_id','=',account_id.id),('date','>=',wiz.from_date),('date','<=',wiz.to_date),('move_id.building_id','=',wiz_building.id),('move_id.state','=','posted'),('product_id','=',wiz_product.id)])
            expense_actual_amount = 0.000
            column =1
            for line_id in move_line_ids:
                expense_actual_amount = expense_actual_amount +(line_id.debit-line_id.credit)
                worksheet.write(row,column,expense_actual_amount,number_format)
            total_expense += expense_actual_amount
            
            
            expense_budget_amount = 0.000
            expense_amount_budget = 0.000
            for budget_line in budget_line_ids:
                if wiz.from_date >= budget_line.date_from and wiz.from_date <= budget_line.date_to and wiz.to_date >= budget_line.date_from and wiz.to_date <= budget_line.date_to:
                    if budget_line.general_budget_id and budget_line.general_budget_id.account_ids:
                        for account in budget_line.general_budget_id.account_ids:
                            if account.code == account_id.code:
                                budget_from_date = budget_line.date_from
                                budget_to_date = budget_line.date_to
                                delta = budget_to_date - budget_from_date
                                budget_days = delta.days
                                expense_amount_budget += (budget_line.planned_amount/budget_days)* wiz_days
                                expense_budget_amount = expense_amount_budget
                                expense_total_budget += expense_amount_budget
                worksheet.write(row,2,expense_budget_amount if expense_budget_amount else '',number_format)
            row+=1
            
            
        row+=1
        worksheet.set_row(row, 30)
        worksheet.write(row, 0,'Total Expenses (D)    ',heading_bold_left)
        worksheet.write(row, 1,total_expense,number_format_bold_right)
        worksheet.write(row, 2,expense_total_budget,number_format_bold_right)
        
        row+=2
        worksheet.write(row, 0,'Net Income From '+str(wiz_building.name)+'(Type 1 Report) A- D',text_heading_bold_left)
        worksheet.write(row, 1,total_income-total_expense,number_format_bold_right_fg)
        worksheet.write(row, 2,total_budget-expense_total_budget,number_format_bold_right_fg)
        
        row+=1
        worksheet.write(row, 0,'Net Income From '+str(wiz_building.name)+'(Type 2 Report) C- D',text_heading_bold_left_fg1)
        worksheet.write(row, 1,other_total_income-total_expense,number_format_bold_right_fg1)
        worksheet.write(row, 2,other_total_budget-expense_total_budget,number_format_bold_right_fg1)
        
        row+=1
        worksheet.conditional_format('A11:C%s'%(str(row)), { 'type' : 'no_blanks' ,'format' : formater})
        worksheet.conditional_format('A11:C%s'%(str(row)), { 'type' : 'blanks' ,'format' : formater})
        
        
        
        
        
        
    
        
        
        
        