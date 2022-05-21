# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
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

from odoo import models, api, _, fields


class AccountJournal(models.Model):
    _inherit = ['account.journal']

    type = fields.Selection(selection_add=[('post_dated_chq', 'Post Dated CHQ')])


class AccountMove_line(models.Model):
    _inherit = 'account.move.line'

    pdc_id = fields.Many2one('pdc.management', string='PDC')
    cheque_no = fields.Char(string='Cheque No', related='move_id.cheque_no', store=True)
    cheque_date = fields.Date(string='Cheque Date', related='move_id.cheque_date', store=True)
    cheque_bank_id = fields.Many2one('res.bank', string='Cheque Bank', related='move_id.cheque_bank_id', store=True)
    journal_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
    ], string='Type', related='journal_id.type')


class account_payment(models.Model):
    _inherit = "account.payment"

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
    cheque_no = fields.Char(string='Cheque No')
    cheque_date = fields.Date(string='Cheque Date')
    cheque_bank_id = fields.Many2one('res.bank', string='Cheque Bank')
    partner_journal_id = fields.Many2one('account.journal', string='Bank Journal')
    inv_id = fields.Many2one('account.move', domain=[('type', 'in', ['out_invoice', 'out_refund', 'in_refund', 'in_invoice'])], string='Invoice')

    def _compute_journal_domain_and_types(self):
        res = super(account_payment, self)._compute_journal_domain_and_types()
        journal_types = {'cash', 'post_dated_chq', 'bank'}
        res['journal_types'] = journal_types
        return res

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

    def post(self):
        res = super(account_payment, self).post()
        if not self._context.get('no_pdc', False):
            for payment in self:
                if payment.journal_type == 'post_dated_chq':
                    type = ''
                    if payment.payment_type == 'outbound':
                        type = 'issued'
                    if payment.payment_type == 'inbound':
                        type = 'received'
                    #dd = payment.inv_id
                    vals = {
                        'name': payment.cheque_no or '',
                        'cheque_date': payment.cheque_date or False,
                        'amount': payment.amount or 0.0,
                        'bank_id': payment.cheque_bank_id.id or False,
                        'partner_id': payment.partner_id.id or False,
                        'payment_ref_id': payment.id or False,
                        'voucher_date': payment.payment_date or False,
                        'partner_journal_id': payment.partner_journal_id and payment.partner_journal_id.id or False,
                        'type': type,
                        'journal_id': payment.journal_id and payment.journal_id.id or False,
                        'submit_date': payment.cheque_date or False,
                        'state': 'draft',
                    }

                    self.env['pdc.management'].create(vals)
        return res


class BankAccounts(models.Model):
    _inherit = ['res.partner.bank']

    charges_account_id = fields.Many2one('account.account', string='Charges Account')


class AccountMove(models.Model):
    _inherit = ['account.move']

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: