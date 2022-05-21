from odoo import models
from datetime import datetime, timedelta,date
import base64 
from io import BytesIO 
from PIL import Image as PILImage

from dateutil.rrule import rrule, DAILY


import logging
_logger = logging.getLogger(__name__)



class ProjectIncomeStatement(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_project_income_statement'
    _description = 'Project Wise Income Statement Report'
    _inherit = 'report.report_xlsx.abstract'

    
    def generate_xlsx_report(self, workbook, data, wiz):
         

        worksheet= workbook.add_worksheet('Project Wise Income Statement Report')
        
        worksheet.set_column('A:A', 10)
        worksheet.set_column('C:C', 18)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        
        title1 = workbook.add_format({'align': 'left','size':10,'bold':True})
        style = workbook.add_format({'size': 10,'bold':True,'border':1,'align': 'center','valign':'center'})
        style1 = workbook.add_format({'size': 10,'bold':True,'border':1,'align': 'left'})
        net_profit = workbook.add_format({'size': 10,'bold':True,'align': 'left'})
        net_profit_value = workbook.add_format({'size': 10,'bold':True,'align': 'right','top':1,'bottom':1,'num_format': '#,###0.000'})
        other_income_total_style = workbook.add_format({'size': 10,'align': 'right','valign': 'vcenter','num_format': '#,###0.000'})
        style2 = workbook.add_format({'size': 10,'bold':True,'border':1,'align': 'right'})
        
        table_value_format = workbook.add_format({'size': 10,'align': 'center','border':1})
        table_value_format1 = workbook.add_format({'size': 10,'align': 'left','border':1})
        table_bottom_value = workbook.add_format({'size': 10,'align': 'left'})
        table_bottom_value_right = workbook.add_format({'size': 10,'align': 'right'})
        amount_format = workbook.add_format({'size': 10,'align': 'right','num_format': '#,###0.000','border':1})
        amount_format_bold = workbook.add_format({'size': 10,'align': 'right','num_format': '#,###0.000','border':1,'bold':True})
        table_bottom_num = workbook.add_format({'size': 10,'align': 'right','num_format': '#,###0.000'})
        
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        if company_logo:
            data=base64.b64decode(company_logo) 
            im = PILImage.open(BytesIO(data)) 
            x = im.save('logo.png') 
        if cmpny.name:
            cmpny_name = cmpny.name
        
        worksheet.insert_image('A1:A4','logo.png',{'x_scale': 0.061, 'y_scale': 0.08})
        
        from_date = datetime.strptime(str(wiz.from_date),'%Y-%m-%d').strftime('%d %b %Y')
        to_date = datetime.strptime(str(wiz.to_date),'%Y-%m-%d').strftime('%d %b %Y')
        
        worksheet.merge_range('B3:C3','%s'%(cmpny_name),title1)
        worksheet.merge_range('B5:F5','Projectwise Income & Expenditure for the Period from %s to %s'%(from_date,to_date),title1)
        
        
        worksheet.write('B7', 'Sr No',style)
        worksheet.write('C7', 'Projects',style1)
        worksheet.write('D7', 'Service Charges',style)
        worksheet.write('E7', 'Direct Costs',style2)
        worksheet.write('F7','Gross Profit',style2) 
        
        params = self.env['ir.config_parameter'].sudo()  
        service_journal_id = params.get_param('zb_bf_custom.service_invoice_journal_id')
        expense_type_ids = params.get_param('zb_bf_custom.project_expense_type_ids')
        income_type_ids = params.get_param('zb_bf_custom.project_income_type_ids') or False
        
        #COA Fetching
        income_list=[]
        if income_type_ids:
            inv=income_type_ids[1:-1].split(',')
            
            for income in inv:
                if income:
                    income_list.append(int(income))
        
        expense_list=[]
        if expense_type_ids:
            inv=expense_type_ids[1:-1].split(',')
            for expense in inv:
                if expense:
                    expense_list.append(int(expense))
        
        expense_account_ids = self.env['account.account'].search([('user_type_id.id','in',expense_list)])
#         expense_list = [expense_account_ids]
        income_account_ids = self.env['account.account'].search([('user_type_id.id','in',income_list)])
        
        service_charge = 0.000
        dc = 0.000
        building_data = {}
        
        building_ids = self.env['zbbm.building'].search([('state','!=','delisted')])
        service_charge_sum = 0.000
        dc_sum =0.000
        for building in building_ids:
            
            self._cr.execute('''
                SELECT line.id 
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                JOIN account_account ac ON ac.id = line.account_id AND ac.user_type_id IN %s
                WHERE move.state = 'posted' 
                AND line.date >= %s and line.date <= %s
                AND move.building_id in (select id from zbbm_building where id=%s)
                
                 ''',[tuple(expense_list),wiz.from_date,wiz.to_date,building.id])
            moves=self._cr.fetchall()
            key =building.id
            direct_cost = 0.000
            total_direct_cost = 0.000
            #Direct cost Calculation
            for line in moves:
                line_id  = self.env['account.move.line'].browse(line[0])
                dc = line_id.move_id.amount_untaxed
                total_direct_cost += dc
            
            dc = total_direct_cost
            direct_cost += dc
                
             #service charge Fetching    
#             service_move_line_ids = self.env['account.move.line'].search([('move_id.state','=','posted'),('date','>=',wiz.from_date),('date','<=',wiz.to_date),('move_id.building_id.id','=',building.id)])
            self._cr.execute('''
                SELECT line.id 
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                JOIN account_account ac ON ac.id = line.account_id AND ac.user_type_id IN %s
                WHERE move.state = 'posted' 
                AND line.date >= %s and line.date <= %s
                AND line.journal_id in (select id from account_journal where id=%s) 
                AND move.building_id in (select id from zbbm_building where id=%s)
                
                 ''',[tuple(income_list),wiz.from_date,wiz.to_date,int(service_journal_id),building.id])
            service_moves=self._cr.fetchall()
            total_service_charge = 0.000
            for line in service_moves:
                line_id  = self.env['account.move.line'].browse(line[0])
                service_charge = line_id.move_id.amount_untaxed
                total_service_charge += service_charge
            
            #Total Service Income and Direct Cost
            service_charge = total_service_charge
            service_charge_sum += service_charge
            direct_cost_sum = direct_cost
            dc_sum += direct_cost_sum
            
            
            if key in building_data:
                building_data[key]['building'] = building.name
                building_data[key]['service_charge'] += total_service_charge
                building_data[key]['direct_cost'] += direct_cost
            else:
                building_data[key] = {
                                'building':building.name,
                                'service_charge':total_service_charge,
                                'direct_cost':direct_cost}
                

        #Other Income data fetching  
        income_data = {}
        self._cr.execute('''
                SELECT line.id 
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                JOIN account_account ac ON ac.id = line.account_id AND ac.user_type_id IN %s
                WHERE move.state = 'posted' 
                AND line.date >= %s and line.date <= %s
                AND move.building_id IS NULL AND move.module_id IS NULL
                
                 ''',[tuple(income_list),wiz.from_date,wiz.to_date])
        income_moves=self._cr.fetchall()
        income_moves_list = []
        for lines in income_moves:
            line_id  = self.env['account.move.line'].browse(lines[0])
            income_moves_list.append(line_id)
        for account_id in income_account_ids:
            sum_of_income = 0.000
            for move_line in income_moves_list:
            
                if account_id == move_line.account_id:
                    if income_data.get(account_id.id):
                        income_data[account_id.id]['account'] = account_id.name
                        income_data[account_id.id]['account_income'] += move_line.move_id.amount_untaxed
                    else:
                        income_data[account_id.id] = {
                                            'account':account_id.name,
                                            'account_income':move_line.move_id.amount_untaxed}
                else:
                    total_income = 0.000
                    if income_data.get(account_id.id):
                        income_data[account_id.id]['account'] = account_id.name
                        income_data[account_id.id]['account_income'] += total_income
                    else:
                        income_data[account_id.id] = {
                                            'account':account_id.name,
                                            'account_income':total_income}
        
        
        row = 7
        count = 1
         
        for k,v in building_data.items():
            worksheet.write(row,1, count ,table_value_format)
            worksheet.write(row, 2, v['building'], table_value_format1)
            worksheet.write(row, 3, v['service_charge'], amount_format)
            worksheet.write(row, 4, v['direct_cost'], amount_format)
            worksheet.write(row, 5, v['service_charge']-v['direct_cost'], amount_format)
            count+=1
            row += 1
        worksheet.write(row,1, '' ,style1)
        worksheet.write(row,2, 'Total' ,style1)
        worksheet.write(row,3,service_charge_sum,amount_format_bold)
        worksheet.write(row,4,dc_sum,amount_format_bold)
        worksheet.write(row,5,service_charge_sum-dc_sum,amount_format_bold)
         
        worksheet.merge_range('B%s:C%s'%(row+2,row+2),'Other Income' ,table_bottom_value)
        
        initial_row = row+3
        row = row+3
        other_income_total = 0.000
        for k,v in income_data.items():
            worksheet.write(row,2,v['account'],table_bottom_value)
            worksheet.write(row,4,v['account_income'],table_bottom_num)
            other_income_total += v['account_income']
            row += 1
        
        self._cr.execute('''
                SELECT line.id 
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                JOIN account_account ac ON ac.id = line.account_id AND ac.user_type_id IN %s
                WHERE move.state = 'posted' 
                AND line.date >= %s and line.date <= %s
                AND move.building_id IS NULL AND move.module_id IS NULL
                
                 ''',[tuple(expense_list),wiz.from_date,wiz.to_date])
        expense_line_without_building=self._cr.fetchall()
        
        total_expense_without_building = 0.000
        
        for lines in expense_line_without_building:
            line_id  = self.env['account.move.line'].browse(lines[0])
            expense_without_building  = line_id.move_id.amount_untaxed
            total_expense_without_building += expense_without_building
        
        
        worksheet.merge_range('F%s:F%s'%(initial_row,row),other_income_total,other_income_total_style)
        worksheet.merge_range('D%s:E%s'%(row+1,row+1),'Common costs including staff cost',table_bottom_value_right)
        worksheet.write('F%s'%(row+1),total_expense_without_building,table_bottom_num)
        worksheet.write('E%s'%(row+2),'Net Profit',net_profit)
        net_profit = (service_charge_sum+other_income_total)-(dc_sum+total_expense_without_building)
        worksheet.write('F%s'%(row+2),net_profit,net_profit_value)
        
        
        
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        