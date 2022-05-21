from odoo import models, fields, api
from datetime import date,datetime

class CheckBook(models.Model):
    _name = 'check.book'
    _description = "Check Book"
    _rec_name = "bank_account_id"
    
               
    @api.onchange('starting_number')
    def get_next_num(self):
        for rec in self:
            rec.next_number = rec.starting_number
            
    @api.onchange('number_check_leaf','starting_number')
    def onchange_check_number(self): 
       for rec in self:
           if rec.number_check_leaf:
               if rec.starting_number:
                   rec.end_number = int(rec.starting_number)+rec.number_check_leaf-1
            
    def write(self,vals):
        if vals.get('next_number',False):
            if vals.get('end_number',False):
                if vals['next_number']== vals['end_number']:
                    vals['state'] = 'finished'
            else:
                if vals['next_number']== self.end_number:
                    vals['state'] = 'finished'
        
        res = super(CheckBook,self).write(vals)
        return res
    
    end_number = fields.Char('End Number')
    next_number = fields.Char('Next Number')
    bank_account_id = fields.Many2one('account.journal','Bank Account')
    number_check_leaf = fields.Integer('Number Of Check Leaves')
    starting_number = fields.Char('Starting Number')
    state = fields.Selection([
                    ('draft','Draft'),
                    ('active', 'Active'),
                    ('finished', 'Finished'),
                    ], 'State',default='draft')
    
    


#     
    

                   
       