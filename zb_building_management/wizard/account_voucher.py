# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from odoo import models, fields, api,exceptions
from odoo.tools.translate import _
from datetime import datetime
import itertools
from lxml import etree
from werkzeug.urls import url_encode
from odoo.tools import mute_logger, test_reports
class account_payment(models.Model):
    
    _inherit = "account.payment"
    _description = "Account Invoice Fields Modification"
    
    
    def fill_notes(self):
        payment_ids = self.env['account.payment'].search([])
        if payment_ids:
            for payment in payment_ids:
                if payment.notes and payment.move_line_ids:
                    for move in payment.move_line_ids:
                        move.narration = payment.notes
                        move.journal_id.narration = payment.notes
            
        
        
#  DB   def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
#         
#         res = super(account_payment, self)._get_shared_move_line_vals(debit, credit, amount_currency, move_id, invoice_id)
#         if self.building_id:
#             res.update({
#                 'building_id': self.building_id.id
#              })
#         return res
    

    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('zb_building_management.email_template_session_mail8', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.payment',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="account.mail_template_data_notification_email_account_invoice",
            force_email=True
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


    
    def default_comment(self):
        '''This function return addtional log for voucher'''
        module_id = False
        context = self._context or {}
        log = ''
        if context.get('active_model', '') and context['active_model'] == 'account.invoice':
            if context.get('active_id', False):
                invoice = self.env.get('account.invoice').browse(context['active_id'])
                if invoice.comment:
                    log = invoice.comment
                else:
                    log = False
        return log


    def default_check_date(self):
        '''This function return check date for customer payment voucher'''
        check_date = False
        context = self._context or {}
        if context.get('active_model', '') and context['active_model'] == 'account.voucher':
            if context.get('active_id', False):
                voucher = self.env.get('account.payment').browse(context['active_id'])
                if voucher.check_date:
                    date = voucher.check_date
                else:
                    date = datetime.now()
        else:
            date = datetime.now()
        return date

    
  
          
    def action_validate_invoice_reprint(self):
        return self.env.ref('zb_building_management.action_report_receipts').report_action(self)
     
     
    
   
    check_no = fields.Char('Check Number', size = 32)
    bank_id = fields.Many2one('res.bank', 'Bank')
    check_date = fields.Date('Check Date',default = default_check_date)
    report_status = fields.Selection([('no', 'No Report'),('with', 'Report')],default ='no', string='Report Type')
    logo = fields.Text('comment',default = default_comment)
    validated = fields.Boolean('Validate')
    


class ReportPlacementLetter(models.AbstractModel):
    _name = 'report.receipt_payment'
     
     
    def _get_day(self):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(data.get('active_ids'))
        res=[]
        for x in docs:
            res.append({
            'amount':x.amount,
            'journal_id':x.journal_id,
            'payment_date':x.payment_date,
            'check_no':x.check_no})
        return res
     
     
    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
 
        holidays_report = self.env['ir.actions.report']._get_report_from_name('zb_building_management.report_payment_receipts')
        holidays = self.env['account.invoice'].browse(self.ids)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(data.get('active_ids'))
        return {
            'doc_ids': self.ids,
            'doc_model': holidays_report.model,
            'docs': holidays,
            'amount':docs.amount,
            'journal_id':docs.journal_id,
            'payment_date':docs.payment_date,
            'check_no':docs.check_no
        }
