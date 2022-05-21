from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import time
from math import floor

import logging
_logger = logging.getLogger(__name__)


class ManagementContractReportQWeb(models.AbstractModel):

    _name = 'report.zb_bf_custom.management_contract'
    _description='Model For Management Contract Report'

    
    def get_management_percent(self,value):
        
        mngmnt_percent = 0
        float_decimal = value - floor(value)
        if float_decimal == 0:
            mngmnt_percent = int(value)
        else:
            mngmnt_percent = format(value, ".2f")
        return mngmnt_percent
    
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
        
        module_id=self.env['zbbm.module'].browse(docids)
        
        latest_contract = module_id.management_contract_ids.filtered(lambda r: r.owner_id.id == module_id.owner_id.id).sorted(key=lambda r: r.id)
        latest_contract_id = ''
        if latest_contract:
            latest_contract_id = latest_contract[-1]
        
        duration = ''
        if latest_contract_id:
            from_date = latest_contract_id.from_date
            agreement_to_date = latest_contract_id.to_date
            if from_date:
                day = from_date.day
            month = 0
            year = 0
            if from_date and agreement_to_date:
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
            
            
            
            # from_date = latest_contract_id.from_date
            # to_date = latest_contract_id.to_date
            # difference = to_date.year-from_date.year
            # duration = ''
            # if difference:
            #     fils,bd = math.modf(difference)
            #     year_words = num2words(int(bd)).capitalize()
            #     duration = '%s(%s) year'%(year_words,difference) 
        
        bank_id = False
        if module_id.owner_id.bank_ids:
            bank_id = module_id.owner_id.bank_ids[0]
        
        return {
                'doc_ids': docids,
                'latest_contract':latest_contract_id,
                'mngmnt_percent':self.get_management_percent(module_id.management_fees_percent),
                'contract_fees':self._decimal_correction(latest_contract_id.contract_fees) if latest_contract_id else 0,
                'owner_bank':bank_id,
                'duration':duration,
                'docs': self.env['zbbm.module'].browse(docids)
            }
        
        
        
        
     
        
        
        
        
        
        
        
        