# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)..
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


from odoo import models, fields, api,exceptions,_
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError



class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
    _description = 'Accounting Voucher'
    
    
    cheque_no = fields.Char(string='Cheque No')
    cheque_date = fields.Date(string='Cheque Date')
    building_id = fields.Many2one('zbbm.building','Building')
    

    
    
    @api.multi
    def first_move_line_get(self, move_id, company_currency, current_currency):
        debit = credit = 0.0
        if self.voucher_type == 'purchase':
            if self.amount < 0:
               debit = self._convert_amount(abs(self.amount)) 
            else:
                credit = self._convert_amount(abs(self.amount))
        elif self.voucher_type == 'sale':
            if self.amount < 0:
               credit = self._convert_amount(abs(self.amount)) 
            else:
                debit = self._convert_amount(abs(self.amount))
            
#             debit = self._convert_amount(self.amount)
#         if debit < 0.0: debit = 0.0
#         if credit < 0.0: credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        if self.building_id:
            build = self.building_id.id
        else:
            build = False
        #set the first line of the voucher
        move_line = {
                'name': self.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': self.account_id.id,
                'building_id':build,
                'move_id': move_id,
                'journal_id': self.journal_id.id,
                'partner_id': self.partner_id.id,
                'currency_id': company_currency != current_currency and current_currency or False,
                'amount_currency': (sign * abs(self.amount)  # amount < 0 for refunds
                    if company_currency != current_currency else 0.0),
                'date': self.account_date,
                'date_maturity': self.date_due
            }
        return move_line
    
    
    @api.multi
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if self.building_id:
            build = self.building_id.id
        else:
            build = False
#DB         if self.cheque_no:
#             cheque_no = self.cheque_no
#         else:
#             cheque_no = False
        for line in self.line_ids:
            debit = credit = 0.0
            #create one move line per voucher line where amount is not 0.0
            if not line.price_subtotal:
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            
            if self.voucher_type == 'purchase':
                if line.price_subtotal < 0:
                  credit = abs(line.price_subtotal)
                else:
                  debit = abs(line.price_subtotal)
#               abs(amount) if self.voucher_type == 'sale' else 0.0    
            if self.voucher_type == 'sale':
                if line.price_subtotal < 0:
                  debit = abs(line.price_subtotal)
                else:
                  credit = abs(line.price_subtotal)    
                    
            
            amount = self._convert_amount(line.price_unit*line.quantity)
            move_line = {
                'journal_id': self.journal_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': self.partner_id.id,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': credit,
                'building_id':build,
#                 'cheque_no':cheque_no,
                'debit': debit,
                'date': self.account_date,
                'tax_ids': [(4,t.id) for t in line.tax_ids],
                'amount_currency': line.price_subtotal if current_currency != company_currency else 0.0,
                'currency_id': company_currency != current_currency and current_currency or False,
            }
            self.env['account.move.line'].with_context(apply_taxes=True).create(move_line)
        return line_total
    
    
    
    
    
    
#     @api.multi
#     def first_move_line_get(self, move_id, company_currency, current_currency):
#         print("enter===========================firstmoveline")
#         debit = credit = 0.0
#         if self.voucher_type == 'purchase':
#             credit = self._convert_amount(self.amount)
#             
#         elif self.voucher_type == 'sale':
#             debit = self._convert_amount(self.amount)
#             
#         if debit < 0.0:
#             debit =  debit   ##adding for negative value
# #             debit = 0.0
#         if credit < 0.0:
#             credit =  credit
# #             credit = 0.0
#         sign = debit - credit < 0 and -1 or 1
#         print(credit,"---------------------------",debit,self.account_id)
#         account_id = self.account_id.id
#         
#         move_line = {
#                 'name': self.name or '/',
#                 'debit': debit,
#                 'credit': credit,
#                 'account_id': self.account_id.id,
#                 'move_id': move_id,
#                 'journal_id': self.journal_id.id,
#                 'partner_id': self.partner_id.commercial_partner_id.id,
#                 'currency_id': company_currency != current_currency and current_currency or False,
#                 'amount_currency': (sign * abs(self.amount)  # amount < 0 for refunds
#                     if company_currency != current_currency else 0.0),
#                 'date': self.account_date,
#                 'date_maturity': self.date_due,
#                 'payment_id': self._context.get('payment_id'),
#             }
#         print (move_line,"move line------------------------")
#         return move_line
    
#     @api.multi
#     def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
#          
#         '''
#         Create one account move line, on the given account move, per voucher line where amount is not 0.0.
#         It returns Tuple with tot_line what is total of difference between debit and credit and
#         a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).
#  
#         :param voucher_id: Voucher id what we are working with
#         :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
#         :param move_id: Account move wher those lines will be joined.
#         :param company_currency: id of currency of the company to which the voucher belong
#         :param current_currency: id of currency of the voucher
#         :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
#         :rtype: tuple(float, list of int)
#         '''
#          
#          
#         for line in self.line_ids:
#              
#             #create one move line per voucher line where amount is not 0.0
#             if not line.price_subtotal:
#                 continue
#             line_subtotal = line.price_subtotal
#             if self.voucher_type == 'sale':
#                 line_subtotal = -1 * line.price_subtotal
#                  
#             amount = self._convert_amount(line.price_unit*line.quantity)
#              
#             credit = 0.0
#             debit = 0.0
#             if self.voucher_type == 'sale':
#                 if amount < 0:
#                     debit = -1 * amount
#                 else:
#                     credit = abs(amount)
#                      
#             if self.voucher_type == 'purchase':
#                 if amount < 0:
#                     credit = -1 * amount
#                 else:
#                     debit = abs(amount)
#             account_id = line.account_id.id
#                      
#             move_line = {
#                 'journal_id': self.journal_id.id,
#                 'name': line.name or '/',
#                 'account_id': line.account_id.id,
#                 'move_id': move_id,
#                 'partner_id': self.partner_id.commercial_partner_id.id,
#                 'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
#                 'quantity': 1,
#                 'credit': abs(amount) if self.voucher_type == 'sale' else 0.0,
#                 'debit': abs(amount) if self.voucher_type == 'purchase' else 0.0,
#                 'date': self.account_date,
#                 'tax_ids': [(4,t.id) for t in line.tax_ids],
#                 'amount_currency': line_subtotal if current_currency != company_currency else 0.0,
#                 'currency_id': company_currency != current_currency and current_currency or False,
#                 'payment_id': self._context.get('payment_id'),
#             }
#             self.env['account.move.line'].create(move_line)
#         return line_total        
        
        
    
    
    
