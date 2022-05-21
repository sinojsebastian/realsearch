# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import date

def first_day_of_month(d):
    return date(d.year, d.month, 1)

class OwnerStatementReport(models.TransientModel):
    
    _name = 'owner.statement.report'
    _description = 'Owner Rental Statement'
    
    
    def print_owner_statement(self):
        
        datas = {
            'ids': self.ids,
            'form': self.read(),
            
        }
        
        return self.env.ref('zb_bf_custom.report_owner_qweb').report_action(self,data=datas)
        
   
#     @api.model
#     def default_partner_id(self):
#         '''This function return building id for voucher'''
#         partner = False
#         context = self._context
#         if context.get('active_model', '') and context['active_model'] == 'res.partner':
#             if context.get('active_id', False):
#                 partner = self.env.get('res.partner').browse(context['active_id'])
#                 if partner:
#                     partner = partner.id
#                 else:
#                     partner = False
#         return partner
                          
     
    from_date = fields.Date("From Date",default = first_day_of_month(date.today()))
    to_date = fields.Date("To Date" ,default=fields.Date.context_today)
    #partner_id = fields.Many2one('res.partner','Partner',default=default_partner_id)



