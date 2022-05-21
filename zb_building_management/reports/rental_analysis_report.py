# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
from dateutil import relativedelta
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import fields,osv
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class rental_analysis(models.Model):
    
    _name = "rental.analysis"
    _description = "Rental Analysis"
    _auto = False
    _order = 'date'
    
                    
    @api.depends('invoice_id')
    def _calculate_payment_total(self):
        '''Function to calculate total from all the valid payments'''
        for items in self:
            if items.invoice_id and items.invoice_id.line_ids:
                total_payments = 0.00
                for payments in items.invoice_id.line_ids:
    #                  if payments.state not in ['draft', 'cancel']:
                    if items.invoice_id.type in ['out_invoice', 'in_refund']:
                        total_payments = total_payments + payments.credit
                    if items.invoice_id.type in ['out_refund', 'in_invoice']:
                        total_payments = total_payments + payments.debit
                items.invoice_payment = total_payments
    
    
    building_id = fields.Many2one('zbbm.building', string='Building')
    module_id = fields.Many2one('zbbm.module', string='Module')
    partner_id = fields.Many2one('res.partner', string='Tenant')
    date = fields.Date('Date')
    month = fields.Many2one('zbbm.month', string='Month')
    type = fields.Selection([
            ('income','Income'),
            ('expense','Expense')], string='Type')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    invoice_amount = fields.Float(string='Amount',digits='Product Unit of Measure')
    invoice_balance = fields.Float(string='Balance',digits='Product Unit of Measure')
    
    invoice_payment = fields.Float(string='Payment', compute='_calculate_payment_total',
                                   digits='Product Unit of Measure')
    
    month_selection = fields.Selection([('current_month', 'Current Month'),
            ('one_month', 'One Month'), ('two_month', 'Two Month'),
            ('other', 'Other')], string='Month Type')
   
   
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'rental_analysis')
        self.env.cr.execute("""create or replace view rental_analysis as (
            select
               inv.id as id, 
               inv.building_id as building_id, 
               inv.module_id as module_id,
               inv.partner_id as partner_id, 
               inv.invoice_date as date,
               inv.month_id as month,
               inv.month_selection as month_selection,
               
               
               case when inv.type in ('out_refund','out_invoice') then 'income'
               else 'expense' end as type,
               
               
               case when inv.type in ('out_refund','in_refund') then inv.amount_total*-1
               else inv.amount_total end as invoice_amount,
               inv.amount_residual as invoice_balance,
               inv.id as invoice_id
            from
                account_move as inv
            where inv.state not in ('draft', 'cancel') and inv.module_id is not null
            order by inv.invoice_date
                )""")
        
        
#     def _search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
#          
#          
#         res = super(rental_analysis, self)._search(cr, user, args, offset=offset, limit=limit, order=order,
#             context=context, count=count, access_rights_uid=access_rights_uid)
#          
#          
#         return res
#     
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         
#         res = super(rental_analysis, self).name_search(name, args=args, operator=operator, limit=limit)
#         return res



# rental_analysis()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
