# -*- coding: utf-8 -*-

from odoo import models, api, _, fields


class AccountPayment(models.Model):
    _inherit = ['account.payment']
    
    name_on_cheque = fields.Char(string = 'Name On Cheque')
    is_arabic = fields.Boolean('Is Arabic')
    
    @api.onchange('partner_id')  
    def partner_id_change(self):
        if self.partner_id.name_on_cheque:
            self.name_on_cheque = self.partner_id.name_on_cheque
        else:
            self.name_on_cheque = self.partner_id.name
        if str(self.name_on_cheque):
                try:
                    if self.name_on_cheque:
                         string = self.name_on_cheque
                         string.encode('ascii')
                         self.is_arabic = False
                except UnicodeEncodeError:
                     self.is_arabic = True
        else:
            self.is_arabic = True
    
class ResPartner(models.Model):
    _inherit = ['res.partner']
    
    name_on_cheque = fields.Char(string = 'Name On Cheque') 
    
class AccountMove(models.Model):
    _inherit = ['account.move']
    
    name_on_cheque = fields.Char(string = 'Name On Cheque')
    
   
    @api.onchange('partner_id')  
    def partner_change(self):
        if self.partner_id.name_on_cheque:
            self.name_on_cheque = self.partner_id.name_on_cheque
        else:
            self.name_on_cheque = self.partner_id.name
            
          