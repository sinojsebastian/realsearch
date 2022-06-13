from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError,Warning
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
import time


class ReceiptVoucherReportQWeb(models.AbstractModel):

    _name = 'report.zb_bf_custom.receipt_voucher_report'
    _description='Model For Receipt Voucher'
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        payment_ids = self.env['account.payment'].browse(docids)
        word = {}
        sum=0
        advance_sum = 0
        for payment_id in payment_ids:
            if payment_id.state == 'draft':
                raise Warning(_('You cannot take the print on Draft payment'))
            if payment_id.method_type=='advance':
                if payment_id.payment_entries():
                    for payment in payment_id.payment_entries():
                        if 'amount' in payment:
                            sum=sum+payment['amount']
                            advance_sum += payment['amount']
                else:
                    sum = payment_id.amount
                if advance_sum and payment_ids.amount - advance_sum:
                    sum += payment_ids.amount - advance_sum
                fils,bd = math.modf(sum)
                fils = (float_round(fils,payment_id.currency_id.decimal_places)*(10**payment_id.currency_id.decimal_places))
                if fils > 0:
                    words = num2words(int(bd)).title()+' '+'Bahraini Dinar and'+ ' '+num2words(int(fils)).title()+' '+payment_id.currency_id.currency_subunit_label+' '+'Only'
                else:
                    words = num2words(int(bd)).title()+' '+'Bahraini Dinar '+'Only'

                # words = f'BHD {num2words(int(bd))} AND {num2words(int(fils))} {payment_id.currency_id.currency_subunit_label} /- ONLY'.upper()
                word.update({payment_id.id:words})
            else:
                for payment in payment_id.payment_line_ids:
                    sum=sum+payment.allocation
                    fils,bd = math.modf(sum)
                    fils = (float_round(fils,payment_id.currency_id.decimal_places)*(10**payment_id.currency_id.decimal_places))
                    if fils > 0:
                        words = num2words(int(bd)).title()+' '+'Bahraini Dinar and'+ ' '+num2words(int(fils)).title()+' '+payment_id.currency_id.currency_subunit_label+' '+'Only'
                    else:
                        words = num2words(int(bd)).title()+' '+'Bahraini Dinar'+' '+'Only'
 
                    word.update({payment_id.id:words})
        return {
            'doc_ids': docids,
            'words':word,
            'advance_sum':advance_sum,
            'payment_amount':payment_ids.amount,
            'docs': self.env['account.payment'].browse(docids),
            'doc_model': self.env['account.payment'],
            
        }
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        