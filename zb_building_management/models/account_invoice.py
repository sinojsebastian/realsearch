# -*- coding: utf-8 -*-
##############################################
#
# Inforise IT & ZestyBeanz Technologies Pvt. Ltd
# By Sinoj Sebastian (sinoj@zbeanztech.com, sinoj@inforiseit.com)
# First Version 2020-08-13
# Website1 : http://www.zbeanztech.com
# Website2 : http://www.inforiseit.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from odoo import models, fields, api,exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools.misc import formatLang, format_date, get_lang

# from odoo.osv.orm import setup_modifiers
from time import strptime
import datetime
from dateutil import relativedelta
from lxml import etree
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date, timedelta
from num2words import num2words

class AccountMove(models.Model):
    
    _inherit = 'account.move'
    _description = "Account Invoice Fields Modification"

    
    def button_payments(self):
        views = [(self.env.ref('account.view_account_payment_tree').id, 'tree'), (self.env.ref('account.view_account_payment_form').id, 'form')]
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
        
        
    
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        
        if self.journal_id and self.journal_id.email_template_id:
            template = self.journal_id.email_template_id
        else:
            template = self.env.ref('zb_building_management.email_template_edi_invoice_account', raise_if_not_found=False)
           
        lang = get_lang(self.env)
        if template and template.lang:
            lang = template._render_template(template.lang, 'account.move', self.id)
        else:
            lang = lang.code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True
        )
        return {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }




# DB    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
#                  'currency_id', 'company_id', 'date_invoice', 'type')
#     def _compute_amount(self):
#         round_curr = self.currency_id.round
#         if self.type=='out_invoice' and self.building_id:
# #         if self.building_id:
#             self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
# #         else:
# #             self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
#             self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
#             self.amount_total = self.amount_untaxed + self.amount_tax
#             amount_total_company_signed = self.amount_total
#             amount_untaxed_signed = self.amount_untaxed
#             if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
#                 currency_id = self.currency_id.with_context(date=self.date_invoice)
#                 amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
#                 amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
#             sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
#             self.amount_total_company_signed = amount_total_company_signed * sign
#             self.amount_total_signed = self.amount_total * sign
#             self.amount_untaxed_signed = amount_untaxed_signed * sign
#         else:
#             res = super(AccountMove, self)._compute_amount()
# 
#     
    
    
    def amount_to_text(self):
        for record in self:
            amount_untaxed = '%.3f' % record.amount_total
            list = str(amount_untaxed).split('.')
            first_part = False
            second_part = False
            if num2words(int(list[0])):
                first_part = num2words(int(list[0])).title()
            if num2words(int(list[1])):
                second_part = num2words(int(list[1])).title()
            amount_in_words = ' Bahrain Dinar '
            if first_part:
                amount_in_words =  str(first_part) + amount_in_words 
            else:
                amount_in_words =  'Zero' + amount_in_words 
            if second_part:
                if list[1] != '000':
                    amount_in_words = amount_in_words + ' and ' +str(list[1]) + ' Fils ' 
                #amount_in_words = ' ' + amount_in_words + ' and Fils ' + str(second_part) 
            record.amount_total_words=  amount_in_words
    
    


#     invoice_line_dates_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines',
#         readonly=True, states={'draft': [('readonly', False)]})
    
    billed_date = fields.Date('Billed Date')
    amount_total_words = fields.Char('Amount in Words',compute='amount_to_text')
    is_company = fields.Boolean('Report Name',default=False)
    comment = fields.Text(string="Comment")
    
#     amount_total_signed = fields.Monetary(string='Amount', currency_field='currency_id',
#         store=True, readonly=True, compute='_compute_amount',
#         help="Total amount in the currency of the invoice, negative for credit notes.")
    
#DB     cheque_no = fields.Char(string='Cheque No')
#     cheque_date = fields.Date(string='Cheque Date')
#     cheque_bank_id = fields.Many2one('res.bank',string='Cheque Bank')    
#     journal_type = fields.Selection([
#             ('sale', 'Sale'),
#             ('purchase', 'Purchase'),
#             ('cash', 'Cash'),
#             ('bank', 'Bank'),
#             ('general', 'Miscellaneous'),
#         ],string='Type',compute='compute_journal_type', store=True)
    
    
#     lis = {}
    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         print('++++++++++++++++',self._context)
        doc = etree.XML(res['arch'])
        if self._context.get('rent') =='yes':
            for node in doc.xpath("//field[@name='partner_id']"):
                user_filter =  "[('is_tenant', '=',True )]"
                node.set('domain',user_filter)
        if self._context.get('rent') =='no':
            for node in doc.xpath("//field[@name='partner_id']"):
                user_filter =  "[('is_tenant', '=',False )]"
                node.set('domain',user_filter)
                
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res       
                
           
    
    def invoice_legal(self):
        for inv in self:
            joun_itm = self.env['account.move.line'].search([('move_id','=',inv.id)])
            receivable_ids = self.env.ref('account.data_account_type_receivable')
            if joun_itm:
                for all in joun_itm:
                    if all.account_id.user_type_id.id ==receivable_ids.id:
                        all.blocked = True
                        inv.is_legal =True
            
            
    def invoice_legal_un(self):
        for inv in self:
            joun_itm = self.env['account.move.line'].search([('move_id','=',inv.id)])
            if joun_itm:
                for all in joun_itm:
                    all.blocked = False
                inv.is_legal =False
    
 

#DB     def finalize_invoice_move_lines(self, move_lines):
#         
#         
#         
#         print("move_linesmove_lines",move_lines[0][2])
#         """ finalize_invoice_move_lines(move_lines) -> move_lines
# 
#             Hook method to be overridden in additional modules to verify and
#             possibly alter the move lines to be created by an invoice, for
#             special cases.
#             :param move_lines: list of dictionaries with the account.move.lines (as for create())
#             :return: the (possibly updated) final move_lines to create for this invoice
#         """
#        
#         move_lines[0][2]['building_id']=self.building_id.id
# #         move_lines = [(0,0,move_lines_2)]
#         return move_lines
#      
     
     
#DB     @api.model
#     def invoice_line_move_line_get(self):
#         res = []
#         for line in self.invoice_line_ids:
#             if line.quantity==0:
#                 continue
#             tax_ids = []
#             for tax in line.invoice_line_tax_ids:
#                 tax_ids.append((4, tax.id, None))
#                 for child in tax.children_tax_ids:
#                     if child.type_tax_use != 'none':
#                         tax_ids.append((4, child.id, None))
#             analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
# 
#             move_line_dict = {
#                 'invl_id': line.id,
#                 'type': 'src',
#                 'name': line.name.split('\n')[0],
#                 'price_unit': line.price_unit,
#                 'quantity': line.quantity,
#                 'price': line.price_subtotal,
#                 'account_id': line.account_id.id,
#                 'product_id': line.product_id.id,
#                 'uom_id': line.uom_id.id,
#                 'account_analytic_id': line.account_analytic_id.id,
#                 'tax_ids': tax_ids,
#                 'move_id': self.id,
#                 'analytic_tag_ids': analytic_tag_ids
#             }
#             res.append(move_line_dict)
#         return res 
     
    

# DB    def action_move_create(self):
#         result = super(AccountMove, self).action_move_create()
#     
#         """ Creates invoice related analytics and financial move lines """
#         account_move = self.env['account.move']
# 
#         for inv in self:
#             if not inv.journal_id.sequence_id:
#                 raise UserError(_('Please define sequence on the journal related to this invoice.'))
#             if not inv.invoice_line_dates_ids:
#                 raise UserError(_('Please create some invoice lines.'))
#             if inv.move_id:
#                 continue
# 
#             ctx = dict(self._context, lang=inv.partner_id.lang)
# 
#             if not inv.invoice_date:
#                 inv.with_context(ctx).write({'invoice_date': fields.Date.context_today(self)})
#             if not inv.date_due:
#                 inv.with_context(ctx).write({'date_due': inv.invoice_date})
#             company_currency = inv.company_id.currency_id
# 
#             # create move lines (one per invoice line + eventual taxes and analytic lines)
#             iml = inv.invoice_line_move_line_get()
#             iml += inv.tax_line_move_line_get()
# 
#             diff_currency = inv.currency_id != company_currency
#             # create one move line for the total and possibly adjust the other lines amount
#             total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)
# 
#             name = inv.name or '/'
#             if inv.payment_term_id:
#                 totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.invoice_date)[0]
#                 res_amount_currency = total_currency
#                 ctx['date'] = inv._get_currency_rate_date()
#                 for i, t in enumerate(totlines):
#                     if inv.currency_id != company_currency:
#                         amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
#                     else:
#                         amount_currency = False
# 
#                     # last line: add the diff
#                     res_amount_currency -= amount_currency or 0
#                     if i + 1 == len(totlines):
#                         amount_currency += res_amount_currency
#                     if inv.building_id:
#                         build =inv.building_id.id
#                     else:
#                         build =False 
#                     iml.append({
#                         'type': 'dest',
#                         'name': name,
#                         'price': t[1],
#                         'account_id': inv.account_id.id,
#                         'date_maturity': t[0],
#                         'amount_currency': diff_currency and amount_currency,
#                         'currency_id': diff_currency and inv.currency_id.id,
#                         'move_id': inv.id,
# #                         'building_id':build,
#                     })
#             else:
#                 if inv.building_id:
#                     build =inv.building_id.id
#                 else:
#                     build =False  
#                 print(build,"build------")  
#                 iml.append({
#                     'type': 'dest',
#                     'building_id':build,
#                     'name': name,
#                     'price': total,
#                     'account_id': inv.account_id.id,
#                     'date_maturity': inv.date_due,
#                     'amount_currency': diff_currency and total_currency,
#                     'currency_id': diff_currency and inv.currency_id.id,
#                     'move_id': inv.id
#                 })
#             
#             part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
#             line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
#             line = inv.group_lines(iml, line)
# 
#             journal = inv.journal_id.with_context(ctx)
#             line = inv.finalize_invoice_move_lines(line)
#             line[0][2]['building_id']=build
#             line[1][2]['building_id']=build
#             print(line,"line---------------==----<<")
#             
#             date = inv.date or inv.invoice_date
#             move_vals = {
#                 'ref': inv.reference,
#                 'line_ids': line,
#                 'journal_id': journal.id,
#                 'date': date,
#                 'narration': inv.comment,
#             }
#             ctx['company_id'] = inv.company_id.id
#             ctx['invoice'] = inv
#             ctx_nolang = ctx.copy()
#             ctx_nolang.pop('lang', None)
#             move = account_move.with_context(ctx_nolang).create(move_vals)
#             # Pass invoice in context in method post: used if you want to get the same
#             # account move reference when creating the same invoice after a cancelled one:
#             move.post()
#             # make the invoice point to that move
#             vals = {
#                 'move_id': move.id,
#                 'date': date,
#                 'move_name': move.name,
#             }
#             inv.with_context(ctx).write(vals)
#         return result
    
    
    
#DB     def action_invoice_open(self):
#         user_id = self.env['res.users'].browse(self.env.uid)
# #         if not user_id.has_group('account.group_account_manager'):
# #             raise ValidationError(_('You have no permission to Validate!'))
#         res = super(account_invoice, self).action_invoice_open()
#         for items in self:
#             if items.number:
#                 items.new_sequence = items.number
#                 items.write({'new_sequence':items.number})
#         if self.building_id:
#             building_id = self.building_id.id
#         else:
#             building_id = False
#         if self.module_id:
#             module =self.module_id.id
#         else:
#             module =False
#         if self.unit_id:
#             unit_id =self.unit_id.id 
#         else:
#             unit_id =False
#         move={} 
#         line_list2 =[]
#         if self.type == 'in_invoice':
#             for all in self.invoice_line_dates_ids:
#                 if all.product_id:
#                     all.product_id.lst_price = all.price_unit
#                     location = self.env['stock.location'].search([('usage','=','supplier')])
#                     type = self.env['stock.picking.type'].search([('code','=','incoming')])
#                     location_des = self.env['stock.location'].search([('usage','=','internal')])
#                     if all.product_id.type == 'product':
#                         move={'product_id': all.product_id.id,
#                               'product_qom_qty':all.quantity,
#                               'location_id':location[0].id,
#                               'name':'stock received',
#                               'product_uom_qty':all.quantity,
#                               'quantity_done':all.quantity,
#                               'product_uom':all.product_id.uom_id.id,
#                               'location_dest_id':location_des[0].id}
#                         line_list2.append((0,0,move))
#             if  line_list2 != []:          
#                 x= self.env['stock.picking'].create({'partner_id':self.partner_id.id,
# #                                                  'building_id':building_id,
# #                                                  'module_id':module,
# #                                                  'unit_id':unit_id,
#                                                  'origin':self.number,
#                                                  'location_id':location[0].id,
#                                                  'location_dest_id':location_des[0].id,
#                                                  'picking_type_id':type[0].id,
#                                                  'move_lines':line_list2}
#                                                           )
#                 x.button_validate()
# #         self.change_sequence()
#         return res 
        
                
    
    @api.model
    def action_set_new_invoice(self):
        units = self.env['zbbm.unit'].search(['|',('state','=','book'),('state','=','contract')])
        invoices = self.search([('state','not in',['paid','cancel']),('type','=','out_invoice')])
        if invoices:
            for items in invoices:
                if items.unit_id:
                    if items.invoice_date_due:
                        if datetime.datetime.today() > end_date and end_date+timedelta(days=16) > datetime.datetime.today():
                            mail_pool = self.env['mail.mail']
                            email_template_obj = self.env['mail.template']
                            mailmess_pool = self.env['mail.message']
                            mail_date = datetime.datetime.now()
                            mail_pool = self.env['mail.mail']
                            email_template_obj = self.env['mail.template']
                            mailmess_pool = self.env['mail.message']
                            mail_date = datetime.datetime.now()
                            ir_model_data = items.env['ir.model.data']
                            try:
                                template_id = ir_model_data.get_object_reference('zb_building_management', 'email_template_session_mail33')[1]
                            except ValueError:
                                template_id = False
                            if template_id:
                                mail_template_obj = self.env['mail.template'].browse(template_id)
                                mail_id = mail_template_obj.send_mail(items.id, force_send=True)
                            else:
                                raise Warning(_('Please provide Assigned user/Email'))
                            
                        if datetime.datetime.today() > end_date+timedelta(days=16):
                            mail_pool = self.env['mail.mail']
                            email_template_obj = self.env['mail.template']
                            mailmess_pool = self.env['mail.message']
                            mail_date = datetime.datetime.now()
                            mail_pool = self.env['mail.mail']
                            email_template_obj = self.env['mail.template']
                            mailmess_pool = self.env['mail.message']
                            mail_date = datetime.datetime.now()
                            ir_model_data = items.env['ir.model.data']
                            try:
                                template_id = ir_model_data.get_object_reference('zb_building_management', 'email_template_session_mail331')[1]
                            except ValueError:
                                template_id = False
                            if template_id:
                                mail_template_obj = self.env['mail.template'].browse(template_id)
                                mail_id = mail_template_obj.send_mail(items.id, force_send=True)
                            else:
                                raise Warning(_('Please provide Assigned user/Email'))
                            
                            
        return True        
    
    
                    
                            
    @api.model
    def action_set_new_invoice_saleperson(self):
        units = self.env['zbbm.unit'].search(['|',('state','=','book'),('state','=','contract')])
        invoices = self.search([('state','not in',['paid','cancel']),('type','=','out_invoice')])
        if invoices:
            for items in invoices:
                if items.unit_id:
                    if items.invoice_date_due:
                        end_date = datetime.datetime.strptime(str(items.invoice_date_due), '%Y-%m-%d')
                        if datetime.datetime.today() > end_date and end_date+timedelta(days=16) > datetime.datetime.today():
                            mail_pool = self.env['mail.mail']
                            email_template_obj = self.env['mail.template']
                            mailmess_pool = self.env['mail.message']
                            mail_date = datetime.datetime.now()
                            mail_pool = self.env['mail.mail']
                            email_template_obj = self.env['mail.template']
                            mailmess_pool = self.env['mail.message']
                            mail_date = datetime.datetime.now()
                            ir_model_data = items.env['ir.model.data']
                            try:
                                template_id = ir_model_data.get_object_reference('zb_building_management', 'email_template_session_mail3312')[1]
                            except ValueError:
                                template_id = False
                            if template_id:
                                mail_template_obj = self.env['mail.template'].browse(template_id)
                                mail_id = mail_template_obj.send_mail(items.id, force_send=True)
                            else:
                                raise Warning(_('Please provide Assigned user/Email'))
                    

    def _get_followers1(self):
        users =self.env['res.users'].search([])
        li =''
        for all in users:
            if all.has_group('acccount.group_account_invoice'):
                if all.partner_id.email:
                    li += (all.partner_id.email) + ','
            if all.has_group('zb_building_management.group_tijaria_admin')  :
                if all.partner_id.email:
                    li+=  (all.partner_id.email) +","
        for items in self:
            items.cc_email = li
        
     
    def _get_followers2(self):
        users =self.env['res.users'].search([])
        li =''
        for all in users:
            if all.has_group('acccount.group_account_invoice'):
                if all.partner_id.email:
                    li += (all.partner_id.email) + ','
            if all.has_group('zb_building_management.group_tijaria_admin'):
                if all.partner_id.email:
                    li+=  (all.partner_id.email) +","
            if all.has_group('zb_building_management.group_user_management'):
                if all.partner_id.email:
                    li+=  (all.partner_id.email) +","    
        
        for items in self:
            items.cc_email2 = li                   
                
    
    
    
    def write(self, vals):
        '''Modified for Message Post'''
         
        msg = ''
        if self.ids:
#             if "invoice_line_dates_ids" in vals and "invoice_line_ids" in vals:
#                 vals.pop("invoice_line_ids")
            if vals.get('building_id'):
                if vals.get('unit_id'):
                    if vals['unit_id'] != self.unit_id:
                        buil = self.env.get('zbbm.building').browse(vals['building_id'])
                        mod = self.env.get('zbbm.unit').browse(vals['unit_id'])
                        msg = 'invoice for %s Building %s  Unit ' %(buil.name,mod.name)
                        self.message_post(body=msg)
                if vals.get('module_id'):
                    if vals['module_id'] != self.module_id:
                        uni = self.env['zbbm.module'].browse(vals['module_id'])
                        buil = self.env.get('zbbm.building').browse(vals['building_id'])
                        msg  = 'Invoice for %s Building, Module %s' %(buil.name,uni.name)
                        self.message_post(body=msg)
        res = super(AccountMove, self).write(vals)
        return res
     

    @api.depends('name')
    def name_get(self):
        result = []
        if self.env.context.get('active_model') == 'installment.details':
            for event in self:
                result.append((event.id, 'Invoiced'))
            return result
        else: 
            for event in self:
                result.append((event.id, '%s' % (event.name or 'Invoice')))
            return result
    
    
    @api.depends('invoice_date')
    def _get_month(self):
        for record in self:
            month_id = False
            if record.invoice_date:
                date = datetime.datetime.strptime(str(record.invoice_date),"%Y-%m-%d")
                month = datetime.datetime.date(date).strftime('%B')
                year = date.year
                value = "%s %s"%(year, month)
                month_id = self.env['zbbm.month'].search([['name', '=', value]])
                month_id = month_id and month_id[0]
                if not month_id:
                    month_id = self.env['zbbm.month'].create({'name': value})
            record.month_id = month_id
            
    
    def update_month_selection(self):
        
        def _get_month(self, from_date, to_date):
            to_date = datetime.date(day=1, month=to_date.month, year=to_date.year)
            from_date = datetime.date(day=1, month=from_date.month, year=from_date.year)
            r = relativedelta.relativedelta(to_date, from_date)
            return r.months
        dict_month_selection = {0 : 'current_month',
                           1 : 'one_month',
                           2 : 'two_month'}
        now = datetime.datetime.now()
        self.env.cr.execute("SELECT month_selection, id, invoice_date \
                            from account_move where \
                            month_selection in ('current_month', 'one_month', 'two_month')")
        list_res = self.env.cr.dictfetchall()
        for res in list_res:
            if res.get('invoice_date'):
                date_invoice = datetime.datetime.strptime(str(res.get('invoice_date')), DF)
                months = _get_month(self, date_invoice, now)
                month_selection = dict_month_selection.get(months, 'other')
                if not month_selection == res.get('month_selection'):
                    self.env.cr.execute("UPDATE account_move \
                            set month_selection = '%s' where id = %s" % (month_selection, res.get('id')))
        return True
    
        
    @api.depends('invoice_date', 'state')
    def _calculate_month(self):
        '''Function to calculate total from all the valid payments'''
        def _get_month(self, from_date, to_date):
            to_date = datetime.date(day=1, month=to_date.month, year=to_date.year)
            from_date = datetime.date(day=1, month=from_date.month, year=from_date.year)
            r = relativedelta.relativedelta(to_date, from_date)
            return r.months
        dict_month_selection = {0 : 'current_month',
                           1 : 'one_month',
                           2 : 'two_month'}
        now = datetime.datetime.now()
        self.env.cr.execute("SELECT month_selection, id, invoice_date \
                            from account_move where \
                            month_selection in ('current_month', 'one_month', 'two_month')")
        list_res = self.env.cr.dictfetchall()
        for res in list_res:
            if res.get('invoice_date'):
                date_invoice = datetime.datetime.strptime(str(res.get('invoice_date')), DF)
                months = _get_month(self, date_invoice, now)
                month_selection = dict_month_selection.get(months, 'other')
                if not month_selection == res.get('month_selection'):
                    self.env.cr.execute("UPDATE account_move \
                            set month_selection = '%s' where id = %s" % (month_selection, res.get('id')))
                else:
                    break
        month_selection = 'other'
        for items in self:
            if items.invoice_date:
                date_invoice = datetime.datetime.strptime(str(items.invoice_date), DF)
                months = _get_month(items, date_invoice, now)
                if dict_month_selection.get(months):
                    month_selection = dict_month_selection[months]
            items.month_selection = month_selection
        
    
    def onchange_flat(self,flat):
        res={'value':{}}
        if flat:
            flat = self.env.get('zbbm.module').browse(flat)
            res['value'].update({'building_id':flat.building_id and flat.building_id.id or False})
        else:
            res['value'].update({'building_id': False})
        return res
    
    
    def onchange_unit(self,flat):
        res={'value':{}}
        if flat:
            flat = self.env.get('zbbm.unit').browse(flat)
            res['value'].update({'building_id':flat.building_id and flat.building_id.id or False})
        else:
            res['value'].update({'building_id': False})
        return res
    
    
    @api.onchange('add_bank')
    def onchange_bank(self):
        lis = {}
        z= []
        if self.add_bank == 'yes':
            res={'value':{}}
            flat = self.env.get('res.partner.bank').search([('report_invoice','=',True),('partner_id','=',self.company_id.partner_id.id)])
            for line in flat:
                z.append(line.id)
            lis['domain'] = {'bank_id':[('id','in',z)]}
        else:
            lis['domain'] = {'bank_id':[]}   
        return lis
    

    @api.onchange('building_id')
    def hide_units_modules(self):
        for all in self:
            if all.building_id:
                if all.building_id.building_type =='rent':
                    all.hide_field =False
                    all.hide_field2 =True
                else:
                    all.hide_field2 =False
                    all.hide_field =True
            else:
                all.hide_field =False
                all.hide_field2 =False
            if all.building_id.bank_id:
                all.add_bank='yes'
                all.bank_id = all.building_id.bank_id.id
            else:
                all.add_bank='no'
                all.bank_id = False
                                
    
    

    payment_id =fields.Many2one('account.journal',string='Payment Method')
    cheque = fields.Char(string = 'Cheque No')
    bank =fields.Many2one('res.bank',string='Bank Name')
    is_legal =   fields.Boolean('Legal',default =False)
    hide_field = fields.Boolean('Hide1',default =False,compute = 'hide_units_modules')
    hide_field2 = fields.Boolean('Hide2',default =False,compute = 'hide_units_modules')
    cc_email = fields.Char('followers1',compute='_get_followers1')
    cc_email2 = fields.Char('followers2',compute='_get_followers2')
    merged = fields.Many2one('account.move',readonly =True)
    add_bank = fields.Selection([('yes','Yes'),('no','No')],default='no')
    unit_id = fields.Many2one('zbbm.unit', 'Unit')
    module_id = fields.Many2one('zbbm.module', 'Flat/Office')
    agreement_id = fields.Many2one('zbbm.module.lease.rent.agreement', 'Agreement')
    building_id = fields.Many2one('zbbm.building', 'Building', domain=[('state', '=', 'available')])
    month_id = fields.Many2one('zbbm.month', string='Month', compute='_get_month', store=True)
    month_selection = fields.Selection([('current_month', 'Current Month'),
             ('one_month', 'OneMonth'), ('two_month', 'Two Month'),
             ('other', 'Other')], string='Type', compute='_calculate_month', store=True)
    bank_id = fields.Many2one('res.partner.bank',string="Bank")
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',copy =False,readonly =False,
         states={'paid': [('readonly', True)]},
        default=lambda self: self.env.user)
    
    new_sequence = fields.Char('Sequence No:')
    lease_id = fields.Many2one('zbbm.module.lease.rent.agreement',string="Lease Id")
    lead_id = fields.Many2one('crm.lead',string="Lead Id")
    

    def assign_outstanding_credit(self, credit_aml_id):
        self.ensure_one()
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        if not credit_aml.currency_id and self.currency_id != self.company_id.currency_id:
            credit_aml.with_context(allow_amount_currency=True, check_move_validity=False).write({
                'amount_currency': self.company_id.currency_id.with_context(date=credit_aml.date).compute(credit_aml.balance, self.currency_id),
                'currency_id': self.currency_id.id})
        if credit_aml.payment_id:
            credit_aml.payment_id.write({'invoice_ids': [(4, self.id, None)],
                                         'building_id':self.building_id.id,
                                         'module_id':self.module_id.id,
                                         'unit_id':self.unit_id.id})
        return self.register_payment(credit_aml)


#DB     @api.onchange('invoice_line_ids','invoice_line_dates_ids')
#     def _onchange_invoice_line_ids(self):
#         res =  super(AccountMove, self)._onchange_invoice_line_ids()
        

    def get_taxes_values(self):
        tax_grouped = {}
        if self.building_id and self.type=='out_invoice':
            for line in self.invoice_line_ids:
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
                for tax in taxes:
                    val = self._prepare_tax_line_vals(line, tax)
                    key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
    
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
            return tax_grouped
        else:
            res = super(AccountMove,self).get_taxes_values()
            return res

   
    
    
    
class Bank(models.Model): 
    
    _inherit = 'res.partner.bank'
    
    iban_no = fields.Char('IBAN Number')  
    report_invoice = fields.Boolean(string='Add in invoice',default =False)
      

    
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    
    building_id = fields.Many2one('zbbm.building', 'Building')
    from_date = fields.Date('From date')
    to_date = fields.Date('To date')
    account_analytic_id = fields.Many2one('account.analytic.account',
        string='Cost Centre')
    
    
    @api.onchange('name')
    def get_analytic(self):
        for items in self:
            if items.move_id.unit_id:
                items.account_analytic_id = items.move_id.unit_id.account_analytic_id
            if items.move_id.module_id:
                items.account_analytic_id = items.move_id.module_id.account_analytic_id
    
    
    

    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    def _check_reconcile_validity(self):
        if not self:
            return
        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled.'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries.'))
        if len(set(all_accounts)) > 1:
            raise UserError(_('Entries are not from the same account.'))
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('Account %s (%s) does not allow reconciliation. First change the configuration of this account to allow it.') % (all_accounts[0].name, all_accounts[0].code))
        return super(AccountMoveLine, self)._check_reconcile_validity()
