# -*- encoding: utf-8 -*-
# Copyright Knacktechs SA

import json
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.exceptions import UserError, ValidationError,Warning

from odoo.tools import float_compare, float_round, float_repr

from pprint import pprint
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')

                    
            
class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    method_type = fields.Selection([('advance', 'Advance Payment'),('adjustment', 'Payment Adjustment')], 'Method of Payment', default='advance', copy=True)
    payment_line_ids=fields.One2many('account.payment.line','advance_id', string="Invoice Adjustment", copy=False)
    advance_expense_ids=fields.One2many('advance.expense.line','payment_id', string="Advance Expense Entries", copy=False)
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {}, partner_id=False,amount=0)
        return super(AccountPayment, self).copy(default=default)
#    to check that the total of the allocation should match with the actual amount of payment form in case of adjustment pay creation
    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        each_allocate=0.0
        amount=0.0
        
        if vals and vals.get('method_type')=='adjustment':
            if vals.get('payment_line_ids', False):
                for each in vals.get('payment_line_ids'):
                    if each[2] and each[2].get('allocation',False):
                        if vals.get('payment_advise'):
                            if each[2].get('debit') > 0.000:
                                each_allocate+=each[2].get('allocation')
                            else:
                                each_allocate +=(-each[2].get('allocation')) if each[2].get('allocation') > 0.00 else each[2].get('allocation')
                        else:
                            if vals.get('payment_type') == 'outbound':
                                if each[2].get('debit') > 0.000:
                                    each_allocate+=(-each[2].get('allocation')) if each[2].get('allocation') > 0.00 else each[2].get('allocation')
                                else:
                                    each_allocate +=each[2].get('allocation')
            if vals.get('amount', 0.0):   
                amount=vals.get('amount')
            
            if not vals.get('payment_advise'): 
                if float_round(each_allocate, 3) != float_round(amount, 3):
                    print('===========================',float_round(each_allocate, 3))
                    print('===========================',float_round(amount, 3))
                    raise UserError(_('The Payment Amount does not match with total allocated amount'))
        return res

    def write(self, vals):
        each_allocate = 0.0
        amount = 0.0
        payment=super(AccountPayment, self).write(vals)
        for rec in self:
            if rec.method_type== 'adjustment':
                if rec.payment_line_ids:
                    for each in rec.payment_line_ids:
                        if each.allocation:
                            if rec.payment_advise:
                                if each.debit>0.00:
                                    each_allocate += each.allocation
                                else:
                                    each_allocate +=(-each.allocation) if each.allocation > 0.000 else each.allocation
                            else:
                                if rec.payment_type == 'outbound':
                                    if each.credit > 0.00:
                                        each_allocate += each.allocation
                                    elif each.debit > 0.00:
                                        each_allocate -= each.allocation
                if rec.amount:
                    amount = rec.amount
                if not rec.payment_advise:
                    if float_round(each_allocate, 3) != float_round(amount, 3):
                        print('===========================',float_round(each_allocate, 3))
                        print('===========================',float_round(amount, 3))
                        raise UserError(_('The Payment Amount does not match with total allocated amount'))
        return payment
    

    def _prepare_payment_moves(self):
        ''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
        to the 'create' method.
 
        Example 1: outbound with write-off:
 
        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |   900.0   |
        RECEIVABLE          |           |   1000.0
        WRITE-OFF ACCOUNT   |   100.0   |
 
        Example 2: internal transfer from BANK to CASH:
 
        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |           |   1000.0
        TRANSFER            |   1000.0  |
        CASH                |   1000.0  |
        TRANSFER            |           |   1000.0
 
        :return: A list of Python dictionary to be passed to env['account.move'].create.
        '''
        all_move_vals = []
        for payment in self:
            company_currency = payment.company_id.currency_id
            move_names = payment.move_name.split(payment._get_move_name_transfer_separator()) if payment.move_name else None
 
            # Compute amounts.
            write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
            if payment.payment_type in ('outbound', 'transfer'):
                counterpart_amount = payment.amount
                liquidity_line_account = payment.journal_id.default_debit_account_id
            else:
                counterpart_amount = -payment.amount
                liquidity_line_account = payment.journal_id.default_credit_account_id
 
            # Manage currency.
            if payment.currency_id == company_currency:
                # Single-currency.
                balance = counterpart_amount
                write_off_balance = write_off_amount
                counterpart_amount = write_off_amount = 0.0
                currency_id = False
            else:
                # Multi-currencies.
                balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id, payment.payment_date)
                write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id, payment.payment_date)
                currency_id = payment.currency_id.id
 
            # Manage custom currency on journal for liquidity line.
            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                # Custom currency on journal.
                if payment.journal_id.currency_id == company_currency:
                    # Single-currency
                    liquidity_line_currency_id = False
                else:
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
            else:
                # Use the payment currency.
                liquidity_line_currency_id = currency_id
                liquidity_amount = counterpart_amount
 
            # Compute 'name' to be used in receivable/payable line.
            rec_pay_line_name = ''
            if payment.payment_type == 'transfer':
                rec_pay_line_name = payment.name
            else:
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Customer Payment")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Customer Credit Note")
                elif payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Vendor Credit Note")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Vendor Payment")
                if payment.invoice_ids:
                    rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))
 
            # Compute 'name' to be used in liquidity line.
            if payment.payment_type == 'transfer':
                liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
            else:
                liquidity_line_name = payment.name
 
            # ==== 'inbound' / 'outbound' ====
            module_id = False
            building_id = False
            if payment.building_id:
                building_id = payment.building_id.id
            if payment.module_id:
                module_id = payment.module_id.id
            
            move_vals = {
                'date': payment.payment_date,
                'ref': payment.communication,
                'journal_id': payment.journal_id.id,
                'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                'partner_id': payment.partner_id.id,
                'cheque_no':payment.cheque_no,
                'module_id':module_id,
                'building_id':building_id,
                'cheque_date':payment.cheque_date,
                'cheque_bank_id':payment.cheque_bank_id.id,
                'line_ids': [
                    # Receivable / Payable / Transfer line.
                    (0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                        'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.destination_account_id.id,
                        'payment_id': payment.id,
                    }),
                    # Liquidity line.
                    (0, 0, {
                        'name': liquidity_line_name,
                        'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                        'currency_id': liquidity_line_currency_id,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': liquidity_line_account.id,
                        'payment_id': payment.id,
                    }),
                ],
            }
            if write_off_balance:
                # Write-off line.
                move_vals['line_ids'].append((0, 0, {
                    'name': payment.writeoff_label,
                    'amount_currency': -write_off_amount,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'date_maturity': payment.payment_date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': payment.writeoff_account_id.id,
                    'payment_id': payment.id,
                }))
 
            if move_names:
                move_vals['name'] = move_names[0]
 
            all_move_vals.append(move_vals)
 
            # ==== 'transfer' ====
            if payment.payment_type == 'transfer':
                journal = payment.destination_journal_id
 
                # Manage custom currency on journal for liquidity line.
                if journal.currency_id and payment.currency_id != journal.currency_id:
                    # Custom currency on journal.
                    liquidity_line_currency_id = journal.currency_id.id
                    transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id, payment.payment_date)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    transfer_amount = counterpart_amount
 
                transfer_move_vals = {
                    'date': payment.payment_date,
                    'ref': payment.communication,
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.destination_journal_id.id,
                    'cheque_no':payment.cheque_no,
                    'cheque_date':payment.cheque_date,
                    'module_id':module_id,
                    'building_id':building_id,
                    'cheque_bank_id':payment.cheque_bank_id.id,
                    'line_ids': [
                        # Transfer debit line.
                        (0, 0, {
                            'name': payment.name,
                            'amount_currency': -counterpart_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.company_id.transfer_account_id.id,
                            'payment_id': payment.id,
                        }),
                        # Liquidity credit line.
                        (0, 0, {
                            'name': _('Transfer from %s') % payment.journal_id.name,
                            'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.destination_journal_id.default_credit_account_id.id,
                            'payment_id': payment.id,
                        }),
                    ],
                }
 
                if move_names and len(move_names) == 2:
                    transfer_move_vals['name'] = move_names[1]
 
                all_move_vals.append(transfer_move_vals)
        return all_move_vals
    
    
    
    def _get_move_vals(self,journal=None):
        """ Return dict to create the payment move
        """
        
        journal =  self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        
        name = journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
        moves = {
            'name': name,
            'date': self.payment_date,
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'state':'draft'
           
        }
        return moves

        # name = False
        # print('=========================move_name',self.move_name)
        # if not self.move_name:
        #     names = self.move_name.split(self._get_move_name_transfer_separator())
        #     print('======================name',names)
        #     if self.payment_type == 'transfer':
        #         if journal == self.destination_journal_id and len(names) == 2:
        #             name = names[1]
        #         elif journal == self.destination_journal_id and len(names) != 2:
        #             # We are probably transforming a classical payment into a transfer
        #             name = False
        #         else:
        #             name = names[0]
        #     else:
        #         name = names[0]

    
    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        print('==================_get_shared_move_line_vals',credit,debit)
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        #Write line corresponding to invoice payment
        if self.method_type=='adjustment' and debit>0.0 and amount_currency==False and self.partner_type=='customer':
            debit=0.0
            for each in self.payment_line_ids:
                if each.allocation>0.0:
                    debit+=each.allocation
        elif self.method_type=='adjustment' and credit>0.0 and amount_currency==False and self.partner_type=='supplier':
            credit=0.0
            for each in self.payment_line_ids:
                if each.allocation>0.0:
                    credit+=each.allocation
        return {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
#             'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            'payment_id': self.id,
        }
     
     
     
     
    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.state == 'posted':
                        name += inv.name + ', '
                name = name[:len(name)-2]
        return {
            'name': name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }
        
        
    def payment_move_line(self,move,amount_currency):
        '''
        Counter Payment Move Line for payment move
        '''
        aml_obj = self.env['account.move.line']
        if self.payment_type == 'inbound':
                debit_amount = self.amount
                credit_amount = 0.00
        else:
            debit_amount = 0.00
            credit_amount = self.amount
        lines = {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
#             'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move.id,
            'debit': debit_amount,
            'credit': credit_amount,
            'amount_currency': amount_currency or False,
            'payment_id': self.id,
            'account_id':self.journal_id.default_debit_account_id.id
        }
        return lines
    
    def get_counter_line(self,amount,move,inv):
        '''
        Counter Payment Move Line for payment move
        '''
        aml_obj = self.env['account.move.line']
        if self.payment_type == 'inbound':
                debit_amount = amount
                credit_amount = 0.00
        else:
            debit_amount = 0.00
            credit_amount = amount
        lines = {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
#             'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move,
            'debit': debit_amount,
            'credit': credit_amount,
#             'amount_currency': amount_currency or False,
            'payment_id': self.id,
            'account_id':self.journal_id.default_debit_account_id.id,
            'credit':credit_amount,
            'debit' : debit_amount
        }
        return lines
        
     
    def get_posted(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))


            #To be reviewed -pv
            # if rec.payment_type in ('inbound', 'outbound'):
            #     # ==== 'inbound' / 'outbound' ====
            #     if rec.invoice_ids:
            #         (moves[0] + rec.invoice_ids).line_ids \
            #             .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id and not (line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label))\
            #             .reconcile()
            # elif rec.payment_type == 'transfer':
            #     # ==== 'transfer' ====
            #     moves.mapped('line_ids')\
            #         .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
            #         .reconcile()
        return True
    
    
    
    def post(self):
        for order in self:
            all_lines = []
            if order.method_type =='adjustment':
                invoice_currency = False
                aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
                if order.invoice_ids and all([x.currency_id == order.invoice_ids[0].currency_id for x in order.invoice_ids]):
                #if all the invoices selected share the same currency, record the paiement in that currency too
                    invoice_currency = order.invoice_ids[0].currency_id
                debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(order.amount, order.currency_id, order.company_id.currency_id, invoice_currency)
                #Write line corresponding to invoice payment
                if order.payment_advise or order.payment_type == 'outbound':
                    res = super(AccountPayment, order).post() 
                    line_reconcile_id = order.move_line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                    for pl in order.payment_line_ids:
                        if pl.allocation > 0 :
                            all_lines.append({
                                                'id' : pl.move_line_id.id,
                                                'debit' : pl.move_line_id.debit, 
                                                'credit' : pl.move_line_id.credit, 
                                                'allocation' : pl.allocation, 
                                                'remaining' : pl.allocation, 
                                                'note' : pl.move_line_id.name,
                                                'payment_line_id': pl.id
                                                })
                    for adv_exp_line in self.advance_expense_ids:
                        advance_entry_id = adv_exp_line._create_advance_expense_journal_entry()
                        for adv_line in advance_entry_id.line_ids:
                            if adv_line.debit:
                                all_lines.append({
                                                'id' : adv_line.id,
                                                'debit' : adv_line.debit, 
                                                'credit' : adv_line.credit, 
                                                'allocation' : adv_exp_line.amount, 
                                                'remaining' : adv_exp_line.amount, 
                                                'note' : adv_exp_line.name,
                                                'payment_line_id': adv_exp_line.id
                                                })
                    reconcile_records =[] 
                    debit_lines = []
                    credit_lines = []
                    cr_dict = {}
                    
                    for line in all_lines:
                        if line['allocation'] > 0:
                            if line['debit'] > 0:
                                debit_lines.append(line)
                            else:
                                cr_dict.update({line['id']:line['allocation']})
                                credit_lines.append(line)
                    
                    while (debit_lines and credit_lines):
                        dr = debit_lines.pop()
                        cr = credit_lines.pop()
                        if dr['remaining'] == cr['remaining']:
                            amount = dr['remaining']
                            cr.update({'remaining' : 0})
                            dr.update({'remaining' : 0})
                            reconcile_records.append({
                                'cr_id' : cr,
                                'dr_id' : dr,
                                'amount' : amount
                                })

                        elif dr['remaining'] > cr['remaining']:       
                            amount = cr['remaining'] 
                            cr.update({'remaining' : 0})
                            dr.update({'remaining' : dr['remaining'] - amount})
                            reconcile_records.append({
                                'cr_id' : cr,
                                'dr_id' : dr,
                                'amount' : amount
                                })
                            debit_lines.append(dr)
                            
                        else:       
                            amount = dr['remaining'] 
                            cr.update({'remaining' : cr['remaining'] - dr['remaining']})
                            dr.update({'remaining' : 0})
                            reconcile_records.append({
                                'cr_id' : cr,
                                'dr_id' : dr,
                                'amount' : amount
                                })
                            credit_lines.append(cr)
                    amt = 0
                    partial_val_list = []
                    
                    for x in reconcile_records:
                        for k,v in x.items():
                            if k == 'cr_id':
                                if cr_dict.get(v['id']):
                                    if v['remaining'] == 0:
                                        cr_dict.pop(v['id'])
                                    else:
                                        cr_dict[v['id']] = v['remaining']
                            elif k == 'amount':
                                amt += v
                            else:
                                partial_val_list.append({'debit_move_id': v['id'], 'credit_move_id': x['cr_id']['id'], 'amount': x['amount']})
                    
                    if len(cr_dict) > 0 :
                        for m,a in cr_dict.items():
                            partial_val_list.append({'debit_move_id': line_reconcile_id.id, 'credit_move_id': m, 'amount': a})
                    
                    reconcile_dict = {}
                    final_list = []
                    for vals in partial_val_list:
                        vals.update({'reconcilied_payment_id':self.id})
                        partial_id = self.env['account.partial.reconcile'].create(vals)
                    
                
                else:
                    #Partial Matching for Payment adjustment missing Partial Reconciliation.
                    for each in self.payment_line_ids:
                        if each.allocation>0.0:
                            move = self.env['account.move'].create(order._get_move_vals())
                            inv_id=each.inv_id
                            if inv_id.type == 'out_invoice':
                                credit=each.allocation
                            else:
                                if inv_id.type == 'entry' and order.payment_type == 'inbound':
                                    credit=each.allocation
                                else:
                                    credit=0.0
                            if inv_id.type == 'in_invoice':
                                debit=each.allocation
                            else:
                                if inv_id.type == 'entry' and order.payment_type == 'outbound':
                                    debit=each.allocation
                                else:
                                    debit=0.0
                                
                            counterpart_aml_dict = order._get_shared_move_line_vals(debit, credit, amount_currency, move.id, inv_id)
                            counterpart_aml_dict.update(order._get_counterpart_move_line_vals(each.inv_id))
                            counterpart_aml_dict.update({'currency_id': currency_id})
                            print('========================counterpart_aml_dict',counterpart_aml_dict)
    #PV                         counterpart_aml.payment_id.write({'invoice_ids': [(4, each.inv_id.id, None)]})
                            counterpart_aml_dict2 = order.get_counter_line(each.allocation, move.id, inv_id)
                            counterpart_aml_dict2.update({'account_id':order.journal_id.default_debit_account_id.id})
                            print('========================counterpart_aml_dict2',counterpart_aml_dict2)
                            move.write({'line_ids':[(0,0,counterpart_aml_dict),(0,0,counterpart_aml_dict2)]})
                            print('========================lines',move.line_ids)
    #                         order.payment_move_line(move,amount_currency)
                            move.post()
                            pay_term_line_ids = move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                            each.inv_id.register_payment(pay_term_line_ids)
                            move_name = order._get_move_name_transfer_separator().join(move.mapped('name'))
                    # res = super(AccountPayment, order).post()
                    self.get_posted()
                    order.write({'move_name': move_name,'state':'posted'})
                
            
            else:
                res = super(AccountPayment, order).post()              
        return True                   

    
    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        line_vals = []
        payment = super(AccountPayment, self)._onchange_payment_type()
        if self.payment_type=='transfer':
            self.method_type='advance'
            self.payment_line_ids = line_vals
        return payment
    
    
    def _load_payment_lines(self):
        payment_line_obj=self.env['account.payment.line']
        line_vals = []
        due_date = ''
        move_line_ids = ''
        inv_obj = ''
        if self.method_type =='adjustment' and self.partner_id:
            if self.payment_type == 'outbound':
                if self.module_id:
                    move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel']),('move_id.module_id','=',self.module_id.id)])
                    inv_obj=self.env['account.move'].search([('type','in',('in_invoice','in_receipt')),('partner_id','=',self.partner_id.id),('state','not in',['draft','cancel']), ('invoice_payment_state', '!=', 'paid'),('module_id','=',self.module_id.id)])
                elif self.unit_id:
                    move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel']),('move_id.unit_id','=',self.unit_id.id)])
                    inv_obj=self.env['account.move'].search([('type','in',('in_invoice','in_receipt')),('partner_id','=',self.partner_id.id),('state','not in',['draft','cancel']), ('invoice_payment_state', '!=', 'paid'),('unit_id','=',self.unit_id.id)])
                elif self.building_id:
                    move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel']),('move_id.module_id.building_id','=',self.building_id.id)])
                    inv_obj=self.env['account.move'].search([('type','in',('in_invoice','in_receipt')),('partner_id','=',self.partner_id.id),('state','not in',['draft','cancel']), ('invoice_payment_state', '!=', 'paid'),('building_id','=',self.building_id.id)])
                else:
                    move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel'])])
                    inv_obj=self.env['account.move'].search([('type','in',('in_invoice','in_receipt')),('partner_id','=',self.partner_id.id),('state','not in',['draft','cancel']), ('invoice_payment_state', '!=', 'paid')])
            else:
                if self.payment_type == 'inbound':
                    if self.module_id:
                        move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel']),('move_id.module_id','=',self.module_id.id)])
                        inv_obj=self.env['account.move'].search([('type','in',('out_invoice','out_receipt')),('partner_id','=',self.partner_id.id),('state','not in',['draft','cancel']), ('invoice_payment_state', '!=', 'paid'),('module_id','=',self.module_id.id)])
                    elif self.unit_id:
                        move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel']),('move_id.unit_id','=',self.unit_id.id)])
                        inv_obj=self.env['account.move'].search([('type','in',('out_invoice','out_receipt')),('partner_id','=',self.partner_id.id),('state','not in',['draft','cancel']), ('invoice_payment_state', '!=', 'paid'),('unit_id','=',self.unit_id.id)])
                    elif self.building_id:
                        move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel']),('move_id.module_id.building_id','=',self.building_id.id)])
                        inv_obj=self.env['account.move'].search([('type','in',('out_invoice','out_receipt')),('partner_id','=',self.partner_id.id),('state','not in',['draft','cancel']), ('invoice_payment_state', '!=', 'paid'),('building_id','=',self.building_id.id)])
                    else:
                        move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel'])])
                        inv_obj=self.env['account.move'].search([('type','in',('out_invoice','out_receipt')),('partner_id','=',self.partner_id.id),('state','not in',['draft','cancel']), ('invoice_payment_state', '!=', 'paid')])
        if self.payment_advise:
            already_processed = []
            if move_line_ids:
                move_line_list = move_line_ids.ids
                if self.module_id and self.lease_id:
                    move_line_tenant_payment_ids = self.env['account.move.line'].search([('move_id.type','in',['entry']),('partner_id','=',self.lease_id.tenant_id.id),('move_id.state','not in',['draft','cancel']),('move_id.module_id','=',self.module_id.id)])
                    if move_line_tenant_payment_ids:
                        for payment in move_line_tenant_payment_ids:
                            if payment.payment_id and payment.payment_id.payment_advise:
                                move_line_list.append(payment.id)
                move_line_ids = self.env['account.move.line'].browse(move_line_list)
                for line in move_line_ids:
                    reconciled_lines = line._reconciled_lines()
                    for lines in set(reconciled_lines):
                        if lines not in already_processed:
                            already_processed.append(lines)
                            match_line = self.env['account.move.line'].browse(lines)
                            if not match_line.full_reconcile_id and match_line.account_id.user_type_id.type == 'receivable':
                                #if not (match_line.matched_debit_ids or match_line.matched_credit_ids):
                                if match_line.reconciled == False:
                                    
                                    balance_amount = 0
                                    if match_line.move_id.type == 'entry':
                                        partial_entry = self.env['account.partial.reconcile'].search([('credit_move_id','=',match_line.id)])
                                        if len(partial_entry) > 0:                                                
                                            line_amount = match_line.credit if match_line.credit > 0 else match_line.debit
                                            for entry in partial_entry:
                                                balance_amount = balance_amount+entry.amount
                                            balance_amount = line_amount - balance_amount
                                        else:
                                            balance_amount = match_line.credit if match_line.credit > 0 else match_line.debit
                                    else:
                                        balance_amount = match_line.move_id.amount_residual if match_line.move_id.amount_residual else 0.00
                                    
                                    if balance_amount > 0:    
                                        open_invoice_lines={
                                            'inv_id':match_line.move_id.id,
                                            'move_line_id':match_line.id,
                                            'ref_num':match_line.move_id.ref,
                                            'acc_id':match_line.account_id.id,
                                            'original_amount':match_line.move_id.amount_total,
                                            'due_date':match_line.move_id.invoice_date_due, #it will change the date format in d/m/y
                                            'original_date':match_line.move_id.invoice_date,
                                            'currency_id':match_line.move_id.currency_id.id,
                                            'balance_amount':balance_amount,
                                            'full_reconcile':False if match_line.debit > 0  else True,
                                            'allocation': balance_amount if match_line.credit > 0 else 0,
                                            'debit': match_line.debit,
                                            'credit':match_line.credit,
                                            }
                                        line_vals.append((0,0,open_invoice_lines))
            else:
                line_vals=[] 
            
                
        else:
            if move_line_ids:
                for each in move_line_ids:
                    if each.account_id.user_type_id.type in ('receivable', 'payable') and not each.payment_id:
                        line_reconcile_id = each
                        allocated_amount=0.0
                        if each.move_id.type == 'entry':
                            acc_date = each.move_id.date
                            partial_id = self.env['account.partial.reconcile'].search(['|',('credit_move_id.move_id','=',each.move_id.id),('debit_move_id.move_id','=',each.move_id.id)])
                            if len(partial_id) > 0:   
                                partial_amount = 0                                             
                                for entry in partial_id:
                                    partial_amount += entry.amount
                                balance_amount = each.move_id.amount_total - partial_amount
                            
                            else:
                                balance_amount = each.move_id.amount_total - partial_id.amount
                        else:
                            acc_date = each.move_id.invoice_date
                            balance_amount = each.move_id.amount_residual
                            # acc_date=self.env['account.move'].search([('type','=','entry'),('name','=',each.name)])
                        pay_line_id=payment_line_obj.search([('inv_id','=',each.move_id.id)])
                        if pay_line_id:
                            allocated_amount=sum(line.allocation for line in pay_line_id)
                        
                        # for date_due in acc_date:
                        #     due_date=date_due.date
                        if balance_amount:
                            open_invoice_lines={
                            'inv_id':each.move_id.id,
                            'move_line_id':line_reconcile_id.id if line_reconcile_id else False,
                            'ref_num':each.move_id.ref,
                            'acc_id':each.partner_id.property_account_receivable_id.id if self.payment_type == 'inbound' else each.partner_id.property_account_payable_id.id ,
                            'original_amount':each.move_id.amount_total,
                            'due_date':each.move_id.invoice_date_due, #it will change the date format in d/m/y
                            'original_date':acc_date,
                            'currency_id':each.currency_id.id,
                            'balance_amount':balance_amount if balance_amount else 0.00,
                            'full_reconcile':False,
                            'allocation':0.00,
                            'debit': each.debit,
                            'credit':each.credit,
                            }
                            line_vals.append((0,0,open_invoice_lines))
            else:
                line_vals=[] 
        return line_vals
        
    
    @api.onchange('partner_id','method_type')
    def _onchange_partner_id(self):
        if self.invoice_ids and self.invoice_ids[0].invoice_partner_bank_id:
            self.partner_bank_account_id = self.invoice_ids[0].invoice_partner_bank_id
        elif self.partner_id != self.partner_bank_account_id.partner_id:
            # This condition ensures we use the default value provided into
            # context for partner_bank_account_id properly when provided with a
            # default partner_id. Without it, the onchange recomputes the bank account
            # uselessly and might assign a different value to it.
            if self.partner_id and len(self.partner_id.bank_ids) > 0:
                self.partner_bank_account_id = self.partner_id.bank_ids[0]
            elif self.partner_id and len(self.partner_id.commercial_partner_id.bank_ids) > 0:
                self.partner_bank_account_id = self.partner_id.commercial_partner_id.bank_ids[0]
            else:
                self.partner_bank_account_id = False
        
            
        payment_lines = self._load_payment_lines()
        self.payment_line_ids = [(6, 0, [])]
        self.payment_line_ids = payment_lines
            
        return {'domain': {'partner_bank_account_id': [('partner_id', 'in', [self.partner_id.id, self.partner_id.commercial_partner_id.id])]}}      


    def cancel(self):
        payment=super(AccountPayment,self).cancel()
        return payment
    
    
    @api.onchange('payment_line_ids')
    def _onchange_payment_line_ids(self):

        for order in self:
            if order.method_type == 'adjustment':
                debit_allocation_total = 0.000
                credit_total = 0.000
                total = 0.000
                if order.payment_line_ids:
                    for line in order.payment_line_ids:
                        if line.move_line_id:
                            allocation = line.allocation
                            if line.credit > 0:
                                total += allocation
                             #PV for the negative payment in first PA    
                            else:
                                total += allocation
                        if line.debit >0.000:
                            debit_allocation_total += line.allocation
                        else:
                            credit_total += line.allocation
                if order.payment_advise or order.payment_type == 'outbound':
                        print('============================total',total)
                        if total < 0:
                            order.amount = credit_total
                        else:
                            order.amount = credit_total - debit_allocation_total
                        #Expense deduction from Payment Allocated Amount
                        expense = 0        
                        for exp_line in order.advance_expense_ids:
                            expense += exp_line.amount
                        if expense > 0:
                           order.amount = order.amount - expense 
                else:
                    if total < 0:
                        order.amount = debit_allocation_total
                    else:
                        order.amount = debit_allocation_total - credit_total
                
                
            
                    
    @api.onchange('advance_expense_ids')                
    def _onchange_advance_expense_ids(self):
        '''Onchange for the Advance Expense entries'''
        for order in self:
            if order.payment_advise:
                order._onchange_payment_line_ids()
                

AccountPayment()


class AccountPaymentLine(models.Model):
    _name='account.payment.line'
    
    
    advance_id=fields.Many2one('account.payment', string="Payment Line", copy=True)
    inv_id=fields.Many2one('account.move',string="Invoice Numbers")
    acc_id= fields.Many2one('account.account',string="Account")
    original_date=fields.Date('Date')
    due_date=fields.Date('Due Date')
    original_amount=fields.Float('Original Amount',digits='Product Price')
    balance_amount=fields.Float('Balance Amount',digits='Product Price')
    full_reconcile=fields.Boolean('Full Reconcile')
    allocation=fields.Float('Allocation')
    ref_num = fields.Char(string="Reference No.")
    currency_id = fields.Many2one('res.currency', string='Currency')
    debit = fields.Float('Debit',digits='Product Price')
    credit = fields.Float('Credit',digits='Product Price')
    move_line_id = fields.Many2one('account.move.line',string="Move Line")
    building_module_ref = fields.Char(compute='_get_building_flat_ref', string='Unit')
    building_module_ref_copy = fields.Char(string='Unit')
    
    @api.depends('inv_id')
    def _get_building_flat_ref(self):
        for lines in self:
            ref = ''
            if lines.inv_id and lines.inv_id.building_id and lines.inv_id.module_id:
                ref = lines.inv_id.building_id.code+' '+lines.inv_id.module_id.name 
            elif lines.inv_id and lines.inv_id.building_id and not lines.inv_id.module_id:
                ref = lines.inv_id.building_id.code
            elif lines.inv_id and not lines.inv_id.building_id and lines.inv_id.module_id:
                ref = lines.inv_id.module_id.name
                
            lines.building_module_ref = ref
            lines.building_module_ref_copy = lines.building_module_ref
    
    
    @api.onchange('allocation')
    def _onchange_allocation(self):
        if not self.advance_id.payment_advise:
            print('=========================allocation',self.allocation,self.balance_amount)
            if self.allocation>self.balance_amount:
                warning = {
                    'title': _("Warning!"),
                    'message': "Allocation Amount Cannot Exceed the Balance Amount!"
                    }
                self.allocation = 0.00
                return {'warning': warning}


#when fully reconciled checked add remaining balance amt to allocated amt
    @api.onchange('full_reconcile')
    def check_full_reconcilation(self):
        if self.full_reconcile==True:
            if self.advance_id.payment_advise:
                if self.debit or self.credit:
                    self.allocation = self.balance_amount # PV -(self.debit -self.credit) if self.debit -self.credit < 0.000 else (self.debit -self.credit)
            else:
                self.allocation=self.balance_amount
        else:
            self.allocation=0.00
            
AccountPaymentLine()    


class AdvanceExpenseLine(models.Model):

    _name='advance.expense.line'
    _description = 'Advance Expense Entries'
    
    name = fields.Char(string='Description')
    amount = fields.Float('Amount', digits = (12,3))
    payment_id = fields.Many2one('account.payment', string="Payment", copy=True)
    move_id = fields.Many2one('account.move', string="Account Move")
    
    def _create_advance_expense_journal_entry(self):
        params = self.env['ir.config_parameter'].sudo() 
        # advance_expense_account_id = params.get_param('zb_bf_custom.advance_expense_account_id') or False
        advance_expense_journal_id = params.get_param('zb_bf_custom.advance_expense_journal_id') or False
        # if not advance_expense_account_id:
        #     raise Warning(_('Please Configure Advance Expense Account in Account Settings'))
        if not advance_expense_journal_id:
            raise Warning(_('Please Configure Advance Expense Journal in Account Settings'))
        debit_val =  {
            'account_id':self.payment_id.partner_id.property_account_receivable_id.id,
            'analytic_account_id':False,
            'partner_id':self.payment_id.partner_id.id,
            'name':'%s on %s'%(self.name,self.payment_id.name),
            'debit':self.amount,
            'credit':0.000,
             }
         
        credit_val = {
                    'account_id': self.payment_id.partner_id.property_account_receivable_id.id,
                    'analytic_account_id':False,
                    'partner_id':self.payment_id.partner_id.id,
                    'name':self.name,
                    'debit':0.000,
                    'credit':self.amount,
                     }
        jv_vals = {
            'partner_id': self.payment_id.partner_id.id,
            'type': 'entry',
            'invoice_date':self.payment_id.payment_date,
            'date':self.payment_id.payment_date,
            'module_id':self.payment_id.module_id.id if self.payment_id.module_id else False,
            'lease_id':self.payment_id.lease_id.id if self.payment_id.lease_id else False,
            'building_id':self.payment_id.building_id.id if self.payment_id.building_id else False,
            'ref':'%s'%(self.name),
            'journal_id':int(advance_expense_journal_id),
            'line_ids': [(0, 0,debit_val),
                         (0, 0,credit_val)],
            }
        move_id = self.env['account.move'].create(jv_vals)
        self.move_id = move_id.id
        move_id.action_post()
        return move_id

    

