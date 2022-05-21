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
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
# from odoo.osv.orm import setup_modifiers
from time import strptime
import datetime
from dateutil import relativedelta
from lxml import etree
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date, timedelta
from num2words import num2words


# DBclass account_register_payments(models.TransientModel):
#     _inherit = "account.register.payments"
#     
#     @api.model
#     def default_description(self):
#         desc = ''
#         if self._context.get('active_model') and self._context.get('active_model') == 'account.invoice':
#             active_ids = self._context.get('active_ids')
#             if active_ids:
#                 invoices = self.env['account.invoice'].browse(self._context.get('active_ids'))
#                 for invoice in invoices:
#                     for lines in invoice.invoice_line_dates_ids:
#                         desc += lines.name+','
#                 desc = desc[:-1]
#         return desc
# 
#     cheque_no = fields.Char('Cheque No', size=64)
#     cheque_date = fields.Date('Cheque Date')
#     cheque_bank_id = fields.Many2one('res.bank', string='Cheque Bank')
#     notes = fields.Char("Description", size=64,required=True, default=default_description)
#     note = fields.Text("Notes", size=64)
#     
#     @api.onchange('communication')
#     def load_memo(self):
#         active_ids = self._context.get('active_ids')
#         invoices = self.env['account.invoice'].browse(active_ids)
#         desc = ''
#         for inv in invoices:
#             desc += inv.number + ','
#         self.communication = desc[:-1]
         

     
class account_payment(models.Model):
    _inherit = 'account.payment'
    _description = "Account Payment Fields Modification"
    
   
    @api.depends('journal_id', 'journal_id.type')
    def compute_journal_type(self):
        for rec in self:
            rec.journal_type = rec.journal_id and rec.journal_id.type or False
            
            
            
    def default_unit_id(self):
        '''This function return additional id for voucher'''
        unit_id = False
        context = self._context or {}
        if context.get('active_model', '') and context['active_model'] == 'account.move':
            if context.get('active_id', False):
                invoice = self.env.get('account.move').browse(context['active_id'])
                if invoice.unit_id:
                    unit_id = invoice.unit_id.id
                else:
                    unit_id = False
        return unit_id
   
   
    dummy = fields.Boolean('dummy',default= False,copy=False)
#     journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash','post_dated_chq'))])
#     journal_type = fields.Selection([('sale', 'Sale'),('sale_refund','Sale Refund'), 
#                                      ('purchase', 'Purchase'), 
#                                      ('purchase_refund','Purchase Refund'),
#                                      ('cash', 'Cash'), 
#                                      ('bank', 'Bank and Cheque'), 
#                                      ('general', 'General'), 
#                                      ('situation', 'Opening/Closing Situation'), 
#                                      ('post_dated_chq', 'Post Dated CHQ')], string='Type',
#                                      compute='compute_journal_type', store=True)
#     
#     cheque_no = fields.Char(string='Cheque No')
#     cheque_date = fields.Date(string='Cheque Date')
#     cheque_bank_id = fields.Many2one('res.bank',string='Cheque Bank')
    partner_journal_id = fields.Many2one('account.journal',string='Bank Journal')
    inv_id = fields.Many2one('account.move', string='Invoice')
    unit_id = fields.Many2one('zbbm.unit',string="Unit",default=default_unit_id)
    
    
#DB     @api.onchange('journal_id')
#     def _onchange_journal(self):
#         res = super(account_payment, self)._onchange_journal()
#         if self.journal_id:
#             self.journal_type = self.journal_id.type
#         return res
    
    
#     transferred =fields.Boolean('to be transferred ',default= False,copy=False)

    def cancel(self):
        for rec in self:
            for move in rec.move_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                move.unlink()
            rec.dummy = True
            rec.state = 'cancelled'
    

    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        res = super(account_payment, self).post()
        for rec in self:
            if rec.dummy:
                rec.name = rec.name
        return res
    
            
    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        res= super(account_payment,self)._get_shared_move_line_vals(debit, credit, amount_currency, move_id, invoice_id=False)
#         if self.notes:
#             note=self.notes
#         else:
#             note ='' 
        res.update({ 'ref':self.notes or False})
        return res
        
        
    @api.model
    def default_description(self):
        desc = ''
        if self._context.get('active_model') and self._context.get('active_model') == 'account.invoice':
            if self._context.get('active_id'):
                invoice = self.env['account.invoice'].browse(self._context.get('active_id'))
                for lines in invoice.invoice_line_dates_ids:
                    desc += lines.name+','
                desc = desc[:-1]
#         else:
#             desc = False
        return desc
        

    def amount_to_text(self):
        for record in self:
            amount_untaxed = '%.3f' % self.amount
            list = str(amount_untaxed).split('.')
            first_part = False
            second_part = False
            if num2words(int(list[0])):
                first_part = num2words(int(list[0])).title()
            if num2words(int(list[1])):
                second_part = num2words(int(list[1])).title()
            amount_in_words = ' Bahrain Dinar '
            if first_part:
                amount_in_words =  str(first_part) + amount_in_words 
            else:
                amount_in_words =  'Zero' + amount_in_words 
            if second_part:
                if list[1] != '000':
                    amount_in_words = amount_in_words + ' and ' +str(list[1]) + ' Fils ' 
                #amount_in_words = ' ' + amount_in_words + ' and Fils ' + str(second_part) 
            self.amount_total_words=  amount_in_words
    
    amount_total_words = fields.Char('Amount in Words',compute='amount_to_text')
    charges = fields.Float('Charges')
    account_id = fields.Many2one('account.account','Account')
    notes = fields.Char('Notes',required=True, default=default_description)
    
    
    @api.model
    def default_module_id(self):
        '''This function return additional id for voucher'''
        module_id = False
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        
        if active_model and active_model == 'account.move':
            if active_id:
                invoice = self.env['account.move'].browse(active_id)
                if invoice.module_id:
                    module_id = invoice.module_id.id
                else:
                     module_id = False
        return module_id
    
    
    @api.model
    def default_building_id(self):
        '''This function return additional id for voucher'''
        building_id = False
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        
        if active_model and active_model == 'account.move':
            if active_id:
                invoice = self.env['account.move'].browse(active_id)
                if invoice.building_id:
                    building_id = invoice.building_id.id
                else:
                    building_id = False
        return building_id
    
    
    @api.model
    def default_comment(self):
        '''This function return addtional log for voucher'''
        
        module_id = False
        log = ''
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        
        if active_model and active_model == 'account.move':
            if active_id:
                invoice = self.env['account.move'].browse(active_id)
                if invoice.comment:
                    log = invoice.comment
                else:
                    log = False
        return log
    
    @api.model
    def default_check_date(self):
        '''This function return check date for customer payment voucher'''
        check_date = False
        
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        
        if active_model and active_model == 'account.move':
            if active_id:
                voucher = self.env['account.move'].browse(active_id)
                if voucher.check_date:
                    date = voucher.check_date
                else:
                    date = datetime.datetime.now()
        else:
            date = datetime.datetime.now()
        return date
    
    @api.onchange('building_id')
    def hide_units_modules(self):
        for all in self:
            if all.building_id:
                if all.building_id.building_type =='rent':
                    all.hide_field =False
                    all.hide_field2 =True
                else:
                    all.hide_field2 =False
                    all.hide_field =True
            else:
                all.hide_field =False
                all.hide_field2 =False
                
                
    hide_field = fields.Boolean('Hide',default =False,compute = 'hide_units_modules')
    hide_field2 = fields.Boolean('Hide',default =False,compute = 'hide_units_modules')
    building_id = fields.Many2one('zbbm.building', 'Building',default=default_building_id ,domain=[('state', '=', 'available')])
    module_id = fields.Many2one('zbbm.module', 'Flat/Office', default=default_module_id)
    logo = fields.Text('comment', default=default_comment)
    check_date = fields.Date('Check Date', default=default_check_date)
    note = fields.Text("Notes")
    
    
    def _get_move_vals(self, journal=None):
        res = super(account_payment,self)._get_move_vals(journal)
        res.update({
                    'building_id':self.building_id.id or False,
                    'module_id':self.module_id.id or False,
                    'unit_id':self.unit_id.id or False,
                    'ref':self.notes or False,
#DB                     'cheque_no':self.cheque_no or '',
#                     'cheque_date' : self.cheque_date or False,
#                     'cheque_bank_id':self.cheque_bank_id and self.cheque_bank_id.id or False,
            })
        return res
    
    
