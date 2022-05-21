from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class InternalTransferPayments(models.TransientModel):
    _name = 'internal.transfer.payments'

    @api.model
    def load_values(self):
        active_ids = self._context.get('active_ids')
        if self._context.get('active_model') == 'account.payment' and active_ids:
            payments = self.env['account.payment'].search([('id','=',active_ids)])
            list = []
            for payment in payments:
                dic={
                     'date':payment.payment_date,
                     'partner_id':payment.partner_id,
                     'memo':payment.name,
                     'description':payment.notes,
                     'transferred':payment.transferred,
                     'amount':payment.amount
                     }
                list.append((0,0,dic))
        return list
    
    @api.depends('line_ids.amount')
    def compute_total_amount(self):
        for vals in self:
            tot = 0.000
            for lines in vals.line_ids:
                tot += lines.amount
            vals.total_amount = tot
                
                
    def validate_internal_payments(self):
        list=[]
        for vals in self.line_ids:
            dic={'account_id':''
                 }
        dst_move = self.env['account.move'].create(
                    {'name':'ABCDEF',
                     'date':self.date,
                     'line_ids':''})
        
            
    from_journal_id = fields.Many2one('account.journal',"Payment From")
    to_journal_id = fields.Many2one('account.journal',"Payment To")
    date = fields.Date("Date")
    total_amount = fields.Float("Total Amount",compute="compute_total_amount")
    line_ids = fields.One2many('internal.transfer.payments.line','payment_id',"Lines",default=load_values)
    
            
class InternalTransferPaymentsLine(models.TransientModel):
    _name = 'internal.transfer.payments.line'
    
    date = fields.Date("Date")
    partner_id = fields.Many2one('res.partner',"Customer")
    memo = fields.Char("Memo")
    description = fields.Char("Description")
    transferred = fields.Boolean("To Be Transferred")
    amount = fields.Float("Amount")
    payment_id = fields.Many2one('internal.transfer.payments',"Payments")