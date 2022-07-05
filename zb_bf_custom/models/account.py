# -*- coding: utf-8 -*-

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



class AccountAccount(models.Model):
    _inherit = "account.account"
    _description = "Account"
    

    def _get_balance(self):
        for acct in self:
            sql="select l.debit, l.credit from account_move_line as l where l.account_id=%s"%(acct.id)
            self._cr.execute(sql)
            moves=self._cr.fetchall()
            debit = credit = 0.000
            for mov in moves:
                debit = debit + mov[0]
                credit = credit + mov[1]
            acct.outstanding_balance = debit - credit

    outstanding_balance = fields.Float('Balance',compute='_get_balance')
    outstanding = fields.Float('Balance',related='outstanding_balance',store =True)
    
 
class AccountPayment(models.Model):
    _inherit = "account.payment"
    _description = "Account Payment"
    

    def reload_lines(self):
        for order in self:
            order._onchange_partner_id()
    
    
    @api.model
    def default_lease_id(self):
        lease_id = False
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        
        if active_model and active_model == 'account.move':
            if active_id:
                invoice = self.env['account.move'].browse(active_id)
                if invoice.module_id:
                    lease_id = invoice.lease_id.id
                else:
                    lease_id = False
        
        return lease_id
    
    @api.model
    def default_get(self, fields):
        res = super(AccountPayment, self).default_get(fields)
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        description = ''
        if active_model and active_model == 'account.move':
            if active_id:
                invoice = self.env['account.move'].browse(active_id)
                res.update({
                    'journal_id':self.env['account.journal'].search([('company_id', '=', self.env.company.id),('outbound_payment_method_ids','!=',False),('type', 'in', ('bank','cash','post_dated_chq'))], limit=1).id,
                })
                
                for lines in invoice.invoice_line_ids:
                    if lines.name:
                        description += lines.name+','
                description = description[:-1]
                res.update({
                                'notes':description
                            })
        return res
    
    @api.onchange('module_id')
    def fetch_owner(self):
        if self.module_id and self.module_id.owner_id:
            self.owner_id = self.module_id.owner_id.id
        payment_lines = self._load_payment_lines()
        self.payment_line_ids = [(6, 0, [])]
        self.payment_line_ids = payment_lines
        
    @api.onchange('unit_id')
    def onchange_unit_id(self):
        if self.unit_id and self.unit_id.owner_id:
            self.owner_id = self.unit_id.owner_id.id
        payment_lines = self._load_payment_lines()
        self.payment_line_ids = [(6, 0, [])]
        self.payment_line_ids = payment_lines
        
#     
    payment_advise = fields.Boolean(string="Payment Advise")
    lease_id = fields.Many2one('zbbm.module.lease.rent.agreement',string="Lease", default=default_lease_id)
    collected_by_user_id = fields.Many2one('res.users',string="Collected By",copy=False)
    owner_id = fields.Many2one('res.partner',string="Owner")
    
    def _get_move_vals(self, journal=None):
        res = super(AccountPayment,self)._get_move_vals(journal)
        res.update({
                    'lease_id':self.lease_id.id or False,
                    'owner_id':self.module_id.owner_id.id or False,
            })
        return res
    
    
#  DB   def post(self): 
#         """    Function overridden to generate vendor payment
#                 for Owner of leasable unit when  invoice is rent    """
#           
#         res = super(AccountPayment, self).post()
#         params = self.env['ir.config_parameter'].sudo()    
#         entries = self.payment_entries()
#         
#         rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
#         rent_transfer_journal_id = params.get_param('zb_bf_custom.rent_transfer_journal_id') or False
#         rent_transfer_product_id = params.get_param('zb_bf_custom.rent_transfer_product_id') or False
#         
#         product = self.env['product.product'].browse(int(rent_transfer_product_id))
#         
#         for invoice_id in  self.invoice_ids:
#             if invoice_id.journal_id.id == int(rent_invoice_journal_id):
#                 if invoice_id.module_id and invoice_id.module_id.owner_id:
#                     if invoice_id.module_id.building_id.analytic_account_id:
#                         analytic = invoice_id.module_id.building_id.analytic_account_id.id
#                     else:
#                         analytic = '' 
#                     
# #                    
#                     debit_val =  {
#                         'account_id':product.property_account_income_id.id,
#                         'analytic_account_id':analytic,
#                         'partner_id':invoice_id.module_id.owner_id.id,
#                         'debit':invoice_id.amount_total,
#                         'credit':0.000,
#                          }
#                     
#                     credit_val = {
#                                 'account_id': invoice_id.module_id.owner_id.property_account_receivable_id.id,
#                                 'analytic_account_id':analytic,
#                                 'partner_id':invoice_id.module_id.owner_id.id,
#                                 'debit':0.000,
#                                 'credit':invoice_id.amount_total,
#                                  }
#                     jv_vals = {
#                         'partner_id': invoice_id.module_id.owner_id.id,
#                         'type': 'entry',
#                         'invoice_date':invoice_id.invoice_date,
#                         'module_id': invoice_id.module_id.id,
#                         'building_id':invoice_id.module_id.building_id.id,
#                         'journal_id':int(rent_transfer_journal_id),
#                         'line_ids': [(0, 0,debit_val),
#                                      (0, 0,credit_val)],
#                         }
#                     
#                     journal_id = self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('type', 'in', ('bank', 'cash'))], limit=1).id
#                     domain = [('payment_type', '=', 'outbound')]
#                     payment_method_id= self.env['account.payment.method'].search(domain, limit=1).id
#                     
#                     if invoice_id.amount_residual ==0.000:
#                         move_id = self.env['account.move'].create(jv_vals) 
#                         move_id.action_post()
#                         
#                         company_id = self.env['res.company']._company_default_get()  
#                         if invoice_id.module_id and invoice_id.module_id.state != 'delisted' and invoice_id.module_id.managed == True and invoice_id.module_id.owner_id != False:
#                             management_fee_journal_id = params.get_param('zb_bf_custom.management_fee_journal_id') or False
#                             management_product_id = params.get_param('zb_bf_custom.management_product_id') or False
#                             building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
#                             last_date = invoice_id.invoice_date
#                             updated_last_date = datetime.strptime(str(invoice_id.invoice_date), '%Y-%m-%d')
#                             if not building_income_account_id:
#                                 journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
#                                 if journal :
#                                     acct_id = journal[0].default_credit_account_id.id
#                             else:
#                                 acct_id = int(building_income_account_id)
#                                 
#                             description = 'Management Fee for the Period for the Month '+ updated_last_date.strftime("%B")+' '+ updated_last_date.strftime("%Y")
#                             params = self.env['ir.config_parameter'].sudo()        
#                             tax_ids = params.get_param('zb_building_management.default_rental_tax_ids') or False,
#                             if tax_ids[0]:
#                                 temp = re.findall(r'\d+', tax_ids[0]) 
#                                 tax_list = list(map(int, temp))
#                             
#                             product = self.env['product.product'].browse(int(management_product_id))
#                             
#                             amt = 0.000
#                             if invoice_id.module_id.management_fees_percent:
#                                 perc = invoice_id.module_id.management_fees_percent/100
#                                 amt = perc *invoice_id.module_id.monthly_rate
#                             
#                                 vals = {
#                                       'partner_id': invoice_id.module_id.owner_id.id,
#                                       'type': 'out_invoice',
#                                       'invoice_date': last_date,
#                                       'building_id': invoice_id.module_id.building_id.id,
#                                       'module_id': invoice_id.module_id.id,
#                                       'comment': description,
#                                       'journal_id':int(management_fee_journal_id),
#                                       'management_fees_boolean':True,
#                                       'invoice_line_ids': [(0, 0, {
#                                                             'product_id':int(management_product_id),
#                                                             'name': description,
#                                                             'price_unit': amt,
#                                                             'tax_ids' : product.taxes_id.ids,
#                                                             'quantity': 1,
#                                                             'account_analytic_id':invoice_id.module_id.building_id.analytic_account_id.id if invoice_id.module_id.building_id.analytic_account_id else '',
#                                                             'account_id':product.property_account_income_id.id,
#                                                             })],
#                                     }
#                                 invoice_id = self.env.get('account.move').create(vals)
#                                 for line in invoice_id.line_ids:
#                                     if line.credit > 0.000:
#                                         line.partner_id = company_id.partner_id.id
#                                 invoice_id.action_post()
#                                 
#                         building_journal_id = params.get_param('zb_bf_custom.building_journal_id') or False
#                         if not building_journal_id:
#                             raise Warning(_('Please Configure Building Bank Journal'))
#                         for entry in entries:
#                             if entry['number'] == invoice_id.name:
#                                 owner_payment_vals = {
#                                     'payment_type':'outbound',
#                                     'partner_id':invoice_id.module_id.owner_id.id,
#                                     'lease_id':invoice_id.lease_id.id,
#                                     'amount':invoice_id.amount_total,
#                                     'payment_advise':True,
#                                     'method_type':'adjustment',
#                                     'partner_type':'supplier',
#                                     'building_id':invoice_id.module_id.building_id.id,
#                                     'module_id':invoice_id.module_id.id,
#                                     'journal_id':int(building_journal_id),
#                                     'payment_method_id':payment_method_id,
#                                     }
#                                 payment = self.env['account.payment'].create(owner_payment_vals)
#                                 payment._onchange_partner_id()
#                                 invoice_id.lease_id.payment_advise_id = payment.id
#                                 
#         return res
    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        print('==========================context',self._context)
        res = super(AccountPayment, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         default_type = self._context.get('default_type', False)
        partner_type = self._context.get('default_partner_type', False)
        if partner_type and partner_type not in ['customer']:
            receipt_reports = self.env.ref('zb_bf_custom.report_receipt_voucher_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == receipt_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            if 'default_payment_advise' not in self._context:
                payment_advise_report = self.env.ref('zb_bf_custom.report_payment_invoice_qweb')
                for print_submenu in res.get('toolbar', {}).get('print', []):
                    if print_submenu['id'] == payment_advise_report.id:
                        res['toolbar']['print'].remove(print_submenu)
        
        if partner_type and partner_type not in ['supplier']:
            if 'default_payment_advise' in self._context:
                print('========================hiiiiiiiiiiiiii',self._context['default_payment_advise'])
                receipt_reports = self.env.ref('zb_bf_custom.report_receipt_voucher_qweb')
                for print_submenu in res.get('toolbar', {}).get('print', []):
                    if print_submenu['id'] == receipt_reports.id:
                        res['toolbar']['print'].remove(print_submenu)
                
                cus_payment_reports = self.env.ref('zb_account_reports.payment_receipt_report')
                for print_submenu in res.get('toolbar', {}).get('print', []):
                    if print_submenu['id'] == cus_payment_reports.id:
                        res['toolbar']['print'].remove(print_submenu)
            else:
                payment_reports = self.env.ref('zb_bf_custom.report_payment_voucher_qweb')
                for print_submenu in res.get('toolbar', {}).get('print', []):
                    if print_submenu['id'] == payment_reports.id:
                        res['toolbar']['print'].remove(print_submenu)
                cus_payment_reports = self.env.ref('zb_account_reports.payment_receipt_report')
                for print_submenu in res.get('toolbar', {}).get('print', []):
                    if print_submenu['id'] == cus_payment_reports.id:
                        res['toolbar']['print'].remove(print_submenu)
                payment_advise_report = self.env.ref('zb_bf_custom.report_payment_invoice_qweb')
                for print_submenu in res.get('toolbar', {}).get('print', []):
                    if print_submenu['id'] == payment_advise_report.id:
                        res['toolbar']['print'].remove(print_submenu)
                    
#         doc = etree.XML(res['arch'])
#         print(self._context,'ccccccc')
#         for node in doc.xpath("//field[@name='cheque_no']"):
#             node.set('string', 'cccccc')
#         res['arch'] = etree.tostring(doc, encoding='unicode')
            
        return res
    
    @api.model
    def payment_entries(self):
        payment_list =[]
        payment_dict={}
        for payment in self:
#             for inv in payment.invoice_ids:
#                 payment_vals = inv._get_payments_vals()
#                 for vals in payment_vals:
#                     if vals['account_payment_id'] == payment.id:
            move_id = self.env['account.move'].search([('name','=',payment.move_name)]) 
            payy_ml_id=''
            for aml in move_id.line_ids:
                if aml.account_id.reconcile:
                    if payment.payment_type == 'outbound':
                        if aml.debit >0:
                            payy_ml_id = aml.id
                    else:
                        if payment.payment_type == 'inbound':
                            if aml.credit >0:
                                payy_ml_id = aml.id
            move_line_ids = self.env['account.move.line'].browse(payy_ml_id)
            partial_reconciled_entrys=''
            for move_line in move_line_ids:
                if payment.payment_type == 'outbound':
                    partial_reconciled_entrys = self.env['account.partial.reconcile'].search([('debit_move_id','=',payy_ml_id)])  
                else:
                    if payment.payment_type == 'inbound':   
                        partial_reconciled_entrys = self.env['account.partial.reconcile'].search([('credit_move_id','=',payy_ml_id)]) 
                         
            for entry in partial_reconciled_entrys:
                name = ''
                date = ''
                ref = ''
                from_date = ''
                to_date = ''
                module = ''
                label = ''
                amount_total = ''
                amount_due = ''
                from_date_lang = ''
                to_date_lang = ''
                if entry.credit_move_id.move_id.type != 'entry':
                    name = entry.credit_move_id.move_id.name
                    date = entry.credit_move_id.move_id.invoice_date
                    ref = entry.credit_move_id.move_id.ref
                    desc =[line.name for line in entry.credit_move_id.move_id.invoice_line_ids]
                    label = desc[0]
                    amount_total = entry.credit_move_id.move_id.amount_total
                    amount_due = entry.credit_move_id.move_id.amount_residual
                    from_date = entry.credit_move_id.move_id.from_date
                    to_date = entry.credit_move_id.move_id.to_date
                    module = entry.credit_move_id.move_id.module_id
                else:
                    if entry.debit_move_id.move_id.type != 'entry':
                        name = entry.debit_move_id.move_id.name
                        date = entry.debit_move_id.move_id.invoice_date
                        ref = entry.debit_move_id.move_id.ref
                        desc =[line.name for line in entry.debit_move_id.move_id.invoice_line_ids]
                        label = desc[0]
                        amount_total = entry.debit_move_id.move_id.amount_total
                        amount_due = entry.debit_move_id.move_id.amount_residual
                        from_date = entry.debit_move_id.move_id.from_date
                        to_date = entry.debit_move_id.move_id.to_date
                        module = entry.debit_move_id.move_id.module_id
                    else:
                        name = entry.debit_move_id.move_id.name
                        date = entry.debit_move_id.move_id.date
                        ref = entry.debit_move_id.move_id.ref
                        desc =[line.name for line in entry.debit_move_id.move_id.line_ids]
                        label = desc[0]
                        amount_total = entry.debit_move_id.move_id.amount_total
                        amount_due = entry.debit_move_id.move_id.amount_residual
                        from_date = entry.debit_move_id.move_id.from_date
                        to_date = entry.debit_move_id.move_id.to_date
                        module = entry.debit_move_id.move_id.module_id
                        
                if date:
                    date_lang = date.strftime(get_lang(self.env).date_format)
                if from_date:
                    from_date_lang = from_date.strftime(get_lang(self.env).date_format)
                if to_date:
                    to_date_lang = to_date.strftime(get_lang(self.env).date_format)
                
                payment_dict={
                       'number':name,
                       'invoice_date':date_lang,
                       'ref':ref,
                       'label':label,
                       'from_date':from_date_lang,
                       'to_date':to_date_lang,
                       'module':module,
                       'amount':entry.amount,
                       'amt_total':amount_total,
                       'amt_due':amount_due,
                       }
                payment_list.append(payment_dict)
        return payment_list
    
    
    @api.model
    def amount_words(self):
        word = {}
        sum=0
        words = 0
        for payment_id in self:
            if payment_id.method_type=='advance':
                if payment_id.payment_entries():
                    for payment in payment_id.payment_entries():
                        sum=sum+payment['amount']
                        fils,bd = math.modf(sum)
                        fils = (float_round(fils,payment_id.currency_id.decimal_places)*(10**payment_id.currency_id.decimal_places))
                        words = 'BHD'+' '+num2words(int(bd)).capitalize()+' '+'and'+ ' '+num2words(int(fils)).capitalize()+' '+payment_id.currency_id.currency_subunit_label+' '+'Only'
                        # words = 'BD'+' '+num2words(int(bd)).upper()+' '+ 'AND'+' '+num2words(int(fils)).upper()+' '+payment_id.currency_id.currency_subunit_label+' '+ '/- ONLY'
                        word.update({payment_id.id:words})
                else:
                    fils,bd = math.modf(payment_id.amount)
                    fils = (float_round(fils,payment_id.currency_id.decimal_places)*(10**payment_id.currency_id.decimal_places))
                    words = 'BHD'+' '+num2words(int(bd)).capitalize()+' '+'and'+ ' '+num2words(int(fils)).capitalize()+' '+payment_id.currency_id.currency_subunit_label+' '+'Only'
                    word.update({payment_id.id:words})
                    
            else:
                for payment in payment_id.payment_line_ids:
                    sum=sum+payment.allocation
                    fils,bd = math.modf(sum)
                    fils = (float_round(fils,payment_id.currency_id.decimal_places)*(10**payment_id.currency_id.decimal_places))
                    words = 'BHD'+' '+num2words(int(bd)).capitalize()+' '+'and'+ ' '+num2words(int(fils)).capitalize()+' '+payment_id.currency_id.currency_subunit_label+' '+'Only'
                    # words = 'BD'+' '+num2words(int(bd)).upper()+' '+ 'AND'+' '+num2words(int(fils)).upper()+' '+payment_id.currency_id.currency_subunit_label+' '+ '/- ONLY'
                    word.update({payment_id.id:words})
        
        return words
    
    
    def post(self):
        for order in self:
#  pv-duplicate code           reconcile_line_id = order.move_line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
#             print('=================reconcile_line_id==========================',reconcile_line_id)
#             if order.method_type =='adjustment':
#                 invoice_currency = False
#                 aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
#                 if order.invoice_ids and all([x.currency_id == order.invoice_ids[0].currency_id for x in order.invoice_ids]):
#                 #if all the invoices selected share the same currency, record the paiement in that currency too
#                     invoice_currency = order.invoice_ids[0].currency_id
#                 debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(order.amount, order.currency_id, order.company_id.currency_id, invoice_currency)
#                 #Write line corresponding to invoice payment
#                 if order.payment_advise:
#                     move_line_ids = [each.move_line_id.id for each in order.payment_line_ids if each.credit > 0 and not each.move_line_id.reconciled and each.allocation >0]
#                     mov_line_id = self.env['account.move.line'].browse(move_line_ids)
#                     print('==================mov_line_id====================',mov_line_id)
#                     (mov_line_id + reconcile_line_id).reconcile()
                    
            user_id=self.env['res.users'].browse(self._uid)
            order.write({'collected_by_user_id':user_id.id,
                           })
#             order.fetch_owner()
            # rent-transfer on partial payment
        
        return super(AccountPayment, self).post()
    
    
    def write(self, vals):
        '''Modified for Message Post'''
        msg = ''
        if self.ids:
            if vals.get('state', False):
                state = dict(self._fields['state'].selection).get(vals['state'])
                msg = 'State -> %s</br>' %state
                self.message_post(body=msg)
                     
        res = super(AccountPayment, self).write(vals)
        return res
    
    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        for order in self:
            pdc = self.env['pdc.management'].search([('payment_ref_id','=',order.id)])
            if pdc:
                for payment in pdc:
                    payment.unlink()

            reconcilied_ids = self.env['account.partial.reconcile'].search([('reconcilied_payment_id','=',order.id)])
            reconcilied_ids.unlink()
        for adv_exp_line in self.advance_expense_ids:
            entry = self.env['account.move'].search([('id','=',int(adv_exp_line.move_id.id))])
            if entry:
                for move in entry:
                    move.state = 'cancel'
            # moves = order.payment_line_ids.filtered(lambda line:line.debit > 0 and line.full_reconcile == True).mapped('move_line_id.move_id')
            # moves.filtered(lambda move: move.state == 'posted').button_draft()
            # moves.with_context(force_delete=True).unlink()
        return res

    @api.model
    def action_set_to_draft(self):
        for rec in self.search([('name', '=', False),('state', '=', 'reconciled')]):
            rec.action_draft()
        return True



    @api.onchange('load_other_transactions','module_ids')
    def get_unrelated_transactions(self):
        for rec in self:
            lines_to_display = []
            line_vals = []
            if rec.method_type =='adjustment' and rec.partner_id:
                if rec.payment_type == 'outbound' and rec.payment_advise == True:
                    if rec.load_other_transactions == True:
                        line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',self.partner_id.id),('move_id.state','not in',['draft','cancel']),('move_id.module_id','in',rec.module_ids.ids)])
                        for line in line_ids:
                            if line.module_id and line.module_id.state not in ['occupied']:
                                if line.lease_agreement_id:
                                    if line.lease_agreement_id.state not in ['active','expired']:
                                        lines_to_display.append(line.id)
                                else:
                                    lines_to_display.append(line.id)
                        if lines_to_display:
                            already_processed = []
                            move_line_ids = self.env['account.move.line'].browse(lines_to_display)
                            for line in move_line_ids:
                                if line.debit > 0:
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
                            payment_lines = self._load_payment_lines()
                            rec.payment_line_ids = [(6, 0, [])]
                            rec.write({'payment_line_ids':payment_lines+line_vals}) 
                        else:
                            payment_lines = self._load_payment_lines()
                            self.payment_line_ids = [(6, 0, [])]
                            self.payment_line_ids = payment_lines
                    else:
                        payment_lines = self._load_payment_lines()
                        self.payment_line_ids = [(6, 0, [])]
                        self.payment_line_ids = payment_lines
                        
            
            # rec.payment_line_ids = [(6, 0, [])]
            
                
        
        
    settlement_date = fields.Date('Settlement Date')
    load_other_transactions = fields.Boolean('Load Other Transactions',default=False)
    # commented by ansu 7714
    from_date = fields.Date('Payment Period')
    to_date = fields.Date('To Date')
    building_ids = fields.Many2many('zbbm.building','building_payment_rel','payment_id','building_id')
    module_ids = fields.Many2many('zbbm.module','module_payment_rel','payment_id','module_id')

class AccountMove(models.Model):
    
    _inherit = 'account.move'
    _description = "Account Invoice Fields Modification"
    
    def get_acc_type_ids(self, journals):
        journal_list=[]
        if journals:
            journals=journals[1:-1].split(',')
            for journal in journals:
                if journal:
                    journal_list.append(int(journal))
        return journal_list
    
    def get_rs_invoice(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.get_acc_type_ids(rs_journal_ids)
        journal_ids = self.get_acc_type_ids(rs_journal_ids)
        action = self.env.ref('account.action_move_out_invoice_type')
        view_id = self.env.ref('zb_building_management.view_account_move_inherit_zb').id 
        return {
            'name': 'Real search Invoice',
            'type': action.type,
            'domain': [('journal_id', 'in', journal_ids)],
            'res_model': 'account.move',
            'view_mode': action.view_mode,
            'target': 'current',
            'res_model': action.res_model,
            'context' : {'default_type': 'out_invoice'},
        } 
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountMove, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        default_type = self._context.get('default_type', False)
        
        if default_type and default_type in ['out_invoice']:
            cus_inv_reports = self.env.ref('zb_account_reports.report_customer_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == cus_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            debit_reports = self.env.ref('zb_bf_custom.report_debit_note')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == debit_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            original_bills = self.env.ref('account.action_account_original_vendor_bill')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == original_bills.id:
                    res['toolbar']['print'].remove(print_submenu)
                    
        if default_type and default_type in ['in_invoice']:
            rent_inv_reports = self.env.ref('zb_bf_custom.report_rent_invoice_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == rent_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            debit_reports = self.env.ref('zb_bf_custom.report_debit_note')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == debit_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            original_bills = self.env.ref('account.action_account_original_vendor_bill')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == original_bills.id:
                    res['toolbar']['print'].remove(print_submenu)
            tax_invoice = self.env.ref('zb_bf_custom.report_tax_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == tax_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)
            commission_invoice = self.env.ref('zb_bf_custom.report_commission_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == commission_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)
            management_invoice = self.env.ref('zb_bf_custom.report_management_fee_invoice_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == management_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)
            tenant_invoice = self.env.ref('zb_bf_custom.report_tenant_deposit_invoice_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == tenant_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)
        
        if default_type and default_type in ['out_receipt']:
            debit_reports = self.env.ref('zb_bf_custom.report_debit_note')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == debit_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
        
        if default_type and default_type in ['out_refund']:
            cus_inv_reports = self.env.ref('zb_account_reports.report_customer_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == cus_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            je_reports = self.env.ref('zb_journal_entry_report.report_journal_entry')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == je_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            rent_inv_reports = self.env.ref('zb_bf_custom.report_rent_invoice_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == rent_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            debit_reports = self.env.ref('zb_bf_custom.report_debit_note')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == debit_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            original_bills = self.env.ref('account.action_account_original_vendor_bill')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == original_bills.id:
                    res['toolbar']['print'].remove(print_submenu)
        
        if default_type and default_type in ['in_refund']:
            vendor_reports = self.env.ref('zb_account_reports.report_vendor_bill')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == vendor_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            je_reports = self.env.ref('zb_journal_entry_report.report_journal_entry')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == je_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            rent_inv_reports = self.env.ref('zb_bf_custom.report_rent_invoice_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == rent_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            tax_inv_reports = self.env.ref('zb_bf_custom.report_tax_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == tax_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            original_bills = self.env.ref('account.action_account_original_vendor_bill')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == original_bills.id:
                    res['toolbar']['print'].remove(print_submenu)
            tax_invoice = self.env.ref('zb_bf_custom.report_tax_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == tax_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)
            commission_invoice = self.env.ref('zb_bf_custom.report_commission_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == commission_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)
            management_invoice = self.env.ref('zb_bf_custom.report_management_fee_invoice_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == management_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)
            tenant_invoice = self.env.ref('zb_bf_custom.report_tenant_deposit_invoice_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == tenant_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)
            
        if default_type and default_type in ['entry']:
            cus_inv_reports = self.env.ref('zb_account_reports.report_customer_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == cus_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            vendor_reports = self.env.ref('zb_account_reports.report_vendor_bill')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == vendor_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            receipt_reports = self.env.ref('zb_account_reports.action_voucher_report')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == receipt_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            rent_inv_reports = self.env.ref('zb_bf_custom.report_rent_invoice_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == rent_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            tax_inv_reports = self.env.ref('zb_bf_custom.report_tax_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == tax_inv_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            debit_reports = self.env.ref('zb_bf_custom.report_debit_note')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == debit_reports.id:
                    res['toolbar']['print'].remove(print_submenu)
            original_bills = self.env.ref('account.action_account_original_vendor_bill')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == original_bills.id:
                    res['toolbar']['print'].remove(print_submenu)
            
        return res          


    def button_payments(self):
        views = [(self.env.ref('account.view_account_payment_tree').id, 'tree'),(self.env.ref('account.view_account_payment_form').id, 'form')]
        
        payments = self.env['account.payment'].search([('invoice_ids','=',self.id)])
        return {
            'name': _('Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in payments])],
        }
    
    
    @api.depends('invoice_line_ids')
    def fetch_product(self):
        count = 1
        for order in self:
            if order.invoice_line_ids:
                for line in order.invoice_line_ids:
                    if count == 1:
                        if line.product_id:
                            order.nature_product_id = line.product_id
                        else:
                            order.nature_product_id = False
                    count+=1
            else:
                order.nature_product_id = False
        
                
    def post(self):
        result = super(AccountMove, self).post()
        params = self.env['ir.config_parameter'].sudo()    
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        ir_model_data = self.env['ir.model.data']
        template_id = ''
        email_validate = False
        # description = ''
        # for lines in self.invoice_line_ids:
        #     if lines.name:
        #         description += lines.name+','
        # description = description[:-1]
        # self.narration = description
        for move in self:
            template_id = move.journal_id.email_template_id.id
            email_validate = move.journal_id.validate_email
            move_line = self.env['account.move.line'].search([('move_id','=',move.name)])
            for move in move_line:
                move.internal_note = move.name
        if template_id:
            if email_validate == True:
                mail_template_obj = self.env['mail.template'].browse(template_id)
                if self.journal_id.id == int(rent_invoice_journal_id):
                    mail_id = mail_template_obj.send_mail(self.id, force_send=True, notif_layout='mail.mail_notification_paynow')
    
        # else:
        #     raise Warning(_('Please provide Assigned user/Email'))
    
        return result
    
    @api.model
    def create(self,vals):
        if vals.get('lease_id'):
            lease = self.env['zbbm.module.lease.rent.agreement'].browse(vals.get('lease_id'))
            vals['owner_id'] = lease.owner_id.id
        
        elif vals.get('module_id'):
            module = self.env['zbbm.module'].browse(vals.get('module_id'))
            vals['owner_id'] = module.owner_id.id
        else:
            vals['owner_id'] = False
        res = super(AccountMove, self).create(vals)
        return res
    
    def button_draft(self):
        # if not self._context.get('default_payment_type') == 'inbound':
        #     if not self._context.get('active_model') == 'zbbm.module.lease.rent.agreement':
        if 'active_model' in self._context and not self._context.get('active_model') == 'zbbm.module.lease.rent.agreement':
            reconciled_lines = self.line_ids._reconciled_lines()
            for lines in reconciled_lines:
                partial_entries = self.env['account.partial.reconcile'].search([('credit_move_id','=',lines)])
                for entry in partial_entries:
                    if entry.reconcilied_payment_id:
                        if entry.reconcilied_payment_id.state == 'posted':
                            raise Warning(_('This transaction is reconciled with the Payment Advise %s, Kindly unreconcile it from Payment Advise'%(entry.reconcilied_payment_id.name)))
        else:
            if 'default_payment_type' not in self._context and 'active_model' not in self._context:
                reconciled_lines = self.line_ids._reconciled_lines()
                for lines in reconciled_lines:
                    partial_entries = self.env['account.partial.reconcile'].search([('credit_move_id','=',lines)])
                    for entry in partial_entries:
                        if entry.reconcilied_payment_id:
                            if entry.reconcilied_payment_id.state == 'posted':
                                raise Warning(_('This transaction is reconciled with the Payment Advise %s, Kindly unreconcile it from Payment Advise'%(entry.reconcilied_payment_id.name)))
        
        
        return super(AccountMove, self).button_draft()
    
    
    is_service_charge = fields.Boolean('Service Charge Invoice',default=False)
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    deposit_jv_desc = fields.Char(string="Description")
    management_fees_boolean = fields.Boolean(string="Management fees",default=False)
    raw_service_id = fields.Many2one('raw.services',string="Service Data")
    # nature_product_id = fields.Many2one('product.product',string="Nature Of Expense",compute='fetch_product')
    nature_product_id = fields.Many2one('product.product',string="Nature Of Expense",compute="fetch_product")
    rent_transfer_id = fields.Many2one('account.move',string="Rent Transfer")
    payment_advise_id = fields.Many2one('account.payment',string="Payment Advise")
    management_fees_move_id = fields.Many2one('account.move',string="Management Fees")
    owner_id = fields.Many2one('res.partner','Owner')
    tax_invoice_fields = fields.Boolean(string="Hide Tax Invoice Fields",default=False)
    show_area_rate = fields.Boolean(string="Show Area and Rate",default=False)
    sellable_unit_id = fields.Many2one('zbbm.unit',string="Sellable Unit")
    report_bank_details = fields.Selection([
                    ('company_bank', 'Company Bank Details'),
                    ('building_bank', 'Building Bank Details'),
                    ], 'Report Bank Details',default='company_bank')
    
    management_fees = fields.Float(string="Management Fee",digits = (12,3),copy=False)
    compare_commission = fields.Boolean('Compared For Commission',default=False)
    invoice_plan_id = fields.Many2one('invoice.plan','Invoice Plan')
   
    

class AccountMoveLine(models.Model):
    
    _inherit = 'account.move.line'
    _description = "Move Line Write Modification"  
    
    
    price_unit = fields.Float(string='Unit Price', digits=(16, 3))
    building_id = fields.Many2one('zbbm.building', 'Building',related="move_id.module_id.building_id",store=True,)
    building_ref_id = fields.Many2one('zbbm.building', 'Building Ref',related="move_id.module_id.building_id",store=True,)
    module_id = fields.Many2one('zbbm.module', 'Module',related="move_id.module_id",store=True,)
    lease_agreement_id = fields.Many2one('zbbm.module.lease.rent.agreement', 'Lease Agreement',related="move_id.lease_id")
    sellable_unit_id = fields.Many2one('zbbm.unit',string="Sellable Unit",related="move_id.unit_id")
    building_module_ref = fields.Char(compute='_get_building_flat', string='Unit',store=True)
    module_building_ref_dummy = fields.Char(compute='_get_building_flat', string='Unit',store=True)
    tax_report_line = fields.Many2one(string="Tax Report Line", comodel_name='account.tax.report.line')
    
    @api.depends('building_id','module_id')
    def _get_building_flat(self):
        for lines in self:
            ref = ''
            if lines.building_ref_id and lines.building_ref_id.code and lines.module_id:
                ref = lines.building_ref_id.code+' '+lines.module_id.name 
            elif lines.building_ref_id and lines.building_ref_id.code and not lines.module_id:
                ref = lines.building_ref_id.code
            elif lines.building_ref_id and lines.module_id:
                ref = lines.module_id.name
            lines.building_module_ref = ref
            lines.module_building_ref_dummy = ref
    
    def generate_payment_advice(self):
        params = self.env['ir.config_parameter'].sudo()    
# PV        entries = self.payment_entries()
        
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        rent_transfer_journal_id = params.get_param('zb_bf_custom.rent_transfer_journal_id') or False
        rent_transfer_product_id = params.get_param('zb_bf_custom.rent_transfer_product_id') or False
        
        product = self.env['product.product'].browse(int(rent_transfer_product_id))
        
        deposit_product_id = params.get_param('zb_bf_custom.deposit_product_id') or False
        
        deposit_product = self.env['product.product'].browse(int(deposit_product_id))
        
        deposit_journal_id = params.get_param('zb_bf_custom.deposit_journal_id') or False

        
        building_journal_id = params.get_param('zb_bf_custom.building_journal_id') or False
        
        resale_commission_journal_id = params.get_param('zb_bf_custom.resale_commission_journal_id') or False
        resale_commission_product_id = params.get_param('zb_bf_custom.resale_commission_product_id') or False
        
        installment_journal_id = params.get_param('zb_bf_custom.installment_journal_id') or False
        installment_product_id = params.get_param('zb_bf_custom.installment_product_id') or False
        
        new_install_journal = params.get_param('zb_bf_custom.install_journal_id') or False
        
        advance_journal_id = params.get_param('zb_bf_custom.advance_payment_journal_id') or False
        advance_product_id = params.get_param('zb_bf_custom.advance_product_id') or False
        
        advance_transfer_journal = params.get_param('zb_bf_custom.advance_transfer_journal_id') or False
        
        
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
        
        building_journal = self.env['account.journal'].browse(int(building_journal_id))
        if not building_journal_id:
            raise Warning(_('Please Configure Building Bank Journal'))
        
        lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
        date_format = lang_id.date_format
        
        
        for line in  self:
            inv_date = ''
            if line.move_id.invoice_date:
                inv_date = datetime.strptime(str(line.move_id.invoice_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            if line.move_id.journal_id.id == int(installment_journal_id):
                product = self.env['product.product'].browse(int(installment_product_id))
                debit_val =  {
                        'account_id':product.property_account_income_id.id,
                        'analytic_account_id':line.move_id.building_id.analytic_account_id.id or '',
                        'partner_id':line.move_id.unit_id.owner_id.id,
                        'name':'%s'%(line.move_id.name),
                        'debit':line.move_id.amount_total,
                        'credit':0.000,
                         }
                    
                credit_val = {
                            'account_id': line.move_id.unit_id.owner_id.property_account_receivable_id.id,
                            'analytic_account_id':line.move_id.building_id.analytic_account_id.id or '',
                            'partner_id':line.move_id.unit_id.owner_id.id,
                            'name':'Installment Details  on %s to %s'%(inv_date,line.move_id.unit_id.owner_id.name),
                            'debit':0.000,
                            'credit':line.move_id.amount_total,
                             }
                
                jv_vals = {
                    'partner_id': line.move_id.unit_id.owner_id.id,
                    'type': 'entry',
                    'invoice_date':datetime.today(),
                    'from_date':datetime.today(),
                    'to_date':datetime.today(),
                    'unit_id': line.move_id.unit_id.id,
                    'building_id':line.move_id.building_id.id,
                    'ref':'Installment Details on %s to %s'%(inv_date,line.move_id.unit_id.owner_id.name),
                    'journal_id':int(new_install_journal),
                    'line_ids': [(0, 0,debit_val),
                                 (0, 0,credit_val)],
                    }
                move_id = self.env['account.move'].create(jv_vals) 
                move_id.action_post()
                
            # Transfer creation for 100% advance payment for sellable unit
            elif line.move_id.journal_id.id == int(advance_journal_id):
                line.move_id.unit_id.state_change()
                product = self.env['product.product'].browse(int(advance_product_id))
                advance_debit_val =  {
                        'account_id':product.property_account_income_id.id,
                        'analytic_account_id':line.move_id.building_id.analytic_account_id.id or '',
                        'partner_id':line.move_id.unit_id.owner_id.id,
                        'name':'%s'%(line.move_id.name),
                        'debit':line.move_id.amount_total,
                        'credit':0.000,
                         }
                    
                advance_credit_val = {
                            'account_id': line.move_id.unit_id.owner_id.property_account_receivable_id.id,
                            'analytic_account_id':line.move_id.building_id.analytic_account_id.id or '',
                            'partner_id':line.move_id.unit_id.owner_id.id,
                            'name':'Advance Payment Details  on %s to %s'%(inv_date,line.move_id.unit_id.owner_id.name),
                            'debit':0.000,
                            'credit':line.move_id.amount_total,
                             }
                
                advance_jv_vals = {
                    'partner_id': line.move_id.unit_id.owner_id.id,
                    'type': 'entry',
                    'invoice_date':datetime.today(),
                    'unit_id': line.move_id.unit_id.id,
                    'building_id':line.move_id.building_id.id,
                    'ref':'Advance Payment Details on %s to %s'%(inv_date,line.move_id.unit_id.owner_id.name),
                    'journal_id':int(advance_transfer_journal),
                    'line_ids': [(0, 0,advance_debit_val),
                                 (0, 0,advance_credit_val)],
                    }
                advance_move_id = self.env['account.move'].create(advance_jv_vals) 
                advance_move_id.action_post()
                
                    
            # commented as per creation of deposit transfer   
            # if line.move_id.journal_id.id == int(rent_invoice_journal_id):
            #     if line.move_id.module_id and line.move_id.module_id.owner_id:
            #         if line.move_id.module_id.building_id.analytic_account_id:
            #             analytic = line.move_id.module_id.building_id.analytic_account_id.id
            #         else:
            #             analytic = '' 
            #
            #         amount_total = line.move_id.amount_total
            #
            #         if not line.move_id.lease_id.managed:
            #             if line.move_id.lease_id.security_deposit:
            #                 deposit_debit_val = {
            #                             'account_id':deposit_product.property_account_income_id.id,
            #                             'analytic_account_id':analytic,
            #                             'partner_id':line.move_id.module_id.owner_id.id,
            #                             'name':'%s'%(line.move_id.name),
            #                             'debit':0.000 if line.move_id.type=='out_refund' else line.move_id.lease_id.security_deposit,
            #                             'credit':line.move_id.lease_id.security_deposit if line.move_id.type=='out_refund' else 0.000,
            #                              }
            #
            #                 deposit_credit_val = {
            #                             'account_id': line.move_id.module_id.owner_id.property_account_receivable_id.id,
            #                             'analytic_account_id':analytic,
            #                             'partner_id':line.move_id.module_id.owner_id.id,
            #                             'name':'Rent transfer on %s to %s'%(line.move_id.invoice_date,line.move_id.module_id.owner_id.name),
            #                             'debit':line.move_id.lease_id.security_deposit if line.move_id.type=='out_refund' else 0.000,
            #                             'credit':0.000 if line.move_id.type=='out_refund' else line.move_id.lease_id.security_deposit,
            #                              }
            #
            #
            #                 deposit_jv_vals = {
            #                     'partner_id': line.move_id.module_id.owner_id.id,
            #                     'type': 'entry',
            #                     'invoice_date':datetime.today(),
            #                     'from_date':datetime.today(),
            #                     'to_date':datetime.today(),
            #                     'module_id': line.move_id.module_id.id,
            #                     'lease_id':line.move_id.lease_id.id,
            #                     'building_id':line.move_id.module_id.building_id.id,
            #                     'ref':'Security deposit on %s to %s'%(line.move_id.invoice_date,line.move_id.module_id.owner_id.name),
            #                     'journal_id':int(deposit_journal_id),
            #                     'line_ids': [(0, 0,deposit_debit_val),
            #                                  (0, 0,deposit_credit_val)],
            #                     }
            #                 move_id = self.env['account.move'].create(deposit_jv_vals) 
            #                 move_id.action_post()
            #                 line.move_id.lease_id.voucher_move_id = move_id.id
            #
            #
            #
            #         currnet_user = self.env['res.users'].browse(self._uid)
            #         company_id = currnet_user.company_id
                    
    
    
    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        if vals.get('full_reconcile_id'):
            self.generate_payment_advice()
        return res
        
    
     
class AccountReconcilePartial(models.Model):
    
    _inherit = 'account.partial.reconcile'
    _description = "Account reconcile Write Modification"  
    
            
    rent_transfer_id = fields.Many2one('account.move',string='Rent Transfer')
    payment_advise_id = fields.Many2one('account.payment',string="Payment Advise")
    management_fees_move_id = fields.Many2one('account.move',string="Management Fees")
    management_fees = fields.Float(string="Management Fee",digits = (12,3),copy=False)
    reconcilied_payment_id = fields.Many2one('account.payment',string='Reconciled Payment')
    
    
    def create(self, vals):
        
        params = self.env['ir.config_parameter'].sudo()    
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        rent_deposit_journal_id = params.get_param('zb_bf_custom.deposit_journal_id') or False
        move = self.env['account.move.line'].browse(vals.get('debit_move_id'))
        if move.move_id.journal_id.id == int(rent_invoice_journal_id):
            if vals.get('amount'):
                self._get_payments_widget_reconciled_info(vals)
        
        credit_move = self.env['account.move.line'].browse(vals.get('credit_move_id'))        
        if credit_move.move_id.journal_id.id == int(rent_invoice_journal_id) and credit_move.move_id.type == 'out_refund':
            vasls = self._get_reverse_rent_transfer(credit_move.move_id,vals.get('amount'),vals)
            
        # deposit transfer creation
        if move.move_id.journal_id.id == int(rent_deposit_journal_id):
            if vals.get('amount'):
                self._get_payments_widget_reconciled_info(vals)
        
        
        return super(AccountReconcilePartial, self).create(vals)
    
    def _get_reverse_rent_transfer(self, move, amt, vals):
        
        params = self.env['ir.config_parameter'].sudo()    
        rent_transfer_journal_id = params.get_param('zb_bf_custom.rent_transfer_journal_id') or False
        rent_transfer_product_id = params.get_param('zb_bf_custom.rent_transfer_product_id') or False
        product = self.env['product.product'].browse(int(rent_transfer_product_id))
        
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        
        currnet_user = self.env['res.users'].browse(self._uid)
        company_id = currnet_user.company_id
        
        building_journal_id = params.get_param('zb_bf_custom.building_journal_id') or False
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
        
        building_journal = self.env['account.journal'].browse(int(building_journal_id))
        if not building_journal_id:
            raise Warning(_('Please Configure Building Bank Journal'))
        
        invoice_ids  = self.env['account.move.line'].browse(move)
        
        lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
        date_format = lang_id.date_format
        
        rt_inv_date = datetime.strptime(str(move.invoice_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            
        if move.module_id and move.module_id.owner_id:
            # RT creation
            amount = amt
            payment_date = ''

            if move.module_id.building_id.analytic_account_id:
                analytic = move.module_id.building_id.analytic_account_id.id
            else:
                analytic = '' 
                
            owner_id = self.env['res.partner'].get_owner_id(move.module_id,move.lease_id)
            
            # if move.module_id.flat_on_offer == True:
            #     owner_id = config_owner_id
            #     owner_obj = self.env['res.partner'].browse(int(partner_id))
            # else:
            #     owner_id = move.module_id.owner_id
            #     owner_obj = self.env['res.partner'].browse(int(partner_id))
            
            debit_val =  {
                'account_id':product.property_account_income_id.id,
                'analytic_account_id':analytic,
                'partner_id':owner_id.id,
                'name':'%s'%(move.name),
                'debit':0.000 if move.type=='out_refund' else amount,
                'credit':amount if move.type=='out_refund' else 0.000,
                 }
             
            credit_val = {
                        'account_id': owner_id.property_account_receivable_id.id,
                        'analytic_account_id':analytic,
                        'partner_id':owner_id.id,
                        'name':'Reverse Rent transfer on %s to %s'%(rt_inv_date,owner_id.name),
                        'debit':amount if move.type=='out_refund' else 0.000,
                        'credit':0.000 if move.type=='out_refund' else amount,
                         }
            jv_vals = {
                'partner_id': owner_id.id,
                'type': 'entry',
                'invoice_date': move.invoice_date,
                'date': move.invoice_date,
                'from_date':datetime.today(),
                'to_date':datetime.today(),
                'module_id': move.module_id.id,
                'lease_id': move.lease_id.id,
                'building_id':move.module_id.building_id.id,
                'ref':'Reverse Rent transfer on %s to %s'%(rt_inv_date,owner_id.name),
                'journal_id':int(rent_transfer_journal_id),
                'line_ids': [(0, 0,debit_val),
                             (0, 0,credit_val)],
                }
            if move.lease_id.managed:
                move_id = self.env['account.move'].create(jv_vals) 
                move.rent_transfer_id = move_id.id
                vals.update({'rent_transfer_id' : move_id.id})
                move_id.action_post()
        return vals        

    
    def create_transfer(self,vals):
        params = self.env['ir.config_parameter'].sudo() 
        deposit_product_id = params.get_param('zb_bf_custom.deposit_product_id') or False
        deposit_product = self.env['product.product'].browse(int(deposit_product_id))
        rent_deposit_journal_id = params.get_param('zb_bf_custom.deposit_journal_id') or False
        deposit_transfer_journal = params.get_param('zb_bf_custom.deposit_transfer_journal_id') or False
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
        if not deposit_transfer_journal:
            raise Warning(_('Please Configure Deposit Transfer Journal'))
        move_line_id = vals.get('debit_move_id')
        move_line = self.env['account.move.line'].browse(move_line_id)
        amount = vals.get('amount')
        payment_date = ''
        if vals.get('credit_move_id'):
            credit_move = self.env['account.move.line'].browse(vals.get('credit_move_id'))
            payment_date = credit_move.date
        if move_line.move_id.building_id.analytic_account_id:
            analytic = move_line.move_id.building_id.analytic_account_id.id
        else:
            analytic = False
            
        owner_id = self.env['res.partner'].get_owner_id(move_line.move_id.module_id,move_line.move_id.lease_id)
        
        lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
        date_format = lang_id.date_format
        
        deposit_inv_date = datetime.strptime(str(move_line.move_id.invoice_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        
        # if move_line.move_id.module_id.flat_on_offer == True:
        #     owner_id = config_owner_id
        #     owner_obj = self.env['res.partner'].browse(int(owner_id))
        # else:
        #     owner_id = move_line.move_id.module_id.owner_id
        #     owner_obj = self.env['res.partner'].browse(int(owner_id))
            
        deposit_debit_val =  {
            'account_id':deposit_product.property_account_income_id.id,
            'analytic_account_id':analytic,
            'partner_id':move_line.move_id.partner_id.id,
            'name':'%s'%(move_line.move_id.name),
            'debit':0.000 if move_line.move_id.type=='out_refund' else amount,
            'credit':amount if move_line.move_id.type=='out_refund' else 0.000,
             }
         
        deposit_credit_val = {
                    'account_id': owner_id.property_account_receivable_id.id,
                    'analytic_account_id':analytic,
                    'partner_id':owner_id.id,
                    'name':'Deposit transfer on %s to %s'%(deposit_inv_date,owner_id.name),
                    'debit':amount if move_line.move_id.type=='out_refund' else 0.000,
                    'credit':0.000 if move_line.move_id.type=='out_refund' else amount,
                     }
        deposit_jv_vals = {
            'partner_id': owner_id.id,
            'type': 'entry',
            'invoice_date':payment_date,
            'date':payment_date,
            'from_date':datetime.today(),
            'to_date':datetime.today(),
            'module_id': move_line.move_id.module_id.id,
            'lease_id':move_line.move_id.lease_id.id,
            'building_id':move_line.move_id.module_id.building_id.id,
            'ref':'Deposit transfer on %s to %s'%(deposit_inv_date,owner_id.name),
            'journal_id':int(deposit_transfer_journal),
            'line_ids': [(0, 0,deposit_debit_val),
                         (0, 0,deposit_credit_val)],
            }
        deposit_move_id = self.env['account.move'].create(deposit_jv_vals) 
        deposit_move_id.action_post()
    
    
    
    
    def _get_payments_widget_reconciled_info(self,value):
        
        params = self.env['ir.config_parameter'].sudo()   
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False 
        rent_deposit_journal_id = params.get_param('zb_bf_custom.deposit_journal_id') or False
        rent_transfer_journal_id = params.get_param('zb_bf_custom.rent_transfer_journal_id') or False
        rent_transfer_product_id = params.get_param('zb_bf_custom.rent_transfer_product_id') or False
        lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
        date_format = lang_id.date_format
        
        product = self.env['product.product'].browse(int(rent_transfer_product_id))
        
        management_fee_journal_id = params.get_param('zb_bf_custom.management_fee_journal_id') or False
        management_product_id = params.get_param('zb_bf_custom.management_product_id') or False
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        
        mngmnt_pdt = self.env['product.product'].browse(int(management_product_id))
        currnet_user = self.env['res.users'].browse(self._uid)
        company_id = currnet_user.company_id
        
        building_journal_id = params.get_param('zb_bf_custom.building_journal_id') or False
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
        
        building_journal = self.env['account.journal'].browse(int(building_journal_id))
        if not building_journal_id:
            raise Warning(_('Please Configure Building Bank Journal'))
        
        move_line_id = value.get('debit_move_id')
        move_line = self.env['account.move.line'].browse(move_line_id)
        if move_line.move_id.journal_id.id == int(rent_invoice_journal_id):
            if move_line.move_id.module_id and move_line.move_id.module_id.owner_id:
                
                # RT creation
                
                rt_from_date = datetime.strptime(str(move_line.move_id.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                rt_to_date = datetime.strptime(str(move_line.move_id.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                inv_date = datetime.strptime(str(move_line.move_id.invoice_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                amount = value.get('amount')
                payment_date = ''
                if value.get('credit_move_id'):
                    credit_move = self.env['account.move.line'].browse(value.get('credit_move_id'))
                    payment_date = credit_move.date
    
                if move_line.move_id.module_id.building_id.analytic_account_id:
                    analytic = move_line.move_id.module_id.building_id.analytic_account_id.id
                else:
                    analytic = '' 
                    
                owner_id = self.env['res.partner'].get_owner_id(move_line.move_id.module_id,move_line.move_id.lease_id)
                
                # if move_line.move_id.module_id.flat_on_offer == True:
                #     owner_id = config_owner_id
                #     owner_obj = self.env['res.partner'].browse(int(owner_id))
                # else:
                #     owner_id = move_line.move_id.module_id.owner_id
                #     owner_obj = self.env['res.partner'].browse(int(owner_id))
                    
                debit_val =  {
                    'account_id':product.property_account_income_id.id,
                    'analytic_account_id':analytic,
                    'partner_id':owner_id.id,
                    'name':'%s'%(move_line.move_id.name),
                    'debit':0.000 if move_line.move_id.type=='out_refund' else amount,
                    'credit':amount if move_line.move_id.type=='out_refund' else 0.000,
                     }
                 
                credit_val = {
                            'account_id': owner_id.property_account_receivable_id.id,
                            'analytic_account_id':analytic,
                            'partner_id':owner_id.id,
                            'name':'Rent transfer on %s to %s'%(inv_date,owner_id.name),
                            'debit':amount if move_line.move_id.type=='out_refund' else 0.000,
                            'credit':0.000 if move_line.move_id.type=='out_refund' else amount,
                             }
                jv_vals = {
                    'partner_id': owner_id.id,
                    'type': 'entry',
                    'invoice_date':payment_date,
                    'date':payment_date,
                    'from_date':move_line.move_id.from_date,
                    'to_date':move_line.move_id.to_date,
                    'module_id': move_line.move_id.module_id.id,
                    'lease_id':move_line.move_id.lease_id.id,
                    'building_id':move_line.move_id.module_id.building_id.id,
                    'ref':'Rent transfer for the period from %s to %s'%(rt_from_date,rt_to_date),
                    'journal_id':int(rent_transfer_journal_id),
                    'line_ids': [(0, 0,debit_val),
                                 (0, 0,credit_val)],
                    }
    
                move_id = self.env['account.move'].create(jv_vals) 
                move_id.action_post()
                self.rent_transfer_id = move_id.id
                value.update({'rent_transfer_id':move_id.id})
                    
                #Management fee move creation
                
                last_date = move_line.move_id.invoice_date
                updated_last_date = datetime.strptime(str(move_line.move_id.invoice_date), '%Y-%m-%d')
                if not building_income_account_id:
                    journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                    if journal :
                        acct_id = journal[0].default_credit_account_id.id
                else:
                    acct_id = int(building_income_account_id)
                    
                mf_from_date = datetime.strptime(str(move_line.move_id.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                mf_to_date = datetime.strptime(str(move_line.move_id.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                description = 'Management Fee for the Period from %s to %s'%(mf_from_date,mf_to_date)
                params = self.env['ir.config_parameter'].sudo()        
                tax_ids = params.get_param('zb_building_management.default_rental_tax_ids') or False,
                if tax_ids[0]:
                    temp = re.findall(r'\d+', tax_ids[0]) 
                    tax_list = list(map(int, temp))
                
                amount_total = 0
                payment_values = move_line.move_id._get_reconciled_info_JSON_values()
                if payment_values:
                    for data in payment_values:
                        amount_total += data['amount']
                    total = amount_total + amount                                                                                                                                                                                                         
                else:
                    total = amount
                mngmnt_amount = 0
                if move_line.move_id.lease_id.commission_move_id:
                    commission_mov_amt = move_line.move_id.lease_id.commission_move_id.amount_untaxed
                else:
                    commission_mov_amt = 0
                if move_line.move_id.type in ['out_invoice']:
                    rent_transfer_ids = self.env['account.move'].search([('type','=','entry'),('lease_id','=',move_line.move_id.lease_id.id),('module_id','=',move_line.move_id.module_id.id)])
                    total_paid_amount = 0
                    
                    for rt_move in rent_transfer_ids:
                        rent_transfer_move_lines = self.env['account.move.line'].search([('move_id.state','=','posted'),('move_id','=',rt_move.id)])
                        for line in rent_transfer_move_lines:
                            total_paid_amount += line.debit

                    if move_line.move_id.lease_id.is_commission == True:
                        mngmnt_amount = amount
                    
                    else:
                        if commission_mov_amt:
                            # commission_mov_amt
                            if total_paid_amount - commission_mov_amt > 0:
                                mngmnt_amount = total_paid_amount - commission_mov_amt
                                move_line.move_id.lease_id.is_commission = True
                            else:
                                mngmnt_amount = 0
                        else:
                            mngmnt_amount = amount
                                # if move_line.move_id.amount_residual - amount == 0:
                                #     move_line.move_id.lease_id.is_commission = True
                                #     move_line.move_id.compare_commission = True
                                # else:
                                #     if total_paid_amount >= commission_mov_amt:
                                #         move_line.move_id.lease_id.is_commission = True
                                #         move_line.move_id.compare_commission = True
                            
                                # if move_line.move_id.amount_total - total_paid_amount == 0:
                                #     move_line.move_id.lease_id.is_commission = True
                                #     move_line.move_id.compare_commission = True
                                # else:
                                #     if total_paid_amount >= commission_mov_amt:
                                #         move_line.move_id.lease_id.is_commission = True
                                #         move_line.move_id.compare_commission = True
                                
                        
                move_line.move_id.management_fees = mngmnt_amount
                pay_amount = 0
                if mngmnt_amount > 0:
                    perc = move_line.move_id.module_id.management_fees_percent/100
                    pay_amount = mngmnt_amount * perc
                
                if pay_amount:
                    vals = {
                          'partner_id': owner_id.id,
                          'type': 'out_invoice',
                          'invoice_date': payment_date,
                          'from_date':move_line.move_id.from_date,
                          'to_date':move_line.move_id.to_date,
                          'building_id': move_line.move_id.module_id.building_id.id,
                          'module_id': move_line.move_id.module_id.id,
                          'lease_id':move_line.move_id.lease_id.id,
                          'comment': description,
                          'journal_id':int(management_fee_journal_id),
                          'management_fees_boolean':True,
                          'invoice_line_ids': [(0, 0, {
                                                'product_id':int(management_product_id),
                                                'name': description,
                                                'price_unit': pay_amount,
                                                'tax_ids' : mngmnt_pdt.taxes_id.ids,
                                                'quantity': 1,
                                                'account_analytic_id':move_line.move_id.module_id.building_id.analytic_account_id.id if move_line.move_id.module_id.building_id.analytic_account_id else '',
                                                'account_id':mngmnt_pdt.property_account_income_id.id,
                                                })],
                        }
                    if move_line.move_id.lease_id.managed:
                        if pay_amount > 0:
                            mngmt_invoice_id = self.env['account.move'].create(vals)
                            for line in mngmt_invoice_id.line_ids:
                                if line.credit > 0.000:
                                    # line.partner_id = company_id.partner_id. - as per 6351-Neha
                                    if line.move_id.type=='out_refund':
                                        line.credit = 0.000
                                        line.debit = pay_amount
                                if line.debit > 0.000:
                                    if line.move_id.type=='out_refund':
                                        line.credit = pay_amount
                                        line.debit = 0.000 
                                    
                            # mngmt_invoice_id.action_post()
                            move_line.move_id.management_fees_move_id = mngmt_invoice_id.id
                            move_line.move_id.lease_id.management_move_id = mngmt_invoice_id.id
                            value.update({'management_fees_move_id':mngmt_invoice_id.id})
                            
                    move_line.move_id.lease_id.commission_generated = True
                
                #payment advise invoice creation 
                journal_id = self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('type', 'in', ('bank', 'cash'))], limit=1).id
                domain = [('payment_type', '=', 'outbound')]
                payment_method_id= self.env['account.payment.method'].search(domain, limit=1).id
                
                owner_payment_vals = {
                    'payment_type':'outbound',
                    'payment_date':datetime.today(),
                    'partner_id':owner_id.id,
                    'lease_id':move_line.move_id.lease_id.id,
                    'amount':amount,
                    'payment_advise':True,
                    'method_type':'adjustment',
                    'partner_type':'customer',
                    'building_id':move_line.move_id.module_id.building_id.id,
                    'module_id':move_line.move_id.module_id.id,
                    'payment_method_id':payment_method_id,
                    'journal_id':int(building_journal_id),
                    'journal_type':'bank',
                    'owner_id':owner_id.id,
                    'cheque_bank_id':building_journal.bank_id.id,
                    'notes' : 'Payment Advice to %s against Rent Invoice %s'%(owner_id.name,move_line.move_id.name)
    
                    }
                payment_advise = self.env['account.payment'].search([('payment_advise','=',True),('lease_id','=',move_line.move_id.lease_id.id),('state','=','draft')])
                if not payment_advise:
                    payment = self.env['account.payment'].create(owner_payment_vals)
                    payment._onchange_partner_id()
                    payment.with_context(create_pa=True)._onchange_payment_line_ids()
                    move_line.move_id.payment_advise_id = payment.id
                    move_line.move_id.lease_id.payment_advise_id = payment.id
                    value.update({'payment_advise_id':payment.id})
                else:
                    payment_advise.reload_lines()
                    payment_advise._onchange_payment_line_ids()
        
        elif move_line.move_id.journal_id.id == int(rent_deposit_journal_id):
            if move_line.move_id.lease_id.managed == False:
                self.create_transfer(value)
    
    def unlink(self):
        for rec in self:
            print('=============Unlink================',rec._context)
            # if not rec._context.get('default_payment_type') == 'inbound':
            #     if not rec._context.get('active_model') == 'zbbm.module.lease.rent.agreement':
            if 'active_model' in rec._context and not rec._context.get('active_model') == 'zbbm.module.lease.rent.agreement':
                if rec.reconcilied_payment_id:
                    if rec.reconcilied_payment_id.state == 'posted':
                        raise Warning(_('This transaction is reconciled with the Payment Advise %s, Kindly unreconcile it from Payment Advise'%(rec.reconcilied_payment_id.name)))
            else:
                if 'default_payment_type' not in rec._context and 'active_model' not in rec._context:
                    if rec.reconcilied_payment_id:
                        if rec.reconcilied_payment_id.state == 'posted':
                            raise Warning(_('This transaction is reconciled with the Payment Advise %s, Kindly unreconcile it from Payment Advise'%(rec.reconcilied_payment_id.name)))
            rent_tranfer = rec.rent_transfer_id
            lines=rec.rent_transfer_id.mapped('line_ids')
            payment_advise = rec.payment_advise_id
            mngmnt_entry = rec.management_fees_move_id
            mngmnt_entry_lines = rec.management_fees_move_id.mapped('line_ids')
            rec.debit_move_id.move_id.lease_id.is_commission = False
            rec.debit_move_id.move_id.compare_commission = False
            if rent_tranfer:
                rent_tranfer.button_cancel()
                lines.unlink()
            if payment_advise:
                payment_advise.unlink()
            if mngmnt_entry:
                mngmnt_entry.button_cancel()
                mngmnt_entry_lines.unlink()
                rec.debit_move_id.move_id.management_fees = rec.debit_move_id.move_id.management_fees - rec.management_fees
        return super(AccountReconcilePartial, self).unlink()

    
    
class AccountJournal(models.Model):
    _inherit = ['account.journal']
    

    email_template_id = fields.Many2one('mail.template', string='Invoice Email Template', copy=False, help='Configuration for Email Template for Sending Mailbased on Journal')
    validate_email = fields.Boolean('Send mail on invoice validation',default=False)
    
       
class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'
    _description = 'Account Move Reversal'

    mf_notice = fields.Char(string='Notice')

    @api.model
    def default_get(self, fields):
        params = self.env['ir.config_parameter'].sudo()  
        res = super(AccountMoveReversal, self).default_get(fields)
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        if not rent_invoice_journal_id:
            raise Warning(_('Please Configure Rent Invoice Journal'))
        mf_notice = False
        move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.env['account.move']
        for move in move_ids:
            if move.journal_id.id == int(rent_invoice_journal_id):
               mf_notice = True
               break
        if mf_notice:  
            res['mf_notice'] = 'Please do create Credit Note for Management Fees Invoices'
        return res
    
class generic_tax_report(models.AbstractModel):
    _inherit = "account.generic.tax.report"
    _description = 'Generic Tax Report'

    def _sql_tax_amt_regular_taxes(self):
        sql = """SELECT "account_move_line".tax_line_id,COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM account_tax tax, %s
                    JOIN account_journal journal ON journal.id = account_move_line.journal_id
                    WHERE %s AND tax.tax_exigibility = 'on_invoice' AND tax.id = "account_move_line".tax_line_id
                    AND journal.type = tax.type_tax_use
                    GROUP BY "account_move_line".tax_line_id"""
        return sql
    
    def _sql_net_amt_regular_taxes(self):
        return '''
            SELECT
                tax.id,
                 COALESCE(SUM(account_move_line.balance))
            FROM %s
            JOIN account_move_line_account_tax_rel rel ON rel.account_move_line_id = account_move_line.id
            JOIN account_tax tax ON tax.id = rel.account_tax_id
            JOIN account_journal journal ON journal.id = account_move_line.journal_id
            WHERE %s AND tax.tax_exigibility = 'on_invoice'
            AND journal.type = tax.type_tax_use
            GROUP BY tax.id

            UNION ALL

            SELECT
                child_tax.id,
                 COALESCE(SUM(account_move_line.balance))
            FROM %s
            JOIN account_move_line_account_tax_rel rel ON rel.account_move_line_id = account_move_line.id
            JOIN account_tax tax ON tax.id = rel.account_tax_id
            JOIN account_tax_filiation_rel child_rel ON child_rel.parent_tax = tax.id
            JOIN account_tax child_tax ON child_tax.id = child_rel.child_tax
            WHERE %s
                AND child_tax.tax_exigibility = 'on_invoice'
                AND tax.amount_type = 'group'
                AND child_tax.amount_type != 'group'
            GROUP BY child_tax.id
        '''
    
    
