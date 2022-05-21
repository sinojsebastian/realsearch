
from odoo import models, fields, api
from datetime import date,datetime

class AccountPayment(models.Model):
    
    _inherit = 'account.payment'
    _description = "Account Payment Fields Modification"
    
       
    
    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id and self.payment_type == 'outbound':
            check_books_id = self.env['check.book'].search([('bank_account_id','=',self.journal_id.id),('state','=','active')])
            if len(check_books_id) == 1:
               self.check_book_id = check_books_id.id
            if check_books_id:
                self.check_book = True
            else:
                self.check_book = False
   
    @api.onchange('check_book_id')
    def onchange_check_number(self): 
       for rec in self:
           rec.cheque_no = rec.check_book_id.next_number  
        
    def post(self):
        res=super(AccountPayment, self).post()
        for rec in self:
#             if rec.check_book_id.next_number != rec.cheque_n:
            rec.check_book_id.next_number = int(rec.check_book_id.next_number)+1       
     
    
    check_book_id = fields.Many2one('check.book','Check Book')
    check_book = fields.Boolean(string='Check')
    invoice_id = fields.Many2one('account.move',string='Invoice')
    payment_mode = fields.Selection([
                    ('cash', 'Cash'),
                    ('cheque', 'Cheque'),
                    ('transfer', 'Transfer'),
                    ('credit card', 'Credit Card')
                    ], 'Payment Mode')
    

    