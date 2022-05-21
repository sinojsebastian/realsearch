from odoo import models
from datetime import datetime, timedelta, date
import base64
from io import BytesIO
from PIL import Image as PILImage
from odoo.exceptions import UserError, Warning

import logging
from distutils.command.build import build
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from calendar import monthrange

_logger = logging.getLogger(__name__)


class BF_Rental_Report_Xlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.bf.rental.report'
    _description = 'BF Rental Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):
        title0 = workbook.add_format({'size': 11, 'bold': True,'bg_color': '#ffffff', 'border':1})
        title1 = workbook.add_format({'size': 9,'border': 1,'bold': True})
        title2 = workbook.add_format({'size': 9, 'bold': True, 'border': 1, 'align': 'center','valign': 'vcenter'})
        title3 = workbook.add_format({'size': 9, 'bold': True,'border': 1,'valign': 'vcenter','align': 'center' })
        title4 = workbook.add_format({'size': 9, 'border': 1,'bold':True,'valign': 'vcenter','align': 'right','num_format': '#,###0.000' })
        title5 = workbook.add_format({'size': 9, 'border': 1, })
        title6 = workbook.add_format({'size': 9, 'bold': True,'border': 1,'valign': 'vcenter','align': 'center' })
        wrap = workbook.add_format({'size': 10, 'bold': True, })
        wrap.set_text_wrap()
        # title1.set_bg_color('#ffffff')
        title2.set_bg_color('#bb9b53')
        title3.set_bg_color('#bb9b53')
        title4.set_bg_color('#bb9b53')
        title6.set_bg_color('#bb9b53')
        title6.set_text_wrap()
        summary_vals = workbook.add_format({'size': 9, 'border': 1, 'align': 'left','valign': 'vcenter'})
        amount_style = workbook.add_format({'size': 9, 'border': 1, 'align': 'right','num_format': '#,###0.000','valign': 'vcenter'})
        gross_payable = workbook.add_format({'bold': True,'size': 9, 'border': 1, 'align': 'left','valign': 'vcenter'})
        grand_amount = workbook.add_format({'bold': True,'size': 9, 'border': 1, 'align': 'right','num_format': '#,###0.000','valign': 'vcenter'})
        prep_by = workbook.add_format({'bold': True,'size': 9, 'top': 1, 'align': 'left','valign': 'vcenter'})
        amount_right = workbook.add_format({'size': 9, 'border': 1, 'align': 'right','num_format': '#,###0.000','valign': 'vcenter'})
        amount_center = workbook.add_format({'size': 9, 'border': 1, 'align': 'center','num_format': '#,###0.000','valign': 'vcenter'})
        net_amt_red = workbook.add_format({'size': 9, 'border': 1, 'align': 'right','num_format': '#,###0.000','valign': 'vcenter','bg_color':'#ffcccb','color':'red'})
        net_amt_style = workbook.add_format({'size': 9, 'border': 1, 'align': 'right','num_format': '#,###0.000','valign': 'vcenter'})
        bold_center = workbook.add_format({'size': 9, 'border': 1, 'align': 'center','bold':True,'valign': 'vcenter'})
        
        build_vals = workbook.add_format({'size': 9, 'border': 1, 'align': 'center','valign': 'vcenter'})
        build_vals.set_text_wrap()

        # Summary
        # Summary
        worksheet = workbook.add_worksheet('Summary')

        # worksheet.set_row(10, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B',8)
        worksheet.set_column('C:C', 35)
        worksheet.set_column('D:D', 18)

        cmpny = self.env.user.company_id
        if self.env.user.company_id.logo:
            data = base64.b64decode(self.env.user.company_id.logo)
            im = PILImage.open(BytesIO(data))
            x = im.save('logo.png')

        if cmpny.name:
            cmpny_name = cmpny.name
        else:
            cmpny_name = ''
            
        current_month_first_date = datetime.strptime('%s-%s-%s'%(1,wiz.month,wiz.year),'%d-%m-%Y')
        month_start_date = current_month_first_date.strftime('%d-%b-%Y')
        # current_month_last_date = current_month_first_date.replace(day = monthrange(current_month_first_date.year, current_month_first_date.month)[1])
        end_date = current_month_first_date.replace(day = monthrange(current_month_first_date.year, current_month_first_date.month)[1])
        end_date_format = end_date.strftime('%d-%b-%y')
        month_end_date = end_date.strftime('%d-%b-%Y')
        # datetime.strptime(str(wiz.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%b-%y')
        
        worksheet.merge_range('B1:C5', '\n%s\n\nBF Rental Payment Summary\n\nFor the peirod end %s\nAll amounts in BD' % (cmpny_name,end_date_format), title1)
        worksheet.insert_image('D1:D5', 'logo.png', {'x_scale': 0.11, 'y_scale': 0.08})
        
        building_list = []
        params = self.env['ir.config_parameter'].sudo()
        owner_id = params.get_param('zb_bf_custom.owner_id')
        module_ids = self.env['zbbm.module'].search([('owner_id','=',int(owner_id))])
        summary_dict = {}
        pa_ids = ''
        commission_journal_id = params.get_param('zb_bf_custom.commission_journal_id') or False,
        mgt_fee_journal_id = params.get_param('zb_bf_custom.management_fee_journal_id') or False,
        ewa_journall_id = params.get_param('zb_bf_custom.ewa_journal_id') or False,
        int_journall_id = params.get_param('zb_bf_custom.internet_journal_id') or False,
        service_journal_id = params.get_param('zb_bf_custom.service_journal_id') or False,
        maintenance_journal_id = params.get_param('zb_bf_custom.maintenance_journal_id') or False,
        rent_transfer_journal_id = params.get_param('zb_bf_custom.rent_transfer_journal_id') or False
        for module in module_ids:
            deduction_dict = {}
            rent_dict = {}
            building_key = module.building_id
            module_key = module
            pa_ids = self.env['account.payment'].search([('payment_advise','=',True),('partner_id','=',int(owner_id)),('payment_date','>=',current_month_first_date),('payment_date','<=',end_date),('module_id','=',module.id),('state','in',['posted','reconciled'])])
            print('===============pa_ids===================',pa_ids)
            payment_list = pa_ids.ids
            for payment in pa_ids:
                amount_total = 0
                for line in payment.payment_line_ids:
                    if line.allocation:
                        if line.debit:
                            if line.inv_id.journal_id.id == int(commission_journal_id[0]):
                                if 'commission' in deduction_dict:
                                    deduction_dict['commission'] += line.allocation
                                else:
                                    deduction_dict.update({'commission':line.allocation})
                            elif line.inv_id.journal_id.id == int(mgt_fee_journal_id[0]):
                                if 'mgt_fee' in deduction_dict:
                                    deduction_dict['mgt_fee'] += line.allocation
                                else:
                                    deduction_dict.update({'mgt_fee':line.allocation})
                            elif line.inv_id.journal_id.id == int(ewa_journall_id[0]):
                                if 'ewa' in deduction_dict:
                                    deduction_dict['ewa'] += line.allocation
                                else:
                                    deduction_dict.update({'ewa':line.allocation})
                            elif line.inv_id.journal_id.id == int(int_journall_id[0]):
                                if 'internet' in deduction_dict:
                                    deduction_dict['internet'] += line.allocation
                                else:
                                    deduction_dict.update({'internet':line.allocation})
                            elif line.inv_id.journal_id.id == int(service_journal_id[0]):
                                if 'service' in deduction_dict:
                                    deduction_dict['service'] += line.allocation
                                else:
                                    deduction_dict.update({'service':line.allocation})
                            elif line.inv_id.journal_id.id == int(maintenance_journal_id[0]):
                                if 'maintenance' in deduction_dict:
                                    deduction_dict['maintenance'] += line.allocation
                                else:
                                    deduction_dict.update({'maintenance':line.allocation})
                            elif line.inv_id.type == 'out_invoice':
                                sales = line.inv_id.invoice_line_ids.sale_line_ids.mapped('order_id')
                                if sales:
                                    if 'maintenance' in deduction_dict:
                                        deduction_dict['maintenance'] += line.allocation
                                    else:
                                        deduction_dict.update({'maintenance':line.allocation})
                                else:
                                    if 'other' in deduction_dict:
                                        deduction_dict['other'] += line.allocation
                                    else:
                                        deduction_dict.update({'other':line.allocation})
                            elif line.inv_id.raw_service_id and line.inv_id.raw_service_id.product_id.id in [9,1626]:
                                if 'cleaning' in deduction_dict:
                                    deduction_dict['cleaning'] += line.allocation
                                else:
                                    deduction_dict.update({'cleaning':line.allocation})
                            else:
                                if 'other' in deduction_dict:
                                    deduction_dict['other'] += line.allocation
                                else:
                                    deduction_dict.update({'other':line.allocation})
                                
                        if line.credit:
                            if line.inv_id.journal_id.id == int(rent_transfer_journal_id):
                                if 'rent_received' in rent_dict:
                                    rent_dict['rent_received'] += line.allocation
                                else:
                                    rent_dict.update({'rent_received':line.allocation})
                            else:
                                if 'other_income' in rent_dict:
                                    rent_dict['other_income'] += line.allocation
                                else:
                                    rent_dict.update({'other_income':line.allocation})
                
                if payment.advance_expense_ids:
                    for exp in payment.advance_expense_ids:
                        if 'other' in deduction_dict:
                            deduction_dict['other'] += exp.amount
                        else:
                            deduction_dict.update({'other':exp.amount})
                
                # deduction_dict.update({'cleaning':0.00})
                if building_key in summary_dict:
                    if module_key in summary_dict[building_key]:
                        if 'amount' in summary_dict[building_key][module_key]:
                            summary_dict[building_key][module_key]['amount'] += payment.amount
                        else:
                            summary_dict[building_key][module_key].update({'amount':payment.amount,'payments':payment_list,'rent':rent_dict,'deduction':deduction_dict})
                    else:
                        summary_dict[building_key].update({module_key:{'amount':payment.amount,'payments':payment_list,'rent':rent_dict,'deduction':deduction_dict}})
                else:
                    summary_dict.update({building_key:{module_key:{'amount':payment.amount,'payments':payment_list,'rent':rent_dict,'deduction':deduction_dict}}})
        worksheet.set_row(6, 25)
        
        worksheet.write('B7', '#', title1)
        worksheet.write('C7', 'Building', title2)
        worksheet.write('D7', 'Amount', title2)
        
        row = 7
        column = 1
        count = 1
        amount_sum = 0
        for key,value in summary_dict.items():
            worksheet.write(row,column,count,summary_vals)
            worksheet.write(row,column+1,key.name,summary_vals)
            amount = 0
            for key1,val1 in value.items():
                amount += value[key1]['amount']
            worksheet.write(row,column+2,amount,amount_style)
            amount_sum += amount
            worksheet.set_row(row, 25)
            row+=1
            count += 1
        worksheet.set_row(row, 25)
        worksheet.write(row,1,'',summary_vals)
        worksheet.write(row,2,'Gross payable',gross_payable)
        worksheet.write(row,3,amount_sum,grand_amount)
        
        worksheet.set_row(row+1, 25)
        worksheet.write(row+1,1,'',title4)
        worksheet.write(row+1,2,'',title4)
        worksheet.write(row+1,3,'',title4)
        
        worksheet.set_row(28, 25)
        worksheet.write(28,1,'Prepared by',prep_by)
        worksheet.write(28,3,'Approved by',prep_by)
        
        
        
                        
        # BF Vacanct flat SC
        worksheet = workbook.add_worksheet('BF Vacanct flat SC')
        worksheet.set_row(10, 50)
        worksheet.set_row(6, 25)
        worksheet.set_column('B:B', 8)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        cmpny = self.env.user.company_id
        if self.env.user.company_id.logo:
            data = base64.b64decode(self.env.user.company_id.logo)
            im = PILImage.open(BytesIO(data))
            x = im.save('logo.png')
        if cmpny.name:
            cmpny_name = cmpny.name
        else:
            cmpny_name = ''
        # worksheet.write('B2', cmpny_name, title1)
        # worksheet.write('B4', 'BF service charge related to vacant flats', title1)
        # worksheet.write('B6', 'All amounts in BHD', title1)
        worksheet.merge_range('B1:G6', ' \n%s\n\n %s\n\n As of %s\n\n %s\n' %(cmpny_name,'BF service charge related to vacant flats',end_date_format,'All amounts in BHD' ), title1)

        # worksheet.insert_image('H1:I6', 'logo.png', {'x_scale': 0.06, 'y_scale': 0.06})
        worksheet.write('B7', 'SL NO', title3)
        worksheet.write('C7', 'Building Name', title3)
        worksheet.write('D7', 'Flat No', title3)
        worksheet.write('E7', 'Service Charges Period', title3)
        worksheet.write('F7', 'Service Charges full year', title6)
        worksheet.write('G7', 'Service Charges till %s'%(end_date_format), title6)
        
        sl_no = 1
        column = 1
        row = 7
        full_service_total = 0
        service_total = 0
        for building1,module1 in summary_dict.items():
            sl_no = sl_no
            row = row
            for module2,val3 in module1.items():
                if module2.state not in ['available','new']:
                    if 'service' in val3['deduction']:
                        worksheet.write(row, column,sl_no, build_vals)
                        worksheet.write(row, column+1, module2.building_id.name or '', build_vals)
                        worksheet.write(row, column+2, module2.name or '', build_vals)
                        service_period = []
                        sorted_service_dates = []
                        full_service_amt = 0
                        worksheet.set_row(row, 25)
                        for pay in val3['payments']:
                            pay_id = self.env['account.payment'].browse(pay)
                            for pay_line in pay_id.payment_line_ids:
                                if pay_line.allocation and pay_line.debit:
                                    if pay_line.inv_id.journal_id.id == int(service_journal_id[0]):
                                        from_date = pay_line.inv_id.from_date.strftime('%d-%m-%Y')
                                        to_date = pay_line.inv_id.to_date.strftime('%d-%m-%Y')
                                        if from_date not in service_period:
                                            service_period.append(from_date)
                                        if to_date not in service_period:
                                            service_period.append(to_date)
                                        full_service_amt += pay_line.inv_id.amount_total
                            service_dates = [datetime.strptime(sts, "%d-%m-%Y") for sts in service_period]
                            service_dates.sort()
                            sorted_service_dates = [datetime.strftime(sts, "%d-%m-%Y") for sts in service_dates]
                        worksheet.write(row, column+3,'%s to %s'%(sorted_service_dates[0],sorted_service_dates[-1]), summary_vals)
                        worksheet.write(row, column+4,full_service_amt, amount_right)
                        full_service_total += full_service_amt
                        service_months = (end_date.date().year - datetime.strptime(sorted_service_dates[0],'%d-%m-%Y').date().year)*12+(end_date.date().month - datetime.strptime(sorted_service_dates[0],'%d-%m-%Y').date().month)
                        service_amt = (full_service_amt/12)*service_months
                        worksheet.write(row, column+5,service_amt or 0.00, amount_right)
                        service_total += service_amt
                        row += 1
                        sl_no += 1
        worksheet.write(row,1,'',title4)
        worksheet.write(row,2,'',title4)
        worksheet.write(row,3,'',title4)
        worksheet.write(row,4,'',title4)
        worksheet.write(row,5,full_service_total,title4)
        worksheet.write(row,6,service_total,title4)
            # row += 1
            # sl_no += 1


        #Building Worksheet
        to_date = end_date.strftime('%m/%y')
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        for building,module in summary_dict.items():
            worksheet = workbook.add_worksheet('%s' % (building.name))
            worksheet.set_column('A:A', 10)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 35)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 12,None, {'hidden': True})
            worksheet.set_column('G:G', 12)
            worksheet.set_column('H:H', 15)
            worksheet.set_column('I:I', 15)
            worksheet.set_column('J:J', 15)
            worksheet.set_column('K:K', 15)
            worksheet.set_column('L:L', 15)
            worksheet.set_column('M:M', 15)
            worksheet.set_column('N:N', 15)
            worksheet.set_column('O:O', 15)
            worksheet.set_column('P:P', 15)
            worksheet.set_column('Q:Q', 15)
            worksheet.set_column('R:R', 15)
            worksheet.set_column('S:S', 15)
            worksheet.set_column('T:T', 15)
            worksheet.merge_range('A6:A7', 'Flat No', title2)
            worksheet.merge_range('B6:B7', 'Status', title2)
            worksheet.merge_range('C6:C7', 'Tenant Name', title2)
            worksheet.merge_range('D6:D7', 'Opening Balance', title2)
            worksheet.merge_range('E6:E7', 'Rental Income December', title2)
            worksheet.merge_range('F6:F7', 'Discount', title2)
            worksheet.merge_range('G6:G7', 'Received', title2)
            worksheet.merge_range('H6:H7', 'Closing Balance', title2)
            worksheet.merge_range('I6:J6', 'Period', title2)
            worksheet.write('I7', 'From', title2)
            worksheet.write('J7', 'To', title2)
            worksheet.merge_range('K6:K7', 'EWA/other Income', title2)
            # worksheet.merge_range('K6:k7', 'EWA/other Income', title2)
            worksheet.merge_range('L6:S6', 'Deductions', title2)
            worksheet.write('L7', 'Commission', title2)
            worksheet.write('M7', 'Mgt Free', title2)
            worksheet.write('N7', 'EWA', title2)
            worksheet.write('O7', 'Internet', title2)
            worksheet.write('P7', 'Service Charges', title2)
            worksheet.write('Q7', 'Maintenance', title2)
            worksheet.write('R7', 'Cleaning', title2)
            worksheet.write('S7', 'Other', title2)
            worksheet.merge_range('T6:T7', 'Net payable', title2)

            worksheet.merge_range('A1:C5', '\n Building: \n\n BF Flats Rental Statement \n\n Month \n ', title1)
            worksheet.merge_range('D1:D5', '\n %s \n\n  \n\n %s \n ' % (building.name, to_date,), title1)
            row = 7
            column = 0
            ewa_journal_id = params.get_param('zb_bf_custom.ewa_journal_id') or False,
            opening_balance_total = 0
            rent_inc_total = 0
            rent_received_total = 0
            other_inc_total = 0
            closing_balance_total = 0
            ewa_inc_total = 0
            commission_total = 0
            mgt_total = 0
            ewa_total = 0
            internet_total = 0
            service_charge_total = 0
            maintenance_total = 0
            cleaning_total = 0
            other_total = 0
            net_payable_total = 0
            for module,val2 in module.items():
                period_list = []
                rent_inc = 0
                opening_balance = 0.00
                closing_balance = 0.00
                current_rent_inv_ids = self.env['account.move'].search([('invoice_date','<=',end_date.date()),('invoice_date','>=',current_month_first_date.date()),('module_id','=',module.id),('state','=','posted'),('type','=','out_invoice'),('journal_id','=',int(rent_invoice_journal_id))])
                prev_rent_inv_ids = self.env['account.move'].search([('invoice_date','<',current_month_first_date.date()),('module_id','=',module.id),('state','=','posted'),('type','=','out_invoice'),('journal_id','=',int(rent_invoice_journal_id))])
                rent_transfer_ids = self.env['account.move'].search([('date','<=',end_date.date()),('date','>=',current_month_first_date.date()),('module_id','=',module.id),('state','=','posted'),('type','=','entry'),('journal_id','=',int(rent_transfer_journal_id))])
                rent_received = 0
                other_income = 0
                for inv in current_rent_inv_ids:
                    date_str = inv.invoice_date.strftime('%d-%b-%Y')
                    if date_str not in period_list:
                        period_list.append(date_str)
                    rent_inc += inv.amount_total
                for prev_inv in prev_rent_inv_ids:
                    if prev_inv.amount_residual:
                        date_str_prev = prev_inv.invoice_date.strftime('%d-%b-%Y')
                        if date_str_prev not in period_list:
                            period_list.append(date_str_prev)
                    opening_balance += prev_inv.amount_residual
                # for rec in rent_transfer_ids:
                #     rent_received += rec.amount_total 
                dates = [datetime.strptime(ts, "%d-%b-%Y") for ts in period_list]
                dates.sort()
                # sorteddates = [datetime.strftime(ts, "%d-%b-%Y") for ts in dates]
                # if not sorteddates:
                #     sorteddates.append(datetime.strftime(3, "%d-%b-%Y"))
                # if len(sorteddates) == 1:
                #     sorteddates.append(datetime.strftime(end_date, "%d-%b-%Y"))
                # rent_transfer_ids = self.env['account.move'].search([('journal_id','=',int(rent_transfer_journal_id)),('module_id','=',module.id),('state','=','posted')])
                # for rent in rent_transfer_ids:
                #     if rent.date.month == wiz.to_date.month:
                #         rent_received += rent.amount_total
                # ewa_ids = self.env['account.move'].search([('date','<=',end_date.date()),('module_id','=',module.id),('state','=','posted'),('type','=','out_invoice'),('journal_id','=',int(ewa_journal_id[0]))])
                # ewa_amt = 0
                # for ewa in ewa_ids:
                #     if ewa.partner_id.id == module.tenant_id.id:
                #         ewa_amt += ewa.amount_total-ewa.amount_residual
                worksheet.set_row(row, 20)
                worksheet.write(row, column, module.name or '', build_vals)
                if module.state in ['occupied']:
                    state = dict(self.env['zbbm.module'].fields_get(allfields=['state'])['state']['selection'])[module.state]
                else:
                    state = 'Empty'
                worksheet.write(row, column+1, state, build_vals)
                worksheet.write(row, column+2, module.tenant_id.name or '', build_vals)
                worksheet.write(row, column+3, opening_balance if opening_balance else '', amount_right)
                opening_balance_total += opening_balance
                worksheet.write(row, column+4, rent_inc or 0.00, amount_right)
                rent_inc_total += rent_inc
                if 'rent_received' in val2['rent']:
                    rent_received = val2['rent']['rent_received']
                    rent_received_total += val2['rent']['rent_received']
                closing_balance = (opening_balance+rent_inc)-rent_received
                closing_balance_total += closing_balance
                
                worksheet.write(row, column+6, rent_received, amount_right)
                worksheet.write(row, column+7,closing_balance, amount_right)
                worksheet.write(row, column+8,month_start_date, build_vals)
                worksheet.write(row, column+9,month_end_date, build_vals)
                # if opening_balance == 0 and closing_balance == 0:
                #     worksheet.write(row, column+8,sorteddates[0], build_vals)
                #     worksheet.write(row, column+9,end_date.date().strftime('%d-%b-%Y'), build_vals)
                # else:
                #     worksheet.write(row, column+8,sorteddates[0], build_vals)
                #     worksheet.write(row, column+9,sorteddates[-1], build_vals)
                if 'other_income' in val2['rent']:
                    other_income = val2['rent']['other_income']
                    other_inc_total += val2['rent']['other_income']
                worksheet.write(row, column+10, other_income, amount_right)
                # ewa_inc_total += ewa_amt
                if 'commission' in val2['deduction']:
                    worksheet.write(row, column+11, val2['deduction']['commission'], amount_right)
                    commission_total += val2['deduction']['commission']
                else:
                    worksheet.write(row, column+11,'', amount_right)
                if 'mgt_fee' in val2['deduction']:
                    worksheet.write(row, column+12, val2['deduction']['mgt_fee'], amount_right)
                    mgt_total += val2['deduction']['mgt_fee']
                else:
                    worksheet.write(row, column+12,'', amount_right)
                if 'ewa' in val2['deduction']:
                    worksheet.write(row, column+13, val2['deduction']['ewa'], amount_right)
                    ewa_total += val2['deduction']['ewa']
                else:
                    worksheet.write(row, column+13,'', amount_right)
                if 'internet' in val2['deduction']:
                    worksheet.write(row, column+14, val2['deduction']['internet'], amount_right)
                    internet_total += val2['deduction']['internet']
                else:
                    worksheet.write(row, column+14,'', amount_right)
                if 'service' in val2['deduction']:
                    worksheet.write(row, column+15, val2['deduction']['service'], amount_right)
                    service_charge_total += val2['deduction']['service']
                else:
                    worksheet.write(row, column+15,'', amount_right)
                if 'maintenance' in val2['deduction']:
                    worksheet.write(row, column+16, val2['deduction']['maintenance'], amount_right)
                    maintenance_total += val2['deduction']['maintenance']
                else:
                    worksheet.write(row, column+16,'', amount_right)
                if 'cleaning' in val2['deduction']:
                    worksheet.write(row, column+17, val2['deduction']['cleaning'], amount_right)
                    cleaning_total += val2['deduction']['cleaning']
                else:
                    worksheet.write(row, column+17,'', amount_right)
                
                if 'other' in val2['deduction']:
                    worksheet.write(row, column+18, val2['deduction']['other'], amount_right)
                    other_total += val2['deduction']['other']
                else:
                    worksheet.write(row, column+18,'', amount_right)
                amt_deduction = 0
                if val2['deduction']:
                    for ded_key,ded_val in val2['deduction'].items():
                        amt_deduction += ded_val
                net_amt = 0
                if 'rent_received' in val2['rent']:
                    net_amt = val2['rent']['rent_received']-amt_deduction
                if 'other_income' in val2['rent']:
                    net_amt += val2['rent']['other_income']
                
                if net_amt < 0:
                    worksheet.write(row, column+19,net_amt, net_amt_red)
                    net_payable_total += net_amt
                else:
                    worksheet.write(row,column+19,net_amt, net_amt_style)
                    net_payable_total += net_amt
                row += 1
                
            worksheet.set_row(row, 25)
            worksheet.write(row,0,'',summary_vals)
            worksheet.write(row,1,'',summary_vals)
            worksheet.write(row,2,'Total',bold_center)
            worksheet.write(row,3,opening_balance_total,net_amt_style)
            worksheet.write(row,4,rent_inc_total,net_amt_style)
            worksheet.write(row,6,rent_received_total,net_amt_style)
            worksheet.write(row,7,closing_balance_total,net_amt_style)
            worksheet.write(row,8,'',summary_vals)
            worksheet.write(row,9,'',summary_vals)
            worksheet.write(row,10,other_inc_total,net_amt_style)
            worksheet.write(row,11,commission_total,net_amt_style)
            worksheet.write(row,12,mgt_total,net_amt_style)
            worksheet.write(row,13,ewa_total,net_amt_style)
            worksheet.write(row,14,internet_total,net_amt_style)
            worksheet.write(row,15,service_charge_total,net_amt_style)
            worksheet.write(row,16,maintenance_total,net_amt_style)
            worksheet.write(row,17,cleaning_total,net_amt_style)
            worksheet.write(row,18,other_total,net_amt_style)
            worksheet.write(row,19,net_payable_total,grand_amount)
            
            worksheet.merge_range('A%s:D%s'%(row+2,row+7), 'Note:\n\n\n\n Prepared by', gross_payable)
            worksheet.merge_range('E%s:T%s'%(row+2,row+7), 'Rent directly received BF \n\n\n\n Approved by', gross_payable)
                
            # rentable_units = self.env['zbbm.module'].search([('building_id', '=', record.id), (('managed','!=',False))])
            # m = 0
            # row = 7
            # column = 0
            # for units in rentable_units:
            #     worksheet.set_row(row + m, 25)
            #     worksheet.write(row + m, column, units.name or '', title5)
            #     worksheet.write(row + m, column + 1, record.state or '', title5)
            #     worksheet.write(row + m, column + 2, units.tenant_id.name or '', title5)
            #     m += 1






