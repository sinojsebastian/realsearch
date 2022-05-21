from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
import time

from datetime import datetime, timedelta, date

from calendar import monthrange

from dateutil.relativedelta import relativedelta

from dateutil.rrule import rrule, MONTHLY
from datetime import datetime,date
from odoo.tools.misc import formatLang, format_date, get_lang


from odoo.tools import DEFAULT_SERVER_DATE_FORMAT



import logging
_logger = logging.getLogger(__name__)


class OwnerRentalQweb(models.AbstractModel):

    _name = 'report.zb_bf_custom.report_owner_rentalstatement'
    _description='Owner Rental Statement'

    
   
    def _decimal_correction(self,value):
        
        three_dec = format(value, ".3f")
        last_digit = str(three_dec)[-1]
        scnd_last_digit = str(three_dec)[-2]
        third_last_digit = str(three_dec)[-3]
        if int(last_digit) == int(scnd_last_digit) == int(third_last_digit) == 0:
            amount = int(value)
        else:
            amount = three_dec
        
        return amount
    
    
    def journal_func(self,from_date,to_date,docs):
        
        from_domain = from_date.strftime('%Y-%m-%d')
        to_domain = to_date.strftime('%Y-%m-%d')
        
        
        sql = "select ml.journal_id,sum(a.allocation),a.id from account_payment_line as a JOIN account_move_line as ml on a.move_line_id = ml.id  where a.advance_id in (select id from account_payment where payment_advise=True and partner_id=%s) and a.original_date >= '%s' and a.original_date <= '%s' GROUP BY ml.journal_id,a.id"%(docs.owner_id.id,from_domain,to_domain)
        self._cr.execute(sql)
        lines=self._cr.fetchall()
        return lines
        
    
    def get_month_data(self,month_list,jv_vals):
        data_list = []
        for k,v in jv_vals.items():
            month_data_list =[]
            month_data_list.append(k)
            for month in month_list:
                month_data_list.append(v[0][month])
            data_list.append(month_data_list)
        return data_list
    
    
    def get_month_expense_data(self,month_list,exp_vals):
        data_list = []
        for k,v in exp_vals.items():
            month_data_list =[]
            month_data_list.append(k)
            for month in month_list:
                month_data_list.append(v[0][month])
            data_list.append(month_data_list)
        return data_list
    
    def get_revised_month_dict(self,month_list,dict_vals):
        for month in month_list:
            if not month in dict_vals:
                dict_vals[month] = 0
        return dict_vals
    
    def get_total_funds(self,funds_total,dict_vals):
        for key,value in dict_vals.items():
            if key in funds_total:
                funds_total[key] += dict_vals[key]
            else:
                funds_total[key] = dict_vals[key]
        return funds_total
    
    # def get_payment_period(self,funds_total,expense_total,month_list):
    #     period_list = []
    #     for month in month_list:
    #         if funds_total and expense_total :
    #             if funds_total[month]-expense_total[month] > 0:
    #                 month_format = datetime.strptime(str(month),'%b-%y').strftime('%d-%b-%Y')
    #                 period_list.append(month_format)
    #     if period_list:
    #         last_data = datetime.strptime(str(period_list[-1]),'%d-%b-%Y')
    #         last_date = last_data.replace(day = monthrange(last_data.year, last_data.month)[1])
    #         period_list[-1] = last_date.strftime('%d-%b-%Y')
    #     return period_list
    

    @api.model
    def _get_report_values(self, docids,data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        result =[]
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        user_id = self.env['res.users'].browse(self.env.uid)
        company_id = user_id.company_id
        company = str(user_id.company_id.name)
        
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        
        
        if data['form']:
        
            from_date = data['form'][0].get('from_date')
            to_date = data['form'][0].get('to_date')
            rent_start_date = data['form'][0].get('date_start')
            rent_start_date_format = datetime.strptime(str(rent_start_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            rent_end_date = data['form'][0].get('date_end')
            rent_end_date_format = datetime.strptime(str(rent_end_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            
            service_start_date_format = ''
            service_end_date_format = ''
            service_start_date = data['form'][0].get('service_date_start')
            if service_start_date:
                service_start_date_format = datetime.strptime(str(service_start_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            service_end_date = data['form'][0].get('service_date_end')
            if service_end_date:
                service_end_date_format = datetime.strptime(str(service_end_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            
            date_from = datetime.strptime(from_date,'%Y-%m-%d').date().replace(day=1)
            date_from_format = datetime.strptime(from_date,'%Y-%m-%d').date()
            date_to_format = datetime.strptime(to_date,'%Y-%m-%d').date()
            
            previous_date = (date_from - relativedelta(months=8))
            
            payment_period_list = []
            if date_from_format and date_to_format:
                from_date_lang = date_from_format.strftime(get_lang(self.env).date_format)
                to_date_lang = date_to_format.strftime(get_lang(self.env).date_format)
                payment_period_list.append(from_date_lang)
                payment_period_list.append(to_date_lang)
            
            month_list = []
            for month_date in rrule(MONTHLY, dtstart=previous_date, until=date_from):
                
                first_month_date = datetime.strptime(str(month_date.date()), DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%b-%Y')
                month_list.append(first_month_date)
                
            
            params = self.env['ir.config_parameter'].sudo()  
            ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id')
            if not ewa_product_id:
                raise Warning(_("""Please configure EWA Service Product in the Accounting Settings"""))
        
            internet_product_id = params.get_param('zb_bf_custom.internet_product_id')
            if not internet_product_id:
                raise Warning(_("""Please configure Internet Service Product in the Accounting Settings"""))
        
            ewa_obj = self.env['product.product'].browse(int(ewa_product_id[0]))
           
            internet_obj = self.env['product.product'].browse(int(internet_product_id[0]))
            
            ewa_amount = 0.000
            int_amount = 0.000
            for line in docs.lease_services_ids:
                if line.product_id.id == ewa_obj.id:
                    ewa_amount = line.owner_share
                elif line.product_id.id == internet_obj.id:
                    int_amount = line.owner_share
            

            
            month_jv_dict = {}
            expense_dict ={}
            for month_date in rrule(MONTHLY, dtstart=previous_date, until=date_from):
                first_month_date = datetime.strptime(str(month_date.date()), DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%b-%Y')
                month_last_date = month_date.replace(day = monthrange(month_date.year, month_date.month)[1])
                journal_list = self.journal_func(month_date.date(), month_last_date.date(),docs)
                
               
                for jv in journal_list:
                    jv_id  = self.env['account.journal'].browse(jv[0])
                    payment_line_id  = self.env['account.payment.line'].browse(jv[2])
                    
                    if payment_line_id.advance_id.payment_type == 'outbound':
                        amount = -jv[1] if (payment_line_id.debit - payment_line_id.credit)>0 else jv[1]
                        if  payment_line_id.credit:
                            if not month_jv_dict.get(jv_id.name):
                                month_jv_dict[jv_id.name] = [{
                                            first_month_date :amount or 0.000,
                                            'journal':jv_id.name
                                    }]
                            else:
                                month_jv_dict[jv_id.name].append({
                                                            first_month_date : amount or 0.000,
                                                            'journal':jv_id.name
                                                        })
                        else:
                            if not expense_dict.get(jv_id.name):
                                expense_dict[jv_id.name] = [{
                                            first_month_date :amount or 0.000,
                                            'journal':jv_id.name
                                    }]
                            else:
                                expense_dict[jv_id.name].append({
                                                            first_month_date : amount or 0.000,
                                                            'journal':jv_id.name
                                                        })
                
                        
                        
                    
                    
                
                        
            
            
            
            for k,v in month_jv_dict.items():
                data_dict = v[0]
                for month in month_list:
                    if not data_dict.get(month):
                        month_jv_dict[k][0].update({
                            month:0.000
                            })
            
            for k,v in expense_dict.items():
                data_dict = v[0]
                for month in month_list:
                    if not data_dict.get(month):
                        expense_dict[k][0].update({
                            month:0.000
                            })
                                
            # new report with new sample
            
            params = self.env['ir.config_parameter'].sudo()           
            rent_transfer_journal_id = params.get_param('zb_bf_custom.rent_transfer_journal_id') or False
            ewa_journal_id = params.get_param('zb_bf_custom.ewa_journal_id') or False
            rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
            deposit_journal_id = params.get_param('zb_bf_custom.deposit_journal_id') or False
            if deposit_journal_id:
                deposit_journal = self.env['account.journal'].browse(int(deposit_journal_id))
            dict_expense = {}
            pa_ids = self.env['account.payment'].search([('payment_advise','=',True),('state','=','posted'),('lease_id','=',docs.id)])
            payment_mode = []
            
            # fetching rent collected amount
            # rent_collection = self.env['account.move.line'].search([('lease_agreement_id','=',docs.id),('module_id','=',docs.subproperty.id),('move_id.state','=','posted'),('move_id.type','=','out_invoice'),('move_id.journal_id','=',int(rent_transfer_journal_id))])
            rent_invoices = self.env['account.move'].search([('lease_id','=',docs.id),('module_id','=',docs.subproperty.id),('state','=','posted'),('type','=','out_invoice'),('journal_id','=',int(rent_invoice_journal_id))])
            print('==================rent_invoices=================',rent_invoices)
            rent_inv_list = [rent.id for rent in rent_invoices]
            journal_items = self.env['account.move.line'].search([('move_id.id','in',rent_inv_list)])
            jornal_item_list = [item.id for item in journal_items]
            partial_entries = self.env['account.partial.reconcile'].search([('debit_move_id.id','in',jornal_item_list)])
            print('==============partial_entries=================',partial_entries)
            # rent_collection = self.env['account.partial.reconcile'].search([('rent_transfer_id','=',docs.id)])
            # ('module_id','=',docs.subproperty.id),('state','=','posted'),('type','=','out_invoice'),('journal_id','=',int(rent_invoice_journal_id))])
            rent_collected = {}
            prior_rent_dict = {}
            advance_rent_dict = {}
            if partial_entries:
                for entry in partial_entries:
                    if entry.rent_transfer_id and entry.rent_transfer_id.date:
                        if entry.rent_transfer_id.date >= date_from_format and entry.rent_transfer_id.date <= date_to_format:
                            month = datetime.strptime(str(entry.rent_transfer_id.date), DEFAULT_SERVER_DATE_FORMAT).strftime('%b-%y')
                            invoice_month = datetime.strptime(str(entry.debit_move_id.move_id.invoice_date), DEFAULT_SERVER_DATE_FORMAT).strftime('%m')
                            payment_month = datetime.strptime(str(entry.rent_transfer_id.date), DEFAULT_SERVER_DATE_FORMAT).strftime('%m')
                            date_key = month
                            if payment_month == invoice_month:
                                if date_key in rent_collected:
                                    rent_collected[date_key] += entry.amount
                                    # rent_collected[date_key] += move.credit
                                else:
                                    rent_collected[date_key] = entry.amount
                                
                            elif payment_month < invoice_month:
                                if date_key in advance_rent_dict:
                                    advance_rent_dict[date_key] += entry.amount
                                    # rent_collected[date_key] += move.credit
                                else:
                                    advance_rent_dict[date_key] = entry.amount
                                
                            else:
                                if date_key in prior_rent_dict:
                                    prior_rent_dict[date_key] += entry.amount
                                    # rent_collected[date_key] += move.credit
                                else:
                                    prior_rent_dict[date_key] = entry.amount
                                
                
                # for move in rent_collection:
                #     if move.invoice_date:
                #         if move.invoice_date >= date_from_format and move.invoice_date <= date_to_format:
                #             month = datetime.strptime(str(move.invoice_date), DEFAULT_SERVER_DATE_FORMAT).strftime('%b-%y')
                #             date_key = month
                #             if date_key in rent_collected:
                #                 rent_collected[date_key] += move.amount_total - move.amount_residual
                #                 # rent_collected[date_key] += move.credit
                #             else:
                #                 rent_collected[date_key] = move.amount_total - move.amount_residual
                                # rent_collected[date_key] = move.credit
            
            
            
            deposit_dict ={}
            deposit_paid = False
            rent_collected_payments = self.env['account.payment'].search([('module_id','=',docs.subproperty.id),('payment_date','>=',date_from_format),('payment_date','<=',date_to_format),('state','=','posted')])
            
            # fetching prior rent,advance rent and deposit rent collected
            if rent_collected_payments:
                for payment in rent_collected_payments:
                    month = datetime.strptime(str(payment.payment_date), DEFAULT_SERVER_DATE_FORMAT).strftime('%b-%y')
                    date_key = month
                    if payment.reconciled_invoice_ids:
                        for inv in payment.reconciled_invoice_ids:
                            for each in inv._get_reconciled_info_JSON_values():
                                if each['account_payment_id'] == payment.id:
                                    if payment.payment_mode:
                                        payment_mode.append(dict(payment._fields['payment_mode'].selection).get(payment.payment_mode))
                                    # if inv.journal_id.id == int(rent_invoice_journal_id) and inv.invoice_date < docs.agreement_start_date:
                                    #     if date_key in prior_rent_dict:
                                    #         prior_rent_dict[date_key] += each['amount']
                                    #     else:
                                    #         prior_rent_dict[date_key] = each['amount']
                                    if inv.journal_id.id == int(deposit_journal_id):
                                        deposit_paid = True
                                        if date_key in deposit_dict:
                                            deposit_dict[date_key] += each['amount']
                                        else:
                                            deposit_dict[date_key] = each['amount']
                                    # elif inv.journal_id.id == int(rent_invoice_journal_id) and inv.invoice_date >= docs.agreement_start_date and inv.invoice_date <= docs.agreement_end_date:
                                    #     if inv.amount_untaxed > docs.monthly_rent:
                                    #         if date_key in advance_rent_dict:
                                    #             advance_rent_dict[date_key] += each['amount']
                                    #         else:
                                    #             advance_rent_dict[date_key] = each['amount']
                                        
            # fetching ewa excess payments
            excess_ewa_collected = {}
            excess_ewa_payments = self.env['account.payment'].search([('partner_id','=',docs.tenant_id.id),('lease_id','=',docs.id),('payment_date','>=',date_from_format),('payment_date','<=',date_to_format)])
            for payment in excess_ewa_payments:
                if payment.reconciled_invoice_ids:
                    for inv in payment.reconciled_invoice_ids:
                        if inv.journal_id.id == int(ewa_journal_id):
                            for each in inv._get_reconciled_info_JSON_values():
                                if each['account_payment_id'] == payment.id:
                                    if payment.payment_mode:
                                        payment_mode.append(dict(payment._fields['payment_mode'].selection).get(payment.payment_mode))
                                    month = datetime.strptime(str(payment.payment_date), DEFAULT_SERVER_DATE_FORMAT).strftime('%b-%y')
                                    date_key = month
                                    if date_key in excess_ewa_collected:
                                        excess_ewa_collected[date_key] += each['amount']
                                    else:
                                        excess_ewa_collected[date_key] = each['amount']
            
            if pa_ids:
                for pa in pa_ids:
                    for payment in pa.payment_line_ids:
                        print('===========================payment',payment.advance_id)
                        if payment.advance_id and payment.advance_id.payment_date:
                            if payment.advance_id.payment_date >= date_from_format and payment.advance_id.payment_date <= date_to_format:
                                if pa.payment_mode:
                                    payment_mode.append(dict(pa._fields['payment_mode'].selection).get(pa.payment_mode))
                                if payment.debit > 0 and payment.allocation > 0:
                                    month = datetime.strptime(str(payment.advance_id.payment_date), DEFAULT_SERVER_DATE_FORMAT).strftime('%b-%y')
                                    date_key = month
                                    journal_key = payment.inv_id.journal_id.name
                                    if journal_key in dict_expense:
                                        if date_key in dict_expense[journal_key]:
                                            print('=========ifff11111================')
                                            dict_expense[journal_key][date_key] += payment.allocation
                                        else:
                                            print('=========else11111================')
                                            dict_expense[journal_key][date_key] = payment.allocation
                                        
                                    else:
                                        print('=========else2222222222================')
                                        dict_expense[journal_key] = {date_key:payment.allocation}
                    for adv_exp in pa.advance_expense_ids:
                        month = datetime.strptime(str(pa.payment_date), DEFAULT_SERVER_DATE_FORMAT).strftime('%b-%y')
                        if adv_exp.name in dict_expense:
                            if month in dict_expense[adv_exp.name]:
                                dict_expense[adv_exp.name][month] += adv_exp.amount
                            else:
                                dict_expense[adv_exp.name][month] = adv_exp.amount
                        else:
                            dict_expense[adv_exp.name] = {month:adv_exp.amount}

            print('================dict_expense================',dict_expense)
            if deposit_paid:
                dict_expense.update({deposit_journal.name:deposit_dict})
                                    
            dates = []
            while date_from_format <= date_to_format:
                month = datetime.strptime(str(date_from_format), DEFAULT_SERVER_DATE_FORMAT).strftime('%b-%y')
                dates.append(month)
                date_from_format = date_from_format + relativedelta(months=1)
                
            funds_total = {}
            rent_collected = self.get_revised_month_dict(dates,rent_collected)
            print('=============rent_collected+++==============',rent_collected)
            excess_ewa_collected = self.get_revised_month_dict(dates,excess_ewa_collected)
            prior_rent_dict = self.get_revised_month_dict(dates,prior_rent_dict)
            advance_rent_dict = self.get_revised_month_dict(dates,advance_rent_dict)
            print('=============advance_rent_dict+++==============',advance_rent_dict)
            if deposit_dict:
                deposit_dict = self.get_revised_month_dict(dates,deposit_dict)
                deposit_dict_total = self.get_total_funds(funds_total, deposit_dict)
            
            for key,value in dict_expense.items():
                for month in dates:
                    if not month in value:
                        value[month] = 0
           
            expense_total = {}
            for key,value in dict_expense.items():
                for vals in value:
                    if vals in expense_total:
                        expense_total[vals] += value[vals]
                    else:
                        expense_total[vals] = value[vals]
                        
            rent_collected_total_dict = self.get_total_funds(funds_total, rent_collected)
            excess_ewa_total = self.get_total_funds(funds_total, excess_ewa_collected)
            prior_rent_total = self.get_total_funds(funds_total, prior_rent_dict)
            advance_rent_total = self.get_total_funds(funds_total, advance_rent_dict)
            
            # payment_period_list = self.get_payment_period(funds_total, expense_total, dates)
            
            docargs = {
                       'doc_ids':self._ids,
                       'doc_model': model,
                       'docs': docs,
                       'company_id':company_id,
                       'data': data['form'],
                       'ewa':self._decimal_correction(ewa_amount),
                       'internet':self._decimal_correction(int_amount),
                       'months':month_list,
                       'jv_vals':month_jv_dict,
                       'expense_vals':expense_dict,
                       'data_vals':self.get_month_data(month_list,month_jv_dict),
                       'dict_expense':dict_expense,
                       'rent_collected':rent_collected,
                       'excess_ewa_collected':excess_ewa_collected,
                       'prior_rent_dict':prior_rent_dict,
                       'advance_rent_dict':advance_rent_dict,
                       'deposit_dict':deposit_dict,
                       'expense_total':expense_total,
                       'funds_total':funds_total,
                       'payment_period':payment_period_list,
                       'rent_start_date':rent_start_date_format,
                       'rent_end_date':rent_end_date_format,
                       'service_start_date':service_start_date_format,
                       'service_end_date':service_end_date_format,
                       'dates':dates,
                       'payment_mode':set(payment_mode),
                       'expense_data_vals':self.get_month_expense_data(month_list,expense_dict),
                       }
            return docargs