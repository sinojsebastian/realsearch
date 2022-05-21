from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from num2words import num2words
from datetime import datetime
import math
from odoo.tools.float_utils import float_round
import time
from odoo.tools.misc import formatLang, format_date, get_lang

import logging
_logger = logging.getLogger(__name__)


class PaymentAdviseReportQWeb(models.AbstractModel):

    _name = 'report.zb_bf_custom.payment_advice_report'
    _description='Model For Payment'

    
        
    @api.model
    def _get_report_values(self, docids, data=None):
        payment_id=self.env['account.payment'].browse(docids)
        print('===========payment_id=================',payment_id)
#                 payments = self.env['account.payment'].search([('payment_advise','=',True),('invoice_ids','=',invoices[0].id)])
#                 word = ''
#                 sum=0
#                 for invoice in invoices:
#                     sum=sum+invoice.amount_total
        reference = []
        for payment in payment_id.payment_line_ids:
            print('================================payment',payment,-(payment.debit-payment.credit))
            if payment.allocation:
                if not payment.inv_id.ref:
                    ref = ''
                    for line in payment.inv_id.line_ids:
                        if line.account_id.user_type_id.name != 'Receivable':
                            if line.name:
                                ref += line.name+' '
                    reference.append(ref)
                    
            
        fils,bd = math.modf(payment_id.amount)
        fils = (float_round(fils,payment_id.currency_id.decimal_places)*(10**payment_id.currency_id.decimal_places))
        if fils > 0:
            words = num2words(int(bd)).title()+' '+'Bahraini Dinar and'+ ' '+num2words(int(fils)).title()+' '+payment_id.currency_id.currency_subunit_label+' '+'Only'
        else:
            words = num2words(int(bd)).title()+' '+'Bahraini Dinar'+' '+'Only'
#         words = f'Bahraini Dinar {num2words(int(bd))}& {num2words(int(fils))} {payment_id.currency_id.currency_subunit_label} ONLY'.upper()
        date_lang = datetime.today().strftime(get_lang(self.env).date_format)
        
        return {
                'doc_ids': docids,
                'words':words,
                'date':date_lang,
                'ref':reference,
                'docs': self.env['account.payment'].browse(docids)
            }
        
        
        
        
     
        
        
        
        
        
        
        
        