from odoo import _, api, fields, models
from odoo.exceptions import ValidationError,Warning
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
import time


class CommissionInvoiceReportQWeb(models.AbstractModel):

    _name = 'report.zb_bf_custom.commission_invoice_report'
    _description='Model For Commission Invoice'
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        bank_dict ={}
        params = self.env['ir.config_parameter'].sudo() 
        company_bank_id = params.get_param('zb_bf_custom.company_bank_id') or False
        bank = self.env['res.partner.bank'].search([('id','=',company_bank_id)])
        if not company_bank_id:
            raise Warning(_("""Please configure Company bank in the General Settings"""))
        invoice_ids = self.env['account.move'].browse(docids)
        word = {}
        sum=0
        for invoice in invoice_ids:
#             for line in invoice.invoice_line_ids:
            sum=sum+invoice.amount_total
            fils,bd = math.modf(sum)
            fils = (float_round(fils,invoice.currency_id.decimal_places)*(10**invoice.currency_id.decimal_places))
            if fils > 0:
                words = num2words(int(bd)).title()+' '+'Bahraini Dinar and'+ ' '+num2words(int(fils)).title()+' '+invoice.currency_id.currency_subunit_label+' '+'Only'
            else:
                words = num2words(int(bd)).title()+' '+'Bahraini Dinar'+' '+'Only'
            word.update({invoice.id:words})
            bank_dict[invoice.id] = {
                                        'name' : bank.bank_id.name,
                                        'partner':bank.partner_id.name,
                                        'acc_number':bank.acc_number,
                                        'iban':bank.iban_no,
                                        'bic':bank.bank_id.bic
                                        }
        
        
        return {
            'doc_ids': docids,
            'bank_data' : bank_dict,
            'words':word,
            'docs': self.env['account.move'].browse(docids),
            'doc_model': self.env['account.move'],
            
        }
        
        
        
        
        
        
        
        
        
        
        
        
        
        