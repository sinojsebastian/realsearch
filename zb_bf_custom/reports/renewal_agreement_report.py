from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
from datetime import date,datetime,timedelta 
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import time

import logging
_logger = logging.getLogger(__name__)


class RenewalAgreementReportQWeb(models.AbstractModel):

    _name = 'report.zb_bf_custom.renewal_agreement'
    _description='Model For Renewal Agreement'

    
    def get_duration(self,lease_id):
        
        from_date = lease_id.agreement_start_date
        agreement_to_date = lease_id.agreement_end_date
        day = from_date.day
        month = 0
        year = 0
        while from_date <= agreement_to_date:
            to_date = from_date + relativedelta(months=1)
            if day <= monthrange(to_date.year,to_date.month)[1]:
                from_date = to_date.replace(day = day)
            else:
                last_day = to_date.replace(day = monthrange(to_date.year,to_date.month)[1])
                from_date = to_date.replace(day = last_day.day)
            month+=1
        if month >=12:
            year = int(month/12)
            month = month-(year*12)
        if year and month:
            fils,bd = math.modf(year)
            year_words = num2words(int(bd)).capitalize()
            fils,bd = math.modf(month)
            month_words = num2words(int(bd)).capitalize()
            duration = '%s(%s) year and %s(%s) months'%(year_words,year,month_words,month)
        elif year:
            fils,bd = math.modf(year)
            year_words = num2words(int(bd)).capitalize()
            duration = '%s(%s) year'%(year_words,year)
        elif month:
            fils,bd = math.modf(month)
            month_words = num2words(int(bd)).capitalize()
            duration = '%s(%s) months'%(month_words,month)
            
            
        # days = to_date - from_date
        # print('=================',days.days+1)
        # if days.days+1 < 365:
        #
        # duration = (to_date.year-from_date.year)*12+(to_date.month-from_date.month)
        return duration
    
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
    
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        lease_id=self.env['zbbm.module.lease.rent.agreement'].browse(docids)
#                 payments = self.env['account.payment'].search([('payment_advise','=',True),('invoice_ids','=',invoices[0].id)])
#                 word = ''
#                 sum=0
#                 for invoice in invoices:
#                     sum=sum+invoice.amount_total
        
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
        ewa_arabic = ''
        int_arabic = ''
        for line in lease_id.lease_services_ids:
            if line.product_id.id == ewa_obj.id:
                ewa_amount = line.owner_share
                ewa_arabic = line.owner_share_arabic
            elif line.product_id.id == internet_obj.id:
                int_amount = line.owner_share
                int_arabic = line.owner_share_arabic
#         pro_rent = pro_rated_rent*pro_rent_days
        fils,bd = math.modf(ewa_amount)
        fils = (float_round(fils,lease_id.currency_id.decimal_places)*(10**lease_id.currency_id.decimal_places))
        ewa_words = num2words(int(bd)).capitalize()+' Bahraini Dinars'+' '+num2words(int(fils)).capitalize()+' Fils'
        fils,bd = math.modf(int_amount)
        int_words = num2words(int(bd)).capitalize()+' Bahraini Dinar'
        fils = (float_round(fils,lease_id.currency_id.decimal_places)*(10**lease_id.currency_id.decimal_places))
        int_words_fils = num2words(int(bd)).capitalize()+' Bahraini Dinars'+' '+num2words(int(fils)).capitalize()+' Fils'
        fils,bd = math.modf(lease_id.advance_pay_mnth)
        fils,bd = math.modf(lease_id.monthly_rent)
        fils = (float_round(fils,lease_id.currency_id.decimal_places)*(10**lease_id.currency_id.decimal_places))
        rent_words = num2words(int(bd)).capitalize()+' Bahraini Dinars'
        fils,bd = math.modf(lease_id.security_deposit)
        deposit_words = num2words(int(bd)).capitalize()+' Bahraini Dinars'
        
        
        
        return {
                'doc_ids': docids,
                'ewa_amt':self._decimal_correction(ewa_amount),
                'int_amt':int_amount,
                'duration':self.get_duration(lease_id),
                'ewa':ewa_words,
                'ewa_arabic':ewa_arabic,
                'int_arabic':int_arabic,
                'int_words_fils':int_words_fils,
                'rent':rent_words,
                'rent_amt':self._decimal_correction(lease_id.monthly_rent),
                'deposit':deposit_words,
                'security':self._decimal_correction(lease_id.security_deposit),
                'docs': self.env['zbbm.module.lease.rent.agreement'].browse(docids)
            }
        
        
        
        
     
        
        
        
        
        
        
        
        