# -*- encoding: utf-8 -*-
# Copyright Knacktechs SA

from odoo import api, models

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"
     
   
    def _get_aml_for_register_payment(self):
        """ Get the aml to consider to reconcile in register payment """
        self.ensure_one()
        return self.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))


    def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False):
        """ Reconcile payable/receivable lines from the invoice with payment_line """
        line_to_reconcile = self.env['account.move.line']
        for inv in self:
            line_to_reconcile += inv._get_aml_for_register_payment()
        print('===========line_to_reconcile=============',line_to_reconcile)
        print('===========payment_line=============',payment_line)
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"   
    
    
    @api.model
    def compute_amount_fields(self, amount, src_currency, company_currency, invoice_currency=False):
        """ Method kept for compatibility reason """
        return self._compute_amount_fields(amount, src_currency, company_currency)


    @api.model
    def _compute_amount_fields(self, amount, src_currency, company_currency):
        """ Helper function to compute value for fields debit/credit/amount_currency based on an amount and the currencies given in parameter"""
        amount_currency = False
        currency_id = False
        if src_currency and src_currency != company_currency:
            amount_currency = amount
            amount = src_currency.with_context(self._context).compute(amount, company_currency)
            currency_id = src_currency.id
        debit = amount > 0 and amount or 0.0
        credit = amount < 0 and -amount or 0.0
        return debit, credit, amount_currency, currency_id

# AccountInvoice()

