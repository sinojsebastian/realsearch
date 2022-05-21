# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models,_
from openerp.tools.translate import _


def first_day_of_month(d):
    return date(d.year, d.month, 1)

class SupplierStatementReport(models.TransientModel):
    
    _name = 'supplier.statement.report'
    _description = 'Supplier Statement'
    
    def print_supplier_statement(self):
        
        datas = {
                'ids': self.ids,
                'form': self.read(),
                }
    
        return self.env.ref('zb_supplier_statement.report_supplier_statement').report_action(self,data=datas)
    
    @api.model
    def default_partner_id(self):
        '''This function return building id for voucher'''
        partner = False
        context = self._context
        if context.get('active_model', '') and context['active_model'] == 'res.partner':
            if context.get('active_id', False):
                partner = self.env.get('res.partner').browse(context['active_id'])
                if partner:
                    partner = partner.id
                else:
                    partner = False
        return partner                      
     
    from_date = fields.Date("From Date",default = first_day_of_month(date.today()))
    show_paid_inv = fields.Boolean('Show Paid Bills') 
    partner_id = fields.Many2one('res.partner','Partner',default=default_partner_id)
