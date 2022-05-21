from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
import time
import logging
_logger = logging.getLogger(__name__)

class ResaleQWeb(models.AbstractModel):

    _name = 'report.zb_bf_custom.report_resale_new'
    _description='Model For custom'

    
        
    @api.model
    def _get_report_values(self, docids, data=None):
        doc_id = self.env['zbbm.unit'].browse(docids)
        for rec in doc_id:
            inv_amnt_total=0
#             move = self.env['account.move'].search([('state','=','posted'),('unit_id','=',rec.id),('type','=','out_invoice'),('partner_id','=',rec.buyer_id.id)])
#             
#             payments = self.env['account.payment'].search([('')])
#             
            move_lines = self.env['account.move.line'].search([('move_id.state','=','posted'),('move_id.unit_id','=',rec.id),('move_id.type','=','entry'),('partner_id','=',rec.owner_id.id)])
            inv_amnt_total=sum([invoice.debit for invoice in move_lines if invoice.debit])
            print('==================inv_amnt_total==========',inv_amnt_total)
        
        return {
                'doc_ids': docids,
                'docs': self.env['zbbm.unit'].browse(docids),
                'doc_model': self.env['zbbm.unit'],
                'inv_amnt_total':inv_amnt_total,
                
                }
        

        