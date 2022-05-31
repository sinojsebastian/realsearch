# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class TaxAdjustments(models.TransientModel):
    _inherit = 'tax.adjustments.wizard'
    _description = 'Tax Adjustments Wizard'
    
    tax_id = fields.Many2one(string="Tax Line", comodel_name='account.tax', required=True, help="The report line to make an adjustment for.")

    @api.onchange('tax_id')
    def _set_report_line(self):
        domain = []
        report_line_list = []
        if self.tax_id:
            repartition_line_ids = self.env['account.tax.repartition.line'].search([('invoice_tax_id','=',self.tax_id.id)])
            for repart_line in repartition_line_ids:
                tag_ids = repart_line.tag_ids
                report_line_ids = self.env['account.tax.report.line'].search([('tag_ids','in',tag_ids.ids)])
                for line in report_line_ids:
                    if line.id not in report_line_list:
                        report_line_list.append(line.id)
        res = {}
        res['domain'] = {'tax_report_line_id': [('id', 'in', report_line_list)]}
        return res
    
    
    def create_move(self):
        move_line_vals = []
    
        is_debit = self.adjustment_type == 'debit'
        sign_multiplier = (self.amount<0 and -1 or 1) * (self.adjustment_type == 'credit' and -1 or 1)
        filter_lambda = (sign_multiplier < 0) and (lambda x: x.tax_negate) or (lambda x: not x.tax_negate)
        adjustment_tag = self.tax_report_line_id.tag_ids.filtered(filter_lambda)
    
        # Vals for the amls corresponding to the ajustment tag
        move_line_vals.append((0, 0, {
            'name': self.reason,
            'debit': is_debit and abs(self.amount) or 0,
            'credit': not is_debit and abs(self.amount) or 0,
            'account_id': is_debit and self.debit_account_id.id or self.credit_account_id.id,
            'tax_report_line':self.tax_report_line_id.id,
            'tag_ids': [(6, False, [adjustment_tag.id])],
        }))
    
        # Vals for the counterpart line
        move_line_vals.append((0, 0, {
            'name': self.reason,
            'debit': not is_debit and abs(self.amount) or 0,
            'credit': is_debit and abs(self.amount) or 0,
            'account_id': is_debit and self.credit_account_id.id or self.debit_account_id.id,
        }))
    
        # Create the move
        vals = {
            'journal_id': self.journal_id.id,
            'date': self.date,
            'state': 'draft',
            'line_ids': move_line_vals,
        }
        move = self.env['account.move'].create(vals)
        for line in move.line_ids:
            if line.tax_report_line:
                line.tax_line_id = self.tax_id.id
        move.post()
    
        # Return an action opening the created move
        action = self.env.ref(self.env.context.get('action', 'account.action_move_line_form'))
        result = action.read()[0]
        result['views'] = [(False, 'form')]
        result['res_id'] = move.id
        return result