# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsxAbstract

from datetime import datetime
from odoo import _, api, fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import logging

_logger = logging.getLogger(__name__)


LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)

class GeneralLedgerXlsx(models.AbstractModel):
    _name = 'report.zb_general_ledger.general.ledger.xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def get_opening_entry(self, account_id, from_date, target_move,partner_id):
        if not account_id.user_type_id.include_initial_balance:
            return {'debit': 0.00, 'credit': 0.00, 'amount_currency':0.00}
        where_cond = "where aml.account_id = %s and aml.date < '%s' and aml.company_id = %s"%(account_id.id, from_date,
                                                                                              self.env.user.company_id.id)
        if target_move == 'posted':
            where_cond += " and am.state = 'posted'"
        if partner_id:
            where_cond += " and aml.partner_id = %s"%(partner_id.id)
        query = """SELECT COALESCE(sum(aml.debit), 0.00) as debit, COALESCE(sum(aml.credit), 0.00) as credit,
                    COALESCE(sum(aml.amount_currency), 0.00) as amount_currency
                    from account_move_line aml
                    left join account_move am on am.id = aml.move_id %s"""%(where_cond)
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        if data:
            credit = data[0]['credit']
            debit = data[0]['debit']
            amount_currency = data[0]['amount_currency']
        else:
            credit = 0.00
            debit = 0.00
            amount_currency = 0.00
        return {'debit': debit, 'credit': credit,'amount_currency':amount_currency}
    
    def get_ledger_data(self, account_ids, from_date, to_date, target_move, partner_id, analytic_id):
        _logger.warning('getttttttttttttttttttttttttttttttttttttttttt ')
        result = []
        if partner_id:
            com_where_cond = """where aml.date >= '%s' and aml.date <= '%s' and aml.company_id=%s and aml.partner_id=%s"""%(from_date, to_date,
                                                                                                 self.env.user.company_id.id,partner_id.id)
        else:
            com_where_cond = """where aml.date >= '%s' and aml.date <= '%s' and aml.company_id=%s"""%(from_date, to_date,
                                                                                                 self.env.user.company_id.id)
        if target_move == 'posted':
            com_where_cond += " and am.state = 'posted'"
        if analytic_id:
            com_where_cond += """ and aml.analytic_account_id=%s"""%(analytic_id.id)
        for account in account_ids:
            opening_bal = self.get_opening_entry(account, from_date, target_move,partner_id)
            where_cond = com_where_cond
            where_cond += " and aml.account_id = %s"%(account.id)
            query = """Select
            aml.name as label,
            aml.ref as reference,
            aml.date as date,
            rp.name as partner,
            am.name as jv_name,
            aj.name as journal,
            aml.debit as debit,
            aml.credit as credit,
            curr.name as currency,
            aml.amount_currency as amount_currency,
            aaa.name as analytic_account
            from account_move_line aml
            left join account_move am on am.id=aml.move_id
            left join res_partner rp on rp.id = aml.partner_id
            left join account_journal aj on aj.id = am.journal_id
            left join res_currency curr on curr.id = aml.currency_id
            left join account_analytic_account aaa on aaa.id = aml.analytic_account_id
            
            %s
            order by aml.date
            """%(where_cond)
            self.env.cr.execute(query)
            data = self.env.cr.dictfetchall()
            res = {
                'account_name': "[%s]%s"%(account.code, account.name),
                'opening_balance': opening_bal,
                'data': data
                }
            result.append(res)
        return result
    
    @api.model
    def get_date_time_in_tz(self,date_time=''):
        
        if date_time:
            time_obj = datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT)
            tz_time = ''
            tz_name = self._context.get('tz', False) \
                or self.env.user.tz
            if not tz_name:
                raise UserError(_('Please configure your time zone in preferance'))
            if tz_name and time_obj:
                return time_obj.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(tz_name)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                return False
        else:
                return False
    
    def generate_xlsx_report(self, workbook, data, wizard):
        partner_bool = True
        account_ids = wizard.account_ids
        if not account_ids:
            account_ids = self.env['account.account'].search([])
        partner_ids = wizard.partner_ids
        if not partner_ids:
            partner_bool = False
#             partner_ids = self.env['res.partner'].search([])
        
            ##FORMATS##
        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 18})
        sub_heading_format = workbook.add_format({'align': 'center',
                                                  'valign': 'vcenter',
                                                  'bold': True, 'size': 14})
        bold = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        no_format = workbook.add_format({'num_format': '#,##0.000'})
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,##0.000'})
        ##FORMATS END##
        if partner_bool == True:
            count = 0
            mv_line = []
            for partner_id in partner_ids:
                
                            
                count += 1
                data = self.get_ledger_data(account_ids, wizard.date_from, wizard.date_to, wizard.target_move, partner_id, wizard.analytic_id)
                try:
                    worksheet = workbook.add_worksheet(partner_id.name[:31])
                except:
                    worksheet = workbook.add_worksheet("General Ledger - %s"%(count))
                    
                row = 6
                end_col = 0    
                worksheet.set_column('A:A', 15)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 15)
                worksheet.set_column('D:D', 15)
                worksheet.set_column('E:E', 15)
                worksheet.set_column('F:F', 15)
                worksheet.set_column('G:G', 15)
                if wizard.show_curr:
                    worksheet.set_column('H:H', 15)
                    worksheet.set_column('I:I', 15)
                worksheet.write(row, end_col, 'Date', bold)
                end_col += 1
                worksheet.write(row, end_col, 'Journal', bold)
                end_col += 1
                worksheet.write(row, end_col, 'Partner', bold)
                end_col += 1
                worksheet.write(row, end_col, 'Ref', bold)
                end_col += 1
                worksheet.write(row, end_col, 'Move', bold)
                end_col += 1
                worksheet.write(row, end_col, 'Analytic Account', bold)
                end_col += 1
                worksheet.write(row, end_col, 'Narration', bold)
                end_col += 1
                if wizard.show_curr:
                    worksheet.write(row, end_col, 'Amount Currency', bold)
                    amount_curr_col = end_col
                    
                    end_col += 1
                    worksheet.write(row, end_col, 'Currency', bold)
                    curr_col = end_col
                    end_col += 1
                worksheet.write(row, end_col, 'Debit', bold)
                debit_col = end_col
                debit_start = excel_style(row + 2, debit_col + 1)
                end_col += 1
                worksheet.write(row, end_col, 'Credit', bold)
                credit_col = end_col
                credit_start = excel_style(row + 2, credit_col + 1)
                end_col += 1
                worksheet.write(row, end_col, 'Balance', bold)
                balance_col = end_col
                row += 1
                
#                 worksheet.set_column('I:I', 25)
                ending_col = excel_style(1, 9)
                worksheet.merge_range('A1:%s'%(ending_col), self.env.user.company_id.name, heading_format)
                ending_col = excel_style(2, 9)
                worksheet.merge_range('A2:%s'%(ending_col), "General Ledger", sub_heading_format)
                worksheet.write(3, 0, "Date From", bold)
                start_date = wizard.date_from
                start_date = datetime.strptime(str(start_date), "%Y-%m-%d")
                worksheet.write_datetime(3, 1, start_date, date_format)
                worksheet.write(4, 0, "Date To", bold)
                end_date = wizard.date_to
                end_date = datetime.strptime(str(end_date), "%Y-%m-%d")
                worksheet.write_datetime(4, 1, end_date, date_format)
                
                
#                 heading_list = ['Date', 'Journal', 'Partner', 'Ref', 'Move', 'Analytic Account', 'Narration', 'Debit', 'Credit', 'Balance']
                
#                 for heading in heading_list:
#                     worksheet.write(row, col, heading, bold)
#                     col += 1
              
                for account_data in data:
                    starting_col = excel_style(row + 1, 1)
                    ending_col = excel_style(row + 1, 9)
                    worksheet.merge_range('%s:%s'%(starting_col, ending_col), account_data['account_name'], bold)
                    row += 1
                    
                    opening_data = account_data['opening_balance']
                    worksheet.write_datetime(row, 0, start_date, date_format)
                    starting_col = excel_style(row + 1, 2)
                    ending_col = excel_style(row + 1, 6)
                    worksheet.merge_range('%s:%s'%(starting_col, ending_col), "Opening Balance")
                    worksheet.write_number(row, debit_col, opening_data['debit'], no_format)
                    worksheet.write_number(row, credit_col, opening_data['credit'], no_format)
                    if wizard.show_curr:
                        worksheet.write(row, amount_curr_col,opening_data['amount_currency'],no_format)
                        worksheet.write(row, amount_curr_col+1, '')
                    balance = opening_data['debit'] - opening_data['credit']
                    debit_total = opening_data['debit']
                    credit_total = opening_data['credit']
                    worksheet.write_number(row,balance_col , balance, no_format)
                    row += 1
                    credit_sum_start_col = excel_style(row, credit_col+1)
                    debit_sum_start_col = excel_style(row , debit_col+1)
                    if wizard.show_curr:
                        amount_curr_start = excel_style(row , amount_curr_col + 1)
                    for line in account_data['data']:
                        
                        date = line['date']
                        date = datetime.strptime(str(date), '%Y-%m-%d')
                        worksheet.write_datetime(row, 0, date, date_format)
                        worksheet.write(row, 1, line['journal'])
                        worksheet.write(row, 2, line['partner'])
                        worksheet.write(row, 3, line['reference'])
                        worksheet.write(row, 4, line['jv_name'])
                        worksheet.write(row, 5, line['analytic_account'])
                        worksheet.write(row, 6, line['label'])
                        col = 7
                        
                        if wizard.show_curr:
                            worksheet.write_number(row, col, line['amount_currency'], no_format)
                            col += 1
                            worksheet.write(row, col, line['currency'] or '')
                            col += 1
                        worksheet.write_number(row, debit_col, line['debit'], no_format)
                        worksheet.write_number(row, credit_col, line['credit'], no_format)
                        balance = balance + (line['debit'] - line['credit'])
                        debit_total = debit_total + line['debit']
                        credit_total = credit_total + line['credit']
                        worksheet.write_number(row, balance_col, (line['debit'] - line['credit']), no_format)
                        row += 1
                    credit_sum_ending_col = excel_style(row, credit_col+1)
                    debit_sum_ending_col = excel_style(row, debit_col+1)
                    credit_dest_cell = excel_style(row + 1, credit_col+1)
                    debit_dest_cell = excel_style(row + 1, debit_col+1)
                    worksheet.write_number(row, balance_col-2, debit_total, normal_num_bold)
                    worksheet.write_number(row, balance_col-1, credit_total, normal_num_bold)
#                     worksheet.write_formula(debit_dest_cell, 'SUM(%s:%s)'%(debit_sum_start_col, debit_sum_ending_col), normal_num_bold)
#                     worksheet.write_formula(credit_dest_cell, 'SUM(%s:%s)'%(credit_sum_start_col, credit_sum_ending_col), normal_num_bold)
                    worksheet.write_number(row, balance_col, balance, normal_num_bold)
                    
                    
                    
                    
#                     debit_stop = excel_style(row, debit_col + 1)
#                     credit_stop = excel_style(row, credit_col + 1)
#                     debit_dest_cell = excel_style(row + 1, debit_col + 1)
#                     credit_dest_cell = excel_style(row + 1, credit_col + 1)
#                     worksheet.write_number(row, credit_col + 1, balance, normal_num_bold)
#                     worksheet.write_formula(debit_dest_cell, 'SUM(%s:%s)'%(debit_start, debit_stop), normal_num_bold)
#                     worksheet.write_formula(credit_dest_cell, 'SUM(%s:%s)'%(credit_start, credit_stop), normal_num_bold)
                    if wizard.show_curr:
                        amount_curr_stop = excel_style(row , amount_curr_col + 1 )
                        amount_cr_dest_cell = excel_style(row + 1, amount_curr_col + 1)
                        cr_dest_cell = excel_style(row + 1, amount_curr_col + 2)
                        worksheet.write_formula(amount_cr_dest_cell, 'SUM(%s:%s)'%(amount_curr_start, amount_curr_stop), normal_num_bold)
                        worksheet.write(row + 2, amount_curr_col + 2, '')
                        
                    row += 2
                selected_partner_list = []
                partner_obj_list = []
                if wizard.combine_aging_bool == True:
                    for account in account_ids:
                        acc_type = account.user_type_id.name
                        if acc_type == 'Receivable':
                            account_type = ['receivable']
                        elif acc_type == 'Payable':
                            account_type = ['payable']
                        else:
                            account_type = ['payable','receivable']
                        date = wizard.date_to
                        target_move = wizard.target_move
                        period_length = wizard.period_length
                        partner_movelines = self.env['report.account.report_agedpartnerbalance']._get_partner_move_lines(account_type,date,target_move,period_length)
                        moveline = partner_movelines[0]
                        if partner_ids:
                            partner_list = partner_ids.ids
                            for line in moveline:
                                if line['partner_id'] in partner_list:
                                    selected_partner_list.append(line)
                                    partner_obj = self.env['res.partner'].browse(line['partner_id'])
                                    partner_obj_list.append(partner_obj)
                        if selected_partner_list:
                            for line in selected_partner_list:
                                if line['partner_id'] == partner_id.id:
                                    mv_line = line
            
                    
                    if mv_line:
                            worksheet.set_column('A:A', 15)
                            worksheet.set_column('B:B', 15)
                            worksheet.set_column('C:C', 15)
                            worksheet.set_column('D:D', 15)
                            worksheet.set_column('E:E', 15)
                            worksheet.set_column('F:F', 15)
                            worksheet.set_column('G:G', 15)
                            end_col = 0
                            worksheet.write(row, end_col, 'Not Due', bold)
                            end_col += 1
                            worksheet.write(row, end_col, '0-30', bold)
                            end_col += 1
                            worksheet.write(row, end_col, '31-60', bold)
                            end_col += 1
                            worksheet.write(row, end_col, '61-90', bold)
                            end_col += 1
                            worksheet.write(row, end_col, '91-120', bold)
                            end_col += 1
                            worksheet.write(row, end_col, '+120', bold)
                            end_col += 1
                            worksheet.write(row, end_col, 'Total', bold)
                            row += 1
                            
                            col = 0
                            worksheet.write(row, col, mv_line['direction'] or '0.00',no_format)
                            col += 1
                            worksheet.write(row, col, mv_line['4'],no_format )
                            col += 1
                            worksheet.write(row, col, mv_line['3'],no_format)
                            col += 1
                            worksheet.write(row, col, mv_line['2'],no_format)
                            col += 1
                            worksheet.write(row, col, mv_line['1'] ,no_format)
                            col += 1
                            worksheet.write(row, col, mv_line['0'],no_format)
                            col += 1
                            worksheet.write(row, col, mv_line['total'] ,no_format)
                            row += 1
            
        else:
            partner_id = []
            data = self.get_ledger_data(account_ids, wizard.date_from, wizard.date_to, wizard.target_move,partner_id, wizard.analytic_id)
            worksheet = workbook.add_worksheet("General Ledger")
            row = 6
            end_col = 0    
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:F', 15)
            worksheet.set_column('G:G', 15)
            if wizard.show_curr:
                worksheet.set_column('H:H', 15)
                worksheet.set_column('I:I', 15)
            ending_col = excel_style(1, 10)
            worksheet.merge_range('A1:%s'%(ending_col), self.env.user.company_id.name, heading_format)
            ending_col = excel_style(2, 10)
            worksheet.merge_range('A2:%s'%(ending_col), "General Ledger", sub_heading_format)
            worksheet.write(3, 0, "Date From", bold)
            start_date = wizard.date_from
            start_date = datetime.strptime(str(start_date), "%Y-%m-%d")
            worksheet.write_datetime(3, 1, start_date, date_format)
            worksheet.write(4, 0, "Date To", bold)
            end_date = wizard.date_to
            end_date = datetime.strptime(str(end_date), "%Y-%m-%d")
            worksheet.write_datetime(4, 1, end_date, date_format)
            worksheet.write(5, 0, "Printed On", bold)
            printed_on = self.get_date_time_in_tz(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            printed_on = datetime.strptime(str(printed_on),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
            worksheet.write(5, 1, printed_on)
            worksheet.write(row, end_col, 'Date', bold)
            end_col += 1
            worksheet.write(row, end_col, 'Journal', bold)
            end_col += 1
            worksheet.write(row, end_col, 'Partner', bold)
            end_col += 1
            worksheet.write(row, end_col, 'Ref', bold)
            end_col += 1
            worksheet.write(row, end_col, 'Move', bold)
            end_col += 1
            worksheet.write(row, end_col, 'Analytic Account', bold)
            end_col += 1
            worksheet.write(row, end_col, 'Narration', bold)
            end_col += 1
            if wizard.show_curr:
                worksheet.write(row, end_col, 'Amount Currency', bold)
                amount_curr_col = end_col
                
                end_col += 1
                worksheet.write(row, end_col, 'Currency', bold)
                curr_col = end_col
                end_col += 1
            worksheet.write(row, end_col, 'Debit', bold)
            debit_col = end_col
            debit_start = excel_style(row + 2, debit_col + 1)
            end_col += 1
            worksheet.write(row, end_col, 'Credit', bold)
            credit_col = end_col
            credit_start = excel_style(row + 2, credit_col + 1)
            end_col += 1
            worksheet.write(row, end_col, 'Balance', bold)
            balance_col = end_col
           
#             heading_list = ['Date', 'Journal', 'Partner', 'Ref', 'Move', 'Analytic Account', 'Narration', 'Debit', 'Credit', 'Balance']
            
            row += 1
            for account_data in data:
                starting_col = excel_style(row + 1, 1)
                ending_col = excel_style(row + 1, 9)
                worksheet.merge_range('%s:%s'%(starting_col, ending_col), account_data['account_name'], bold)
                row += 1
                opening_data = account_data['opening_balance']
                worksheet.write_datetime(row, 0, start_date, date_format)
                
                starting_col = excel_style(row + 1, 2)
                ending_col = excel_style(row + 1, 6)
                worksheet.merge_range('%s:%s'%(starting_col, ending_col), "Opening Balance")
                worksheet.write_number(row, debit_col, opening_data['debit'], no_format)
                worksheet.write_number(row, credit_col, opening_data['credit'], no_format)
                if wizard.show_curr:
                    worksheet.write(row, amount_curr_col,opening_data['amount_currency'],no_format)
                    worksheet.write(row, amount_curr_col+1, '')
                debit_total = opening_data['debit']
                credit_total = opening_data['credit']
                balance = opening_data['debit'] - opening_data['credit']
                worksheet.write_number(row, balance_col, balance, no_format)
                row += 1
                credit_sum_start_col = excel_style(row, credit_col+1)
                debit_sum_start_col = excel_style(row , debit_col+1)
                if wizard.show_curr:
                    amount_curr_start = excel_style(row , amount_curr_col + 1)
                
                for line in account_data['data']:
                    date = line['date']
                    date = datetime.strptime(str(date), '%Y-%m-%d')
                    worksheet.write_datetime(row, 0, date, date_format)
                    worksheet.write(row, 1, line['journal'])
                    worksheet.write(row, 2, line['partner'])
                    worksheet.write(row, 3, line['reference'])
                    worksheet.write(row, 4, line['jv_name'])
                    worksheet.write(row, 5, line['analytic_account'])
                    worksheet.write(row, 6, line['label'])
                    col = 7
                    if wizard.show_curr:
                        worksheet.write_number(row, col, line['amount_currency'], no_format)
                        col += 1
                        worksheet.write(row, col, line['currency'] or '')
                        col += 1
                    worksheet.write_number(row, debit_col, line['debit'], no_format)
                    worksheet.write_number(row, credit_col, line['credit'], no_format)
                    debit_total = debit_total + line['debit']
                    credit_total = credit_total + line['credit']
                    balance = balance + (line['debit'] - line['credit'])
                    worksheet.write_number(row, balance_col, (line['debit'] - line['credit']), no_format)
                    
                    row += 1
                credit_sum_ending_col = excel_style(row, credit_col+1)
                debit_sum_ending_col = excel_style(row, debit_col+1)
                credit_dest_cell = excel_style(row + 1, credit_col+1)
                debit_dest_cell = excel_style(row + 1, debit_col+1)
                worksheet.write_number(row,balance_col-2, debit_total,normal_num_bold)
                worksheet.write_number(row,balance_col-1, credit_total,normal_num_bold)
#                 worksheet.write_formula(debit_dest_cell, 'SUM(%s:%s)'%(debit_sum_start_col, debit_sum_ending_col), normal_num_bold)
#                 worksheet.write_formula(credit_dest_cell, 'SUM(%s:%s)'%(credit_sum_start_col, credit_sum_ending_col), normal_num_bold)
                worksheet.write_number(row, balance_col, balance, normal_num_bold)
                if wizard.show_curr:
                    amount_curr_stop = excel_style(row , amount_curr_col + 1 )
                    amount_cr_dest_cell = excel_style(row + 1, amount_curr_col + 1)
                    cr_dest_cell = excel_style(row + 1, amount_curr_col + 2)
                    worksheet.write_formula(amount_cr_dest_cell, 'SUM(%s:%s)'%(amount_curr_start, amount_curr_stop), normal_num_bold)
                    worksheet.write(row + 2, amount_curr_col + 2, '')
                row += 2
                
#         for sale in sale_orders:
#             float_cols = []
#             sale_order_data, other_cost_map, header_map = self.process_sale_orders(sale_orders)
#             report_name = sale.name
#             report_name = report_name.replace("/", '')
#             # One sheet by partner
#             worksheet = workbook.add_worksheet(report_name[:31])
#             
#             bold = workbook.add_format({'bold': True})
#             bold.set_bg_color('#cbd1db')
#             normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,##0.00'})
#             normal_char_bold = workbook.add_format({'bold': True, 'num_format': '#,##0.00'})
#             date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
#             no_format = workbook.add_format({'num_format': '#,##0.00'})
#             col = 0
#             buffer_row = 4
#             for header in col_heading:
#                 row = buffer_row
#                 if header == 'other_costs':
#                     for other_cost in other_cost_map:
#                         float_cols.append(col)
#                         row = 4
#                         worksheet.write(row, col, other_cost_map[other_cost], bold)
#                         for sale_data in sale_order_data:
#                             row += 1
#                             worksheet.write_number(row, col, sale_data[other_cost], no_format)
#                         col += 1
#                 else:
#                     worksheet.write(row, col, header_map[header], bold)
#                     for sale_data in sale_order_data:
#                         row += 1
#                         if header == 'date':
#                             date = sale_data[header]
#                             date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
# #                             date = date.strftime("%Y-%m-%d")
#                             worksheet.write_datetime(row, col, date, date_format)
#                         elif header in ['exch_rate', 'qty', 'fc_cost',
#                                         'total_fc_cost', 'total_bc_cost',
#                                         'factor', 'other_costs', 'l_cost',
#                                         'margin_per', 'margin_amt',
#                                         'unit_sale_price', 'subtotal']:
#                             if header not in ['exch_rate', 'qty', 'margin_per', 'unit_sale_price']:
#                                 float_cols.append(col)
#                             worksheet.write_number(row, col, sale_data[header], no_format)
#                         else:
#                             worksheet.write(row, col, sale_data[header])
#                     col += 1
#             float_cols = list(set(float_cols))
#             total_rec = len(sale_order_data)
#             for float_col in float_cols:
#                 dest_cell = excel_style(total_rec + (buffer_row + 2), float_col + 1)
#                 till_cell = excel_style(total_rec + (buffer_row + 1), float_col + 1)
#                 from_cell = excel_style(5, float_col + 1)
#                 worksheet.write_formula(dest_cell, 'SUM(%s:%s)'%(from_cell, till_cell), normal_num_bold)
#             heading_format = workbook.add_format({'align': 'center',
#                                                   'valign': 'vcenter',
#                                                   'bold': True, 'size': 18})
#             ending_col = excel_style(1, col)
#             worksheet.merge_range('A1:%s'%(ending_col), sale.company_id.name, heading_format)
#             date_format.set_bold()
#             if sale.date_order:
#                 date = sale.date_order
#                 date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
#                 worksheet.merge_range('A2:B2', "Date :", normal_char_bold)
#                 worksheet.merge_range('C2:E2', date, date_format)
#             worksheet.merge_range('A3:B3', "Customer :", normal_char_bold)
#             worksheet.merge_range('C3:E3', sale.partner_id.name, normal_char_bold)
#             worksheet.merge_range('A4:B4', "Our Ref :", normal_char_bold)
#             worksheet.merge_range('C4:E4', sale.name, normal_char_bold)


# GeneralLedgerXlsx('report.general.ledger.xlsx',
#               'account.report.general.ledger')
