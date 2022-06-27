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
                    if move_line_obj.name:
                        if 'CUST.IN' or 'SUPP.OUT' in move_line_obj.name:
                            payments = payment_pool.search([('name', '=', move_line_obj.name)])
                            for payment in payments:
                                payment._get_move_reconciled()
                                payment.state = 'reconciled'
                                line_vals = {
                                    'state': 'reconciled'
                                }
                                lines.append((1, line.id, line_vals))
                                move_line_obj.write({
                                    'rec_date': line.rec_date,
                                    'reconcilation_id': self.id

                                })
                                self.write({
                                    'reconcileline_ids': lines
                                })


                        linereconciled = True
                        if move_line_obj.payment_id:
                            if line.settlement_date:
                                move_line_obj.payment_id.settlement_date = line.settlement_date
            # line_entries = self.reconcileline_ids.filtered(lambda entry: entry.state != 'reconciled')
            # print("\n\n======================", line_entries)
            # if not line_entries:
            self.write({
                'state': 'validated'
            })

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
    
    
    
    
    