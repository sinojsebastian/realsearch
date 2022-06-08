from odoo import api, fields, models, _
import datetime
from odoo.exceptions import ValidationError,Warning
from datetime import timedelta
from num2words import num2words

class ChequeQWeb(models.AbstractModel):

    _name = 'report.zb_check_printing.report_check'
    _description='Model For Cheque printing'

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_ids = self.env['account.payment'].browse(docids)
        print('===============cheque-payment===============',payment_ids)
        for payment_id in payment_ids:
            if payment_id.state == 'draft':
                raise Warning(_('You cannot make the Cheque printing on Draft Payment'))
        return {
            'doc_ids': docids,
            'docs': self.env['account.payment'].browse(docids),
            'doc_model': self.env['account.payment'],
        }


class check_data_get(models.Model):
    _inherit = "account.payment"
    
    ac_payee = fields.Boolean('A/C Payee',default=False)
    
    def _get_amount(self):
        return str("{:0,.3f}".format(self.amount))
    
    def amount_to_text_wrapp_check(self, amt, obj):
        amt_text = []
        amount_text = self.amount_to_text_check()
        position_list = [pos for pos, char in enumerate(amount_text) if char == ' ']
        if len(amount_text) > 26:
            if amount_text[26] not in ('-', ' '):
                txt_pos = [p for p in position_list if p < 26][-1]
                amt_text.append((amount_text[0:txt_pos],amount_text[txt_pos:64],amount_text[64:]))
            else:
                amt_text.append((amount_text[0:26],amount_text[26:64],amount_text[64:]))
        return amt_text
    
    def amount_to_text_check(self):
        amount_in_words = ''
        for record in self:
            amount_untaxed = '%.3f' % self.amount
            list = str(amount_untaxed).split('.')
            first_part = False
            second_part = False
            if num2words(int(list[0])):
                first_part = num2words(int(list[0])).title()
            if num2words(int(list[1])):
                second_part = num2words(int(list[1])).title()
            # amount_in_words = ' Only '
            if 'And' in first_part:
                first_part = first_part.replace('And','')
            if first_part:
                amount_in_words =  str(first_part) + amount_in_words 
            else:
                amount_in_words =  'Zero' + amount_in_words 
            if second_part:
                if list[1] != '000':
                    amount_in_words = amount_in_words + ' and ' +str(list[1]) + ' Fils ' 
                #amount_in_words = ' ' + amount_in_words + ' and Fils ' + str(second_part)
        if  amount_in_words:
            amount_in_words += ' Only'
        return amount_in_words
    
    
   
    def check_data_get(self):
        '''Function for splitting check date'''
        date_dict = {}
        if self.payment_date:
            count = 0
            pay_date = str(self.payment_date)
            date = pay_date.split('-')
            for d in date:
                if len(d) == 2:
                    count = count + 1
                    date_dict.update({count:d[0]})
                    count = count + 1
                    date_dict.update({count:d[1]})
                elif len(d) == 4:
                    count = count + 1
                    date_dict.update({count:d[0]})
                    count = count + 1
                    date_dict.update({count:d[1]}) 
                    count = count + 1
                    date_dict.update({count:d[2]})
                    count = count + 1
                    date_dict.update({count:d[3]})
            
            return date_dict
                    