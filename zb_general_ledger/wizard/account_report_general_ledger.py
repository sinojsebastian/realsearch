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

from odoo import _, api, fields, models
import time
from datetime import date,datetime
import logging

_logger = logging.getLogger(__name__)


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.report.general.ledger"
    
    
    @api.model
    def default_get(self,vals):
        result = super(AccountReportGeneralLedger, self).default_get(vals)
        start_date = date(date.today().year, 1, 1)
        result['date_from'] = start_date
        result['date_to'] = datetime.today()
        return result
    
    account_ids = fields.Many2many('account.account', 'account_wiz_rel_ledger', 'wiz_id', 'account_id', 'Account')
    partner_ids = fields.Many2many('res.partner', 'partner_wiz_rel_ledger', 'wiz_id', 'partner_id', 'Partner(s)')
    combine_aging_bool = fields.Boolean('Include Aging Report')
    period_length = fields.Integer(string='Period Length (days)', required=True, default=30,readonly=True)
    partner_exists = fields.Boolean(string="Partner Exists",compute='partner_data_exists')
    report_type =fields.Selection([('pdf', 'PDF'),
                                    ('xlsx', 'XLSX')],string='Report Type',default='xlsx')
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    show_curr = fields.Boolean('Show Foreign Currency',default=True)
    account_type_ids = fields.Many2many('account.account.type','general_wiz_account_type_rel',\
                                        'wiz_id','account_type_id',string="Account Types")
    
    @api.depends('partner_ids')
    def partner_data_exists(self):
        if self.partner_ids:
            self.partner_exists = True
    
    def _print_report(self, data):
        super(AccountReportGeneralLedger, self)._print_report(data)
        _logger.warning('_print_report _______________________%s',data)
        records = data['form'].update(self.read(['account_ids'])[0])
        _logger.warning('dddddddddddddddddddddddddddd _______________________%s',data['form'])
        return self.env.ref('accounting_pdf_reports.action_report_general_ledger').with_context(landscape=True).report_action(records, data=data)

#         return res

    
    
    def print_xlsx_report(self):
        return self.env.ref('zb_general_ledger.general_ledger_xlsx').report_action(self)
    
    
    @api.onchange('account_type_ids')
    def set_accounts(self):
        for wiz in self:
            if wiz.account_type_ids:
                account_ids = self.env['account.account'].search([('user_type_id','in',wiz.account_type_ids.ids)]).ids
                user_type_ids = wiz.account_type_ids.ids
            else:
                account_ids = []
                user_type_ids = self.env['account.account.type'].search([]).ids
            wiz.account_ids = account_ids or []
            return {'domain': {'account_ids': [('user_type_id','in',user_type_ids)]}}
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: