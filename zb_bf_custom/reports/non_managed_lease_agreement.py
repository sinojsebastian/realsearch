from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
from datetime import date,datetime,timedelta 
import time

import logging
_logger = logging.getLogger(__name__)


class RentAgreementReportQWeb(models.AbstractModel):

    _name = 'report.zb_bf_custom.non_managed_lease_agreement'
    _description='Model For Non Managed Lease Agreement'

    
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
    
    def get_duration(self,lease_id):
    
        from_date = lease_id.agreement_start_date
        to_date = lease_id.agreement_end_date
        difference = to_date.year-from_date.year
        duration = ''
        pro_rent_days = 0
        if lease_id.moving_date:
            pro_rent_days = (datetime.strptime(str(lease_id.agreement_start_date), '%Y-%m-%d')-datetime.strptime(str(lease_id.moving_date), '%Y-%m-%d')).days
        if difference:
            fils,bd = math.modf(difference)
            year_words = num2words(int(bd)).capitalize()
            duration = '%s(%s) year'%(year_words,difference) 
        if pro_rent_days:
            fils,bd = math.modf(pro_rent_days)
            pro_days_words = num2words(int(bd)).capitalize()
            duration = duration+' & %s(%s) Days'%(pro_days_words,pro_rent_days)
    
        return duration
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        lease_id=self.env['zbbm.module.lease.rent.agreement'].browse(docids)
        
        params = self.env['ir.config_parameter'].sudo()  
        ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id')
        if not ewa_product_id:
            raise Warning(_("""Please configure EWA Service Product in the Accounting Settings"""))
        
        internet_product_id = params.get_param('zb_bf_custom.internet_product_id')
        if not internet_product_id:
            raise Warning(_("""Please configure Internet Service Product in the Accounting Settings"""))
        
        ewa_obj = self.env['product.product'].browse(int(ewa_product_id[0]))
       
        internet_obj = self.env['product.product'].browse(int(internet_product_id[0]))
        
        fils,bd = math.modf(lease_id.monthly_rent)
        fils = (float_round(fils,lease_id.currency_id.decimal_places)*(10**lease_id.currency_id.decimal_places))
        rent_words = num2words(int(bd)).capitalize()+' Bahraini Dinar'
        pro_rated_rent =0.000
        ewa_arabic = ''
        if lease_id.monthly_rent:
            pro_rated_rent = lease_id.monthly_rent/30
        fils,bd = math.modf(lease_id.advance_pay_mnth)
        mnth_words = num2words(int(bd)).capitalize()
        fils,bd = math.modf(lease_id.security_deposit)
        deposit_words = num2words(int(bd)).capitalize()+' Bahraini Dinar'
        pro_rent_days = 0
        if lease_id.moving_date:
            pro_rent_days = (datetime.strptime(str(lease_id.agreement_start_date), '%Y-%m-%d')-datetime.strptime(str(lease_id.moving_date), '%Y-%m-%d')).days
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
        fils,bd = math.modf(ewa_amount)
        fils = (float_round(fils,lease_id.currency_id.decimal_places)*(10**lease_id.currency_id.decimal_places))
        ewa_words = num2words(int(bd)).capitalize()+' Bahraini Dinars'+' '+num2words(int(fils)).capitalize()+' Fils'
        fils,bd = math.modf(int_amount)
        int_words = num2words(int(bd)).capitalize()+' Bahraini Dinar'
        fils = (float_round(fils,lease_id.currency_id.decimal_places)*(10**lease_id.currency_id.decimal_places))
        int_words_fils = num2words(int(bd)).capitalize()+' Bahraini Dinars'+' '+num2words(int(fils)).capitalize()+' Fils'
        fils,bd = math.modf(lease_id.pro_rated_amt)
        pro_rent_words = num2words(int(bd)).capitalize()+' Bahraini Dinar'

        return {
                'doc_ids': docids,
                'rent':rent_words,
                'rent_amt':self._decimal_correction(lease_id.monthly_rent),
                'deposit':deposit_words,
                'ewa_amt':self._decimal_correction(ewa_amount),
                'int_amt':self._decimal_correction(int_amount),
                'security':self._decimal_correction(lease_id.security_deposit),
                'pro_rated_rent':self._decimal_correction(pro_rated_rent),
                'pro_rent_days':pro_rent_days,
                'pro_rent_words':pro_rent_words,
                'ewa':ewa_words,
                'duration':self.get_duration(lease_id),
                'ewa_arabic':ewa_arabic,
                'int_arabic':int_arabic,
                'month':lease_id.advance_pay_mnth,
                'mnth_words':mnth_words,
                'internet':int_words,
                'int_words_fils':int_words_fils,
                'docs': self.env['zbbm.module.lease.rent.agreement'].browse(docids)
            }
        
        
        
        
     
        
        
        
        
        
        
        
        