# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2020 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)
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


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"
    

    repartition_type = fields.Selection(string="Based On", selection_add=[('base', 'Base'), ('tax', 'of vat')], required=True, default='tax', help="Base on which the factor will be applied.")
    invoice_tax_id = fields.Many2one(string='Invoice VAT',comodel_name='account.tax', help="The tax set to apply this repartition on invoices. Mutually exclusive with refund_tax_id")
    refund_tax_id = fields.Many2one(string='Refund VAT',comodel_name='account.tax', help="The tax set to apply this repartition on refund invoices. Mutually exclusive with invoice_tax_id")
    tax_id = fields.Many2one(string='VAT',comodel_name='account.tax', compute='_compute_tax_id')


class AccountMove(models.Model):
    _inherit = 'account.move'

    cheque_no = fields.Char(string='Cheque No')
    cheque_date = fields.Date(string='Cheque Date')
    cheque_bank_id = fields.Many2one('res.bank', string='Cheque Bank')
    journal_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
    ], string='Type', related='journal_id.type')
    
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
      
    cheque_no = fields.Char(string='Cheque No',related='move_id.cheque_no',store=True,copy=False)
    cheque_date = fields.Date(string='Cheque Date',related='move_id.cheque_date',store=True,copy=False)
    cheque_bank_id = fields.Many2one('res.bank',string='Cheque Bank',related='move_id.cheque_bank_id',store=True,copy=False)
    journal_type = fields.Selection([
            ('sale', 'Sale'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
        ],string='Type',related='journal_id.type', store=True)
    

class account_payment(models.Model):
    _inherit = "account.payment"
    
          
    @api.depends('journal_id')
    def _check_is_bank(self):
        for rec in self:
            if rec.journal_id.type == 'bank':
                rec.is_bank = True
            else:
                rec.is_bank = False    
            
    
    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        jrnl_filters = self._compute_journal_domain_and_types()
        journal_types = jrnl_filters['journal_types']
        domain_on_types = [('type', 'in', list(journal_types))]
        if self.journal_id.type not in journal_types:
            self.journal_id = self.env['account.journal'].search(domain_on_types, limit=1)
        return {'domain': {'journal_id': jrnl_filters['domain'] + domain_on_types}}


    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash', 'post_dated_chq'))])
    journal_type = fields.Selection([('sale', 'Sale'), ('sale_refund', 'Sale Refund'),
                                     ('purchase', 'Purchase'),
                                     ('purchase_refund', 'Purchase Refund'),
                                     ('cash', 'Cash'),
                                     ('bank', 'Bank and Cheque'),
                                     ('general', 'General'),
                                     ('situation', 'Opening/Closing Situation'),
                                     ('post_dated_chq', 'Post Dated CHQ')], string='Type',
                                    help="Select 'Sale' for customer invoices journals."
                                    " Select 'Purchase' for supplier invoices journals."
                                    " Select 'Cash' or 'Bank' for journals that are used in customer or supplier payments."
                                    " Select 'General' for miscellaneous operations journals."
                                    " Select 'Opening/Closing Situation' for entries generated for new fiscal years.")
    cheque_no = fields.Char(string='Cheque No',copy=False)
    cheque_date = fields.Date(string='Cheque Date',copy=False)
    cheque_bank_id = fields.Many2one('res.bank', string='Cheque Bank',copy=False)
    is_bank = fields.Boolean(compute='_check_is_bank')   
    
    
    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(account_payment, self)._onchange_journal()
        if self.journal_id:
            self.journal_type = self.journal_id.type
        return res


    def _get_move_vals(self, journal=None):
        res = super(account_payment, self)._get_move_vals(journal)
        res.update({
            'cheque_no': self.cheque_no or '',
            'cheque_date': self.cheque_date or False,
            'cheque_bank_id': self.cheque_bank_id and self.cheque_bank_id.id or False,
        })
        
        
        
        return res
    
    
class payment_register(models.TransientModel):
    _inherit = 'account.payment.register'
    
    
    @api.depends('journal_id', 'journal_id.type')
    def compute_journal_type(self):
        for rec in self:
            rec.journal_type = rec.journal_id and rec.journal_id.type or False
     
     
            
    cheque_no = fields.Char(string='Cheque No',copy=False)
    cheque_date = fields.Date(string='Cheque Date',copy=False)
    cheque_bank_id = fields.Many2one('res.bank',string='Cheque Bank',copy=False)
    journal_type = fields.Selection([
                                    ('sale', 'Sale'),
                                    ('purchase', 'Purchase'),
                                    ('cash', 'Cash'),
                                    ('bank', 'Bank'),
                                    ('general', 'Miscellaneous')],
                                    string='Type',
                                    compute='compute_journal_type', store=True)   



class AccountJournal(models.Model):
    _inherit = ['account.journal']
    
    type = fields.Selection(selection_add=[('sale_refund','Sale Refund'), 
                            ('purchase_refund','Purchase Refund'),
                            ('situation', 'Opening/Closing Situation'), 
                            ('post_dated_chq', 'Post Dated CHQ')], string='Type',
                                help="Select 'Sale' for customer invoices journals."\
                                " Select 'Purchase' for supplier invoices journals."\
                                " Select 'Cash' or 'Bank' for journals that are used in customer or supplier payments."\
                                " Select 'General' for miscellaneous operations journals."\
                                " Select 'Opening/Closing Situation' for entries generated for new fiscal years.")
    
 