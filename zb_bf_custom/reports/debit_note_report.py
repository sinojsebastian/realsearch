from odoo import fields, models,api
import re
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
import time

class DebitNoteReportQWeb(models.AbstractModel):

    _name = 'report.zb_bf_custom.debit_note_report'
    _description='Model For Debit Note Report'
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        move_ids = self.env['account.move'].browse(docids)
        vouch = {}
        payment_ids = []
        invoice_id = ''
        for move_id in move_ids:
            if move_id.ref:
                l_strip = move_id.ref.lstrip('Reversal of: ')
                sub_str=l_strip.split(",", 1)
                final_str = sub_str[0]
                invoice_id = self.env['account.move'].search([('type','=','in_invoice'),('name','=',final_str)])
                voucher_id = self.env['account.payment'].search([('partner_id','=',invoice_id.partner_id.id),('state','=','posted')])
                for payment in voucher_id:
                    if payment.reconciled_invoice_ids:
                        for inv in payment.reconciled_invoice_ids:
                            if inv.id == invoice_id.id:
                                payment_ids.append(payment)
        vouch[move_ids] = {
                            'payno' : payment_ids,
                            'inv' : invoice_id
                            }
        word = {}
        sum=0
        for payment in move_ids:
#             for line in payment.invoice_line_ids:
            sum=sum+payment.amount_total
            fils,bd = math.modf(sum)
            fils = (float_round(fils,payment.currency_id.decimal_places)*(10**payment.currency_id.decimal_places))
            if fils > 0:
                words = num2words(int(bd)).title()+' '+' Bahraini Dinar and '+ ' '+num2words(int(fils)).title()+' '+payment.currency_id.currency_subunit_label+' '+' Only'
            else:
                words = num2words(int(bd)).title()+' '+' Bahraini Dinar '+' Only'
            word.update({payment.id:words})
                
                
        return {
            'doc_ids': docids,
            'docs': self.env['account.move'].browse(docids),
            'doc_model': self.env['account.move'],
            'words':word,
            'payment_no' : vouch,
            
        }
      