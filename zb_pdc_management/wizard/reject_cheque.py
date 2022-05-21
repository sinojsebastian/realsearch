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

from odoo import models, fields, api, _


class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    charges_account_id = fields.Many2one('account.account', string='Charges Account')

    def set_default_charges_account_id(self):
        config = self.browse()
        icp = self.env['ir.config_parameter']
        if config.charges_account_id:
            icp.set_param('pdc_management.charges_account_id',
                          config.charges_account_id.id or '')


class reject_cheque(models.TransientModel):
    _name = 'reject.cheque'
    _description = 'Reject Cheque'

    @api.model
    def default_get(self, fields):
        res = super(reject_cheque, self).default_get(fields)
        pdc_obj = self.env['pdc.management'].browse(self._context.get('active_id', []))
        charges_account_id = self.env['ir.config_parameter'].get_param("pdc_management.charges_account_id")
        if charges_account_id:
            res['charges_account_id'] = int(charges_account_id)
        res['reject_date'] = pdc_obj.clear_reject_date
        return res

    reject_date = fields.Date(string='Rejected Date')
    charges = fields.Float(string='Charges', digits='Product Unit of Measure')
    charges_account_id = fields.Many2one('account.account', string='Charges Account')

    def action_reject_cheque(self):
        move_line_pool = self.env['account.move.line'].with_context(check_move_validity=False)
        move_pool = self.env['account.move']
        pdc_obj = self.env['pdc.management'].browse(self._context.get('active_id', []))
        pdc_obj.state = 'rejected'
        mov_vals = {
            'name': str(pdc_obj.inv_id.name) + ' : Cheque Rejection',
            'ref': pdc_obj.payment_ref_id.name,
            'journal_id': pdc_obj.partner_journal_id.id,
            'date': pdc_obj.payment_ref_id.payment_date,
        }

        move_id = move_pool.create(mov_vals)
        if pdc_obj.type == 'received':
            debit_account = self.charges_account_id and self.charges_account_id.id or False
            credit_account = pdc_obj.partner_journal_id and pdc_obj.partner_journal_id.default_credit_account_id and \
                pdc_obj.partner_journal_id.default_credit_account_id.id or False

        if pdc_obj.type == 'issued':
            debit_account = self.charges_account_id and self.charges_account_id.id or False
            credit_account = pdc_obj.partner_journal_id and pdc_obj.partner_journal_id.default_credit_account_id and \
                pdc_obj.partner_journal_id.default_credit_account_id.id or False
        vals1 = {
            'debit': 0.00,
            'credit': self.charges,
            'account_id': credit_account,
            'pdc_id': pdc_obj.id,
            'journal_id': pdc_obj.journal_id.id,
            'date': pdc_obj.clear_reject_date,
            'name': pdc_obj.payment_ref_id.name or '/',
            'partner_id': pdc_obj.payment_ref_id.partner_id.id,
            'move_id': move_id.id,
            'currency_id': pdc_obj.journal_id.currency_id.id,
        }
        vals2 = {
            'debit': self.charges,
            'credit': 0.00,
            'account_id': debit_account,
            'pdc_id': pdc_obj.id,
            'journal_id': pdc_obj.journal_id.id,
            'date': pdc_obj.clear_reject_date,
            'name': pdc_obj.payment_ref_id.name or '/',
            'partner_id': pdc_obj.payment_ref_id.partner_id.id,
            'move_id': move_id.id,
            'currency_id': pdc_obj.journal_id.currency_id.id,
        }
        move_line_pool.create(vals1)
        move_line_pool.create(vals2)
        pdc_obj.entry_id = move_id.id
        if pdc_obj.payment_ref_id.state == 'posted':
            pdc_obj.payment_ref_id.action_draft()
            pdc_obj.payment_ref_id.cancel()
        else:
            pdc_obj.payment_ref_id.cancel()
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
