from odoo import api, fields, models,_
from odoo.tools.translate import _
from odoo.exceptions import AccessError,UserError,Warning
from lxml import etree
import re
from datetime import date,datetime,timedelta 
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ImportPaymentAdjustmentLines(models.TransientModel):
    _name = 'payment.adjustment.lines.import'
    _inherit = 'data_import.wizard'
    _description = "Import Payment Adjustment Lines"
    
    csv_file =  fields.Binary('CSV File', required=True)
    csv_file_name = fields.Char('CSV File Name', size=64)
    
    def _load_payment_lines(self,raw,partner_id):
        payment_line_obj=self.env['account.payment.line']
        line_vals = []
        due_date = ''
        move_line_ids = ''
        inv_obj = ''
        full_reconcile = raw.get('Full Reconcile',False)
        allocated_amt = raw.get('Line level allocation amount')
        payment_type = raw.get('Payment Type', False)
        payment_line_inv = raw.get('Payment Lines')
        payment_line_inv_id = self.env['account.move'].search([('name','=',payment_line_inv)])
        print('=============payment_line_inv_id=================',payment_line_inv_id)
        if payment_line_inv_id and partner_id:
            move_line_ids = self.env['account.move.line'].search([('move_id','=',payment_line_inv_id.id),('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',partner_id.id),('move_id.state','not in',['draft','cancel'])])
        print('=============move_line_ids=================',move_line_ids)
        if move_line_ids:
            for each in move_line_ids:
                # payment_line_inv_id = self.env['account.move'].search([('name','=',payment_line_inv)])
                # print('=============payment_line_inv_id=================',payment_line_inv_id)
                if each.account_id.user_type_id.type in ('receivable', 'payable') and not each.payment_id and each.move_id.id == payment_line_inv_id.id:
                    line_reconcile_id = each
                    allocated_amount=0.0
                    if each.move_id.type == 'entry':
                        acc_date = each.move_id.date
                        partial_id = self.env['account.partial.reconcile'].search(['|',('credit_move_id.move_id','=',each.move_id.id),('debit_move_id.move_id','=',each.move_id.id)])
                        if len(partial_id) > 0:   
                            partial_amount = 0                                             
                            for entry in partial_id:
                                partial_amount += entry.amount
                            balance_amount = each.move_id.amount_total - partial_amount
                        
                        else:
                            balance_amount = each.move_id.amount_total - partial_id.amount
                    else:
                        acc_date = each.move_id.invoice_date
                        balance_amount = each.move_id.amount_residual
                        # acc_date=self.env['account.move'].search([('type','=','entry'),('name','=',each.name)])
                    pay_line_id=payment_line_obj.search([('inv_id','=',each.move_id.id)])
                    if pay_line_id:
                        allocated_amount=sum(line.allocation for line in pay_line_id)
                    
                    # for date_due in acc_date:
                    #     due_date=date_due.date
                    if balance_amount:
                        open_invoice_lines={
                        'inv_id':each.move_id.id,
                        'move_line_id':line_reconcile_id.id if line_reconcile_id else False,
                        'ref_num':each.move_id.ref,
                        'acc_id':each.partner_id.property_account_receivable_id.id if payment_type and payment_type == 'inbound' else each.partner_id.property_account_payable_id.id ,
                        'original_amount':each.move_id.amount_total,
                        'due_date':each.move_id.invoice_date_due, #it will change the date format in d/m/y
                        'original_date':acc_date,
                        'currency_id':each.currency_id.id,
                        'balance_amount':balance_amount if balance_amount else 0.00,
                        'full_reconcile':full_reconcile,
                        'allocation':allocated_amt,
                        'debit': each.debit,
                        'credit':each.credit,
                        }
                        return open_invoice_lines 
    
    def import_payment_adjustment_lines(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
            ctx = dict(self.env.context or {}) 
            amount = 0
            payment_partner_id = False
            payment_method_id = False
            payment_id = False
            payment_dict = {}
            raw_count = 0
            payment_type_dict = {'outbound':'Send Money','inbound':'Receive Money','transfer':'Internal Transfer'}
            method_type_dict = {'advance':'Advance Payment','adjustment':'Payment Adjustment'}
            partner_type_dict = {'customer':'Customer','supplier':'Vendor'}
            payment_mode_dict = {'cash':'Cash','cheque':'Cheque','transfer':'Transfer','credit card':'Credit Card'}
            for raw in list_raw_data:
                line_list = []
                partner_name = raw.get('Partner', False)
                partner_id = self.env['res.partner'].search([('name','=',partner_name)])
                if partner_id:
                    raw_count += 1
                    raw_payment_type = raw.get('Payment Type', False)
                    payment_type = list(payment_type_dict.keys())[list(payment_type_dict.values()).index(raw_payment_type)]
                    raw_method_of_payment = raw.get('Method of Payment', False)
                    method_of_payment = list(method_type_dict.keys())[list(method_type_dict.values()).index(raw_method_of_payment)]
                    raw_partner_type = raw.get('Partner Type', False)
                    partner_type = list(partner_type_dict.keys())[list(partner_type_dict.values()).index(raw_partner_type)]
                    payment_journal = raw.get('Payment Journal', False)
                    payment_journal_id = self.env['account.journal'].search([('name','=',payment_journal)])
                    raw_payment_mode = raw.get('Payment Mode', False)
                    payment_mode = list(payment_mode_dict.keys())[list(payment_mode_dict.values()).index(raw_payment_mode)]
                    check_book_id = False
                    if payment_mode == 'cheque':
                        check_book_id = self.env['check.book'].search([('state','=','active'),('bank_account_id','=',payment_journal_id.id)],order='id ASC',limit=1)
                    description = raw.get('Description', False)
                    acc_payee = raw.get('Account payee')
                    cheque_no = raw.get('Cheque no', False)
                    cheque_date = raw.get('Cheque Date', False)
                    lang_code = self.env.user.lang
                    lang = self.env['res.lang']
                    lang_id = lang._lang_get(lang_code)
                    date_format = lang_id.date_format
                    cheque_date_format = False
                    if cheque_date:
                        cd = datetime.strptime(cheque_date, '%d/%m/%Y')
                        cheque_date_format = cd.strftime('%Y-%m-%d')
                        # cheque_date.strftime('%d/%b/%Y').strptime(str(cheque_date),'%Y-%m-%d')
                    cheque_bank = raw.get('Cheque Bank', False)
                    cheque_bank_id = self.env['res.bank'].search([('name','=',cheque_bank)])
                    name_on_cheque = raw.get('Name On Cheque', False)
                    payment_method_code = raw.get('Payment Method Code')
                    payment_method_code_value = self.env['account.payment.method'].search([('payment_type','=','outbound'),('name','=',payment_method_code)])
                    date = raw.get('Date', False)
                    payment_date_format = False
                    if date:
                        d = datetime.strptime(date, '%d/%m/%Y')
                        payment_date_format = d.strftime('%Y-%m-%d')
                        # payment_date_format = cheque_date.strftime('%d/%b/%Y').strptime(str(date),'%Y-%m-%d')
                    memo = raw.get('Memo', False)
                    payment_vals = {
                            'payment_type':payment_type,
                            'method_type':method_of_payment,
                            'partner_type':partner_type,
                            'partner_id':partner_id.id,
                            'journal_id':payment_journal_id.id,
                            'payment_mode':payment_mode,
                            'notes':description,
                            'ac_payee':acc_payee,
                            'check_book_id':check_book_id.id if check_book_id else False,
                            'cheque_no':cheque_no,
                            'cheque_date':cheque_date_format,
                            'cheque_bank_id':cheque_bank_id.id,
                            'name_on_cheque':name_on_cheque,
                            'payment_method_id':payment_method_code_value.id,
                            'amount':raw.get('Amount', False) if method_of_payment == 'advance' else 0.000,
                            'payment_line_ids':[],
                            'payment_date':payment_date_format,
                            'communication':memo,
                            }
                
                    if raw.get('Payment Lines'):
                        payment_lines_vals = self._load_payment_lines(raw,payment_partner_id)
                        if payment_lines_vals:
                            line_list.append((0, 0, payment_lines_vals))
                # if partner_id:
                #     raw_count += 1
                    amount = raw.get('Amount', False)
                    payment_partner_id = partner_id
                    payment_method_id = method_of_payment
                    if raw.get('Payment Lines'):
                        payment_lines_vals = self._load_payment_lines(raw,payment_partner_id)
                        if payment_lines_vals:
                            # line_list.append((0, 0, payment_lines_vals))
                            payment_vals['payment_line_ids'] = [(0, 0, payment_lines_vals)]
                        payment_dict.update({raw_count:payment_vals})
                    else:
                        payment_dict.update({raw_count:payment_vals})
                    
                    
                else:
                    if raw.get('Payment Lines'):
                        payment_lines_vals = self._load_payment_lines(raw,payment_partner_id)
                        if payment_lines_vals:
                            payment_dict[raw_count]['payment_line_ids'].append((0, 0, payment_lines_vals))

            for key,vals in payment_dict.items():
                if vals['method_type'] == 'adjustment':
                    if vals['payment_line_ids']:
                        debit_allocation_total = 0.000
                        credit_total = 0.000
                        for each in vals['payment_line_ids']:
                            if each[2] and each[2]['allocation']:
                                if each[2]['credit'] > 0:
                                    credit_total += each[2]['allocation']
                                elif each[2]['debit'] > 0:
                                    debit_allocation_total += each[2]['allocation']
                        total_amount = credit_total - debit_allocation_total
                        vals['amount'] = total_amount
                                          
                payment_id = self.env['account.payment'].create(vals)
                
                
