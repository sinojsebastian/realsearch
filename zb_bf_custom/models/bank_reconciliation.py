from odoo import api, fields, models,_
from datetime import datetime
from dateutil import relativedelta
from lxml import etree

from odoo.exceptions import UserError,Warning
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
import time
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)


class BankReconiliation(models.Model):
    _inherit ="bank.reconciliation"
    _description= "Bank Statement Reconcilation"
    
    
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
                    if move_line_obj.payment_id:
                        if line.settlement_date:
                            move_line_obj.payment_id.settlement_date = line.settlement_date
                            
#                 else:
            if not linereconciled:
                raise Warning(_("""no lines has been reconciled"""))
                        
        else:
            raise Warning(_("""no line to validate"""))
        balance_total = self.closing_balance_stmt + self.debit - self.credit
        self.difference =balance_total - self.closing_balance
        return True




class BankReconciliationLine(models.Model):
    _inherit = "bank.reconciliation.line"
    _description = "Bank Reconciliation Line Modification"
    
    
    @api.model
    def create(self,vals):
        move_line_obj = False
        if vals.get('move_line_id'):
            move_line_obj = self.env['account.move.line'].browse(vals.get('move_line_id'))
        if not vals.get('settlement_date'):
            if move_line_obj and move_line_obj.payment_id:
                vals['settlement_date'] = move_line_obj.payment_id.settlement_date
        
        res = super(BankReconciliationLine, self).create(vals)
        return res
    
    
    def write(self,vals):
        if not vals.get('settlement_date'):
            vals['settlement_date'] = self.settlement_date
        return super(BankReconciliationLine, self).write(vals)
    
    def _get_building_flat(self):
        for lines in self:
            ref = ''
            if lines.move_line_id.payment_id and lines.move_line_id.payment_id.building_id and lines.move_line_id.payment_id.module_id:
                ref = lines.move_line_id.payment_id.building_id.code+' '+lines.move_line_id.payment_id.module_id.name 
            elif lines.move_line_id.payment_id and lines.move_line_id.payment_id.building_id and not lines.move_line_id.payment_id.module_id:
                ref = lines.move_line_id.payment_id.building_id.code
            elif lines.move_line_id.payment_id and not lines.move_line_id.payment_id.building_id and lines.move_line_id.payment_id.module_id:
                ref = lines.move_line_id.payment_id.module_id
            lines.unit_ref = ref
    
    
    settlement_date = fields.Date('Settlement Date')
    unit_ref = fields.Char('Unit',compute='_get_building_flat')
    
    
class account_bank_reconciliation_report(models.AbstractModel):
    _inherit = 'account.bank.reconciliation.report'
    _description = 'Bank Reconciliation Report'


    @api.model
    def _get_bank_rec_report_data(self, options, journal):
        # General data + setup
        rslt = {}

        accounts = journal.default_debit_account_id + journal.default_credit_account_id
        company = journal.company_id
        amount_field = 'amount_currency' if journal.currency_id else 'balance'
        states = ['posted']
        states += options.get('all_entries') and ['draft'] or []

        # Get total already accounted.
        self._cr.execute('''
            SELECT SUM(aml.''' + amount_field + ''')
            FROM account_move_line aml
            LEFT JOIN account_move am ON aml.move_id = am.id
            WHERE aml.date <= %s AND aml.company_id = %s AND aml.account_id IN %s
            AND am.state in %s
        ''', [self.env.context['date_to'], journal.company_id.id, tuple(accounts.ids), tuple(states)])
        rslt['total_already_accounted'] = self._cr.fetchone()[0] or 0.0

        # Payments not reconciled with a bank statement line
        self._cr.execute('''
            SELECT
                aml.id,
                aml.name,
                aml.ref,
                aml.date, 
                aml.payment_id, 
                aml.''' + amount_field + '''                    AS balance
            FROM account_move_line aml
            LEFT JOIN res_company company                       ON company.id = aml.company_id
            LEFT JOIN account_account account                   ON account.id = aml.account_id
            LEFT JOIN account_account_type account_type         ON account_type.id = account.user_type_id
            LEFT JOIN account_bank_statement_line st_line       ON st_line.id = aml.statement_line_id
            LEFT JOIN account_payment payment                   ON payment.id = aml.payment_id
            LEFT JOIN account_journal journal                   ON journal.id = aml.journal_id
            LEFT JOIN account_move move                         ON move.id = aml.move_id
            LEFT JOIN bank_reconciliation rec                   ON rec.id = aml.reconcilation_id
            WHERE aml.date <= %s
            AND aml.company_id = %s
            AND CASE WHEN journal.type NOT IN ('cash', 'bank')
                     THEN payment.journal_id
                     ELSE aml.journal_id
                 END = %s
            AND account_type.type = 'liquidity'
            AND full_reconcile_id IS NULL
            AND (aml.statement_line_id IS NULL OR st_line.date > %s)
            AND (aml.reconcilation_id IS NULL OR aml.rec_date > %s)
            AND (company.account_bank_reconciliation_start IS NULL OR aml.date >= company.account_bank_reconciliation_start)
            AND move.state in %s
            ORDER BY aml.date DESC, aml.id DESC
        ''', [self._context['date_to'], journal.company_id.id, journal.id, self._context['date_to'],self._context['date_to'],tuple(states)])
        rslt['not_reconciled_payments'] = self._cr.dictfetchall()

        # Bank statement lines not reconciled with a payment
        rslt['not_reconciled_st_positive'] = self.env['account.bank.statement.line'].search([
            ('statement_id.journal_id', '=', journal.id),
            ('date', '<=', self._context['date_to']),
            ('journal_entry_ids', '=', False),
            ('amount', '>', 0),
            ('company_id', '=', company.id)
        ])

        rslt['not_reconciled_st_negative'] = self.env['account.bank.statement.line'].search([
            ('statement_id.journal_id', '=', journal.id),
            ('date', '<=', self._context['date_to']),
            ('journal_entry_ids', '=', False),
            ('amount', '<', 0),
            ('company_id', '=', company.id)
        ])
        # Final Bank Reconciliation
        last_statement = self.env['bank.reconciliation'].search([
            ('journal_id', '=', journal.id),
            ('to_date', '<=', self._context['date_to']),
        ], order="to_date desc, id desc", limit=1)
        # rslt['last_st_balance'] = last_statement.balance_end
        rslt['last_st_balance'] = last_statement.closing_balance_stmt
        rslt['last_st_end_date'] = last_statement.to_date
        return rslt







    
