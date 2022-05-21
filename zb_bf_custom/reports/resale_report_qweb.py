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


class ResaleReportQweb(models.AbstractModel):

    _name = 'report.zb_bf_custom.report_resale_new'
    _description='Resale Report'
    
    
    @api.model
    def _get_report_values(self, docids,data=None):
        
        unit_id = self.env['zbbm.unit'].browse(docids)
        params = self.env['ir.config_parameter'].sudo() 
        resale_commision_journal = params.get_param('zb_bf_custom.resale_commission_journal_id') or False
        installment_journal = params.get_param('zb_bf_custom.installment_journal_id') or False
        advance_journal = params.get_param('zb_bf_custom.advance_payment_journal_id') or False
        funds_collected = 0
        resale_amounts = 0
        resale_vat = 0
        total_expenses = 0
        resale_payments = self.env['account.payment'].search([('unit_id','=',unit_id.id)])
        expense_ids = self.env['account.move'].search([('unit_id','=',unit_id.id),('type','=','in_invoice')])
        expenses = {}
        for payment in resale_payments:
            if payment.reconciled_invoice_ids:
                for inv in payment.reconciled_invoice_ids:
                    # if inv.journal_id.id == int(installment_journal):
                    if inv.unit_id and inv.journal_id.id == int(installment_journal) or inv.journal_id.id == int(advance_journal):
                        for each in inv._get_reconciled_info_JSON_values():
                            if each['account_payment_id'] == payment.id:
                                funds_collected += each['amount']
                    elif inv.journal_id.id == int(resale_commision_journal):
                        if inv.partner_id.id == unit_id.owner_id.id:
                            tax = inv.amount_total - inv.amount_untaxed
                            if tax:
                                resale_vat += tax
                            for each in inv._get_reconciled_info_JSON_values():
                                if each['account_payment_id'] == payment.id:
                                    resale_amounts += each['amount']
        # resale_commission = 0
        print('=============resale_amounts==============',resale_amounts)
        if resale_amounts:
            # resale_commission = resale_amounts * (2/100)
            total_expenses += resale_amounts
        if expense_ids:
            for move in expense_ids:
                key = move.journal_id
                if key in expenses:
                    expenses[key] += move.amount_total
                else:
                    expenses[key] = move.amount_total
        if resale_vat:
            total_expenses += resale_vat
        if expenses:
            for key,value in expenses.items():
                total_expenses += value
        
        return {
            'doc_ids': docids,
            'docs': self.env['zbbm.unit'].browse(docids),
            'funds_collected':funds_collected,
            'resale_commission':resale_amounts,
            'resale_vat':resale_vat,
            'expenses':expenses,
            'total_expenses':total_expenses,
            'doc_model': self.env['account.payment'],
            
        }
                                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        