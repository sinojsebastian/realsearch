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

import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class pdc_management(models.Model):
    _name = "pdc.management"
    _order = 'cheque_date desc'
    _description = 'Model for Post Dated Cheques'

    name = fields.Char(string='Cheque')
    cheque_date = fields.Date(string='Date')
    amount = fields.Float(string='Amount', digits='Account')
    bank_id = fields.Many2one('res.bank', string='Bank')
    submit_date = fields.Date(string='Submit Date')
    partner_id = fields.Many2one('res.partner', string='Partner')
    payment_ref_id = fields.Many2one('account.payment', 'Payment Reference')
    voucher_date = fields.Date(string='Voucher Date')
    partner_journal_id = fields.Many2one('account.journal', string='Bank A/C Journal')
    clear_reject_date = fields.Date(string='Clear/Reject Date')
    type = fields.Selection([('received', 'Received'), ('issued', 'Issued')], string='PDC Type', readonly=True)
    journal_id = fields.Many2one('account.journal', string='PDC Journal')
    posted_user_id = fields.Many2one('res.users', string='Posted by')
    state = fields.Selection([('draft', 'Draft'),
                              ('submitted', 'Submitted'),
                              ('rejected', 'Rejected'),
                              ('cleared', 'Cleared'),
                              ('payment_cancelled', 'Payment Cancelled')],
                             string='State', default='draft')
    move_ids = fields.One2many('account.move.line', 'pdc_id', string='Journal Items')
    deadline_date = fields.Date(compute='_compute_deadline_date')
    entry_id = fields.Many2one('account.move', string='Journal Entry')
    inv_id = fields.Many2one('account.move', string='Invoice')
    company_id = fields.Many2one('res.company', string='Company',default= lambda self :self.env.company.id)

    

    @api.depends('cheque_date')
    def _compute_deadline_date(self):
        for pdc in self:
            pdc.deadline_date = datetime.date.today() + datetime.timedelta(days=1)

    def button_submit(self):
        self.state = 'submitted'

    def button_cancel(self):
        self.state = 'payment_cancelled'

    def button_cleared(self):

        for rec in self:
            move_line_pool = self.env['account.move.line'].with_context(check_move_validity=False)
            move_pool = self.env['account.move']
            if not rec.clear_reject_date:
                raise Warning('Enter Clear Date')
            else:
                mov_vals = {
                    'name': rec.payment_ref_id.name or '',
                    'ref': rec.payment_ref_id.name or '',
                    'journal_id': rec.partner_journal_id.id or False,
                    'date': rec.clear_reject_date or False,
                }
                move_id = move_pool.create(mov_vals)
                rec.entry_id = move_id.id
                rec.state = 'cleared'
                rec.posted_user_id = self.env.user

                if rec.type == 'received':
                    debit_account = rec.partner_journal_id.default_debit_account_id.id or False
                    credit_account = rec.journal_id.default_credit_account_id.id
                if rec.type == 'issued':
                    debit_account = rec.journal_id and rec.journal_id.default_debit_account_id and rec.journal_id.default_debit_account_id.id or False
                    credit_account = rec.partner_journal_id.default_credit_account_id.id
                total_amount = 0.00
                debit_aml_dict = {
                    'pdc_id': rec.id,
                    'debit': rec.amount,
                    'credit': 0.00,
                    'account_id': debit_account,
                    'journal_id': rec.partner_journal_id.id,
                    'date': rec.clear_reject_date,
                    'name': rec.payment_ref_id.name or '/',
                    'partner_id': rec.payment_ref_id.partner_id.id,
                    'currency_id': rec.journal_id.currency_id.id,
                    'move_id': move_id.id

                }
                total_amount -= rec.amount
                credit_aml_dict = {
                    'account_id': credit_account,
                    'pdc_id': rec.id,
                    'credit': rec.amount,
                    'debit': 0.00,
                    'journal_id': rec.partner_journal_id.id,
                    'date': rec.clear_reject_date,
                    'name': rec.payment_ref_id.name or '/',
                    'currency_id': rec.journal_id.currency_id.id,
                    'partner_id': rec.partner_id.id,
                    #                     'amount_currency': total_amount,
                    'move_id': move_id.id

                }
                move_line_pool.create(debit_aml_dict)
                move_line_pool.create(credit_aml_dict)
        return True

    def button_rejected(self):

        if not self.clear_reject_date:
            raise Warning('Enter Rejected Date')

        self.posted_user_id = self.env.user

        return {
            'name': 'Reject Cheque',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'reject.cheque',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def onchange_payment_ref(self, payment_ref_id):
        if payment_ref_id:
            payment_obj = self.env['account.payment'].browse(payment_ref_id)
            if payment_obj.payment_type:
                if payment_obj.payment_type == 'outbound':
                    pdc_type = 'issued'
                if payment_obj.payment_type == 'inbound':
                    pdc_type = 'received'
                result = {'value': {'type': pdc_type}}
                return result
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
