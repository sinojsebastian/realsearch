# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2020 OpenERP S.A. (<http://openerp.com>).
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

from odoo import api, fields, models, _
from datetime import datetime, timedelta
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError,Warning
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')



class BankReconiliation(models.Model):
    _name ="bank.reconciliation"
    _description= "Bank Statement Reconcilation"
    _order="name desc"
    
    
    
    def select_all(self):
        if self.reconcileline_ids:
            debit_total = credit_total = difference_total = 0.00
            for line in self.reconcileline_ids:
                if line.state == 'unreconciled':
                    line.reconciled =True
                if line.reconciled:
                    if line.debit > 0.00 and not line.reconciled_done:
                        debit_total += line.debit 
                        self.debit -= line.debit
#                         self.closing_balance -= line.debit
                        line.reconciled_done = True
                    elif line.credit > 0.00 and not line.reconciled_done:
                        credit_total += line.credit 
                        self.credit -=line.credit
#                         self.closing_balance += line.credit
                        line.reconciled_done = True
            difference_total = self.closing_balance_stmt + self.debit - self.credit     
            self.difference = difference_total - self.closing_balance
        
#         return True
    
    def unselect_all(self):
        if self.reconcileline_ids:
            debit_total = credit_total = difference_total = 0.00
            for line in self.reconcileline_ids:
                if line.state == 'unreconciled' and line.reconciled ==True:
                    line.reconciled =False
                if not line.reconciled:
                    if line.debit > 0.00 and  line.reconciled_done:
                        debit_total += line.debit 
                        self.debit += line.debit
#                         self.closing_balance += line.debit
#                         self.difference += line.debit
                        line.reconciled_done = False
                    elif line.credit > 0.00 and  line.reconciled_done:
                        credit_total += line.credit
                        self.credit +=line.credit
#                         self.closing_balance -= line.credit
#                         self.difference -= line.credit
                        line.reconciled_done = False
                    
        difference_total = self.closing_balance_stmt + self.debit - self.credit    
        self.difference = difference_total - self.closing_balance           
                
        
#         return True
    
    
    @api.onchange('reconcileline_ids','reconcileline_ids.reconciled')
    def onchange_reconciled(self):
        if self.reconcileline_ids:
            credit_total = debit_total = 0.00
            for reconcile_line in self.reconcileline_ids:
                if reconcile_line.reconciled:
                    if reconcile_line.debit > 0.00 and not reconcile_line.reconciled_done:
                        self.debit -= reconcile_line.debit
#                         self.closing_balance -= reconcile_line.debit
                        debit_total = reconcile_line.debit
                        self.difference = self.difference - debit_total
                        reconcile_line.reconciled_done = True
                    elif reconcile_line.credit > 0.00 and not reconcile_line.reconciled_done:
                        self.credit -=reconcile_line.credit
                        credit_total =reconcile_line.credit  
                        self.difference = self.difference +  credit_total
#                         self.closing_balance += reconcile_line.credit
                        reconcile_line.reconciled_done = True
                else:
                    if reconcile_line.debit > 0.00 and  reconcile_line.reconciled_done:
                        self.debit += reconcile_line.debit
#                         self.closing_balance += reconcile_line.debit
                        self.difference += reconcile_line.debit
                        reconcile_line.reconciled_done = False
                    elif reconcile_line.credit > 0.00 and  reconcile_line.reconciled_done:
                        self.credit +=reconcile_line.credit
#                         self.closing_balance += reconcile_line.credit
                        self.difference -= reconcile_line.credit
                        reconcile_line.reconciled_done = False
                    
    
    @api.depends('reconcileline_ids','reconcileline_ids.credit','reconcileline_ids.debit','bank_account_id')
    def get_amount(self):
        ope_bal = balance_total = balance_total = 0.000
        clos_bal =0.000
        tot_dr =0.000
        tot_cr =0.000
        domain =[('account_id', '=', self.bank_account_id.id),('date', '<', self.from_date)]
        lines = self.env['account.move.line'].search(domain)
        ope_bal += sum([line.debit - line.credit for line in lines])
        tot_dr +=sum([drline.debit for drline in self.reconcileline_ids if drline.state == 'unreconciled'])
        tot_cr +=sum([crline.credit for crline in self.reconcileline_ids if crline.state == 'unreconciled'])
        self.opening_balance = ope_bal
        self.closing_balance = ope_bal+ tot_dr-tot_cr
        self.debit = tot_dr
        self.credit = tot_cr
        balance_total = self.closing_balance_stmt + self.debit - self.credit
        self.difference =balance_total - self.closing_balance
        
        
#     gl_balance += sum([line.debit - line.credit for line in lines])
    @api.model
    def create(self,vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('bank.reconiliation') or '/'
        return super(BankReconiliation, self).create(vals)
    
    def validate(self):
        payment_pool = self.env['account.payment'] 
        line_vals={}
        lines =[]
        if self.reconcileline_ids:
            linereconciled = False
            for line in self.reconcileline_ids:
                if line.reconciled and line.state == 'unreconciled':
#                     print line
#                     if line.state is 'unreconciled':
                    move_line_obj = line.move_line_id
                    line.rec_date =fields.date.today()
                    line_vals={
                        'state':'reconciled'
                        }
                    lines.append((1, line.id, line_vals))
                    self.write({
                        'state':'validated',
                        'reconcileline_ids':lines
                        })
#                         line.state ='reconciled'
                    move_line_obj.write({
                        'rec_date':line.rec_date,
                        'reconcilation_id':self.id
                        
                        })
                    if 'CUST.IN'or 'SUPP.OUT' in move_line_obj.name:
                        payments = payment_pool.search([('name', '=', move_line_obj.name)])
                        for payment in payments:
                            payment._get_move_reconciled()
                            payment.state = 'reconciled'
                            
                    linereconciled = True
#                 else:
            if not linereconciled:
                raise Warning(_("""no lines has been reconciled"""))
                        
        else:
            raise Warning(_("""no line to validate"""))
        balance_total = self.closing_balance_stmt + self.debit - self.credit
        self.difference =balance_total - self.closing_balance
        return True
    
    name =fields.Char('Bank reconilation No', readonly=True,copy=False)
    journal_id =fields.Many2one('account.journal',string="Journal")
    from_date =  fields.Date('Date From')
    to_date = fields.Date('Date To')
    state = fields.Selection([
            ('draft','Draft'),
            ('validated', 'Validated'),
             
        ], string='Status' ,default="draft")
    bank_account_id = fields.Many2one('account.account', 'Account')
    reconcileline_ids =fields.One2many('bank.reconciliation.line','reconcile_id','Bank reconciliation line')
#     line_ids = fields.One2many('bank.reconciliation.line', 'reconcileline_id', 'Bank Reconciliation Line')
    type = fields.Selection([('reconciled', 'Reconciled'),
                                          ('un_recon', 'To Reconcile'),
                                          ('all', 'All')], 'Show Only',default='un_recon')
    opening_balance =fields.Float("GL Balance",copy=False, digits='Account')
    opening_balance_stmt =fields.Float("Opening Balance",copy=False, digits='Account')
    closing_balance   = fields.Float("GL Closing Balance",copy=False, digits='Account')
    closing_balance_stmt   = fields.Float("BNK Balance",copy=False, digits='Account')
    debit = fields.Float("Debit",copy=False, digits='Account')
    credit = fields.Float("Credit",copy=False, digits='Account')
    difference = fields.Float("Difference",copy=False, digits='Account',readonly=False)

   
    
    @api.onchange('journal_id')
    def onchange_journal_id(self):
        for record in self:
            if  record.journal_id:
                record.bank_account_id = record.journal_id.default_debit_account_id.id
            else:
                record.bank_account_id =False

    def unlink(self):
        for i in self:
            if i.state !='draft':
                 raise UserError(_('Cannot delete record which are already validated.'))
#             else:
#                 super(BankReconiliation,self).unlink()
                 
        return super(BankReconiliation,self).unlink()       
             
             
             
    def update_record(self):    
        move_line_pool = self.env['account.move.line'] 
        payment_pool = self.env['account.payment'] 
        voucher_pool = self.env['account.move'] 
        move_line_obj =[]
        domain =[]
        for record in self:
            lines = []
            if record.bank_account_id:
                from_date = record.from_date
                to_date = record.to_date
                bank_account_id = record.bank_account_id.id
                for x in record.reconcileline_ids:
                    if x.id:
                        x.unlink()
                domain = [('account_id', '=', bank_account_id)]
                if  from_date:
                    domain.append(('date', '>=', from_date))
                if  to_date:
                    domain.append(('date', '<=', to_date))
#                 if record.journal_id:
#                     domain.append(('journal_id', '=', record.journal_id.id))
                move_line_ids = move_line_pool.search(domain)
                for move_line_obj in move_line_ids:
                    debit = 0.00
                    credit = 0.00  
                    file_no =check_no =''
                    reconciled =False
                    state='unreconciled'
                    payment_name =''
                    #checkno
                    file_no =move_line_obj.name

#                     voucher_domain = [('name', '=', file_no)]
                    voucher_domain =[('move_id','=',move_line_obj.move_id.id)]
                    
                    if move_line_obj.payment_id:
                        payment_name =move_line_obj.payment_id.name
                        check_no =move_line_obj.payment_id.cheque_no
#                     voucher_obj =voucher_pool.search(voucher_domain)
#                     
#                     if voucher_obj:
#                         check_no = ''
#                         payment_name =voucher_obj.number
                    
                    if not payment_name:
                        payment_name = move_line_obj.move_id.name   
                    
#                     if payment_name ='':
#                         payment_name =file_no
                                 
                    
                    if move_line_obj.amount_currency:
                        if move_line_obj.amount_currency < 0.00:
                            credit = move_line_obj.amount_currency * -1
                        else:
                            debit = move_line_obj.amount_currency
                    else:
                        debit = move_line_obj.debit or 0.00
                        credit = move_line_obj.credit or 0.00 
                        if move_line_obj.ref:
                            notes =move_line_obj.ref
                        else:
                            notes =move_line_obj.name
                            
                        if move_line_obj.rec_date:
                            rec_date = move_line_obj.rec_date
                            reconciled =True  
                            state='reconciled'
                    if state == 'unreconciled':           
                        vals = {
                            'reconcile_id': record.id,
                            'date': move_line_obj.date,
                            'reference': notes,
                            'move_id': move_line_obj.move_id.id,
                            'document_no':payment_name or '',
                            'move_line_id': move_line_obj.id,
                            'partner_id':move_line_obj.partner_id.id or False,
                            'rec_date': move_line_obj.rec_date,
                            'reconciled':reconciled or False,
                            'state':state,
                            'cheque_no': check_no or False,
                            'debit': move_line_obj.debit,
                            'credit': move_line_obj.credit,
                            }
                        lines.append((0, 0, vals))
                self.write({'reconcileline_ids': lines})
        if self.reconcileline_ids:
              self.get_amount()
        return True     
                    
class BankReconsiliationLine(models.Model):
    _name = 'bank.reconciliation.line'
    _description = 'Reconciliation Line'
    _order = 'date'
    
    
    date = fields.Date('Date')
    reconcile_id =fields.Many2one('bank.reconciliation','Reconcile Record')
#     recocileline_id = fields.Many2one('bank.reconciliation', 'Reconcilation Ref')

    move_id = fields.Many2one('account.move', 'Move')
    document_no =fields.Char('Document No')
    
    
    move_line_id = fields.Many2one('account.move.line', 'Move Line Ref')
    rec_date = fields.Date('Reconciliation Date')
    credit = fields.Float('Credit', digits='Account')
    debit = fields.Float('Debit', digits='Account')
    reference = fields.Char(string="Description")
    partner_id =fields.Many2one('res.partner','Partner')
    reconciled =fields.Boolean('Reconciled')
    reconciled_done = fields.Boolean('Reconciled',default = False)
    cheque_no =fields.Char('Cheque No')
    state   = fields.Selection([
            ('unreconciled','Unreconcile'),
            ('reconciled', 'Reconciled'),
             
        ], string='Status' ,default="unreconciled")
    instrument = fields.Date(string="Instrument Date", related='move_id.cheque_date',readonly=True)
    
