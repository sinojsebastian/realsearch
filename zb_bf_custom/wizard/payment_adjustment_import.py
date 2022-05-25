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
        full_reconcile = raw.get('Full Reconcile')
        allocated_amt = raw.get('Line level allocation amount')
        payment_type = raw.get('Payment Type', False)
        payment_line_inv = raw.get('Payment Lines')
        if payment_line_inv and partner_id:
            move_line_ids = self.env['account.move.line'].search([('move_id.type','in',('in_invoice','in_receipt','out_invoice','out_receipt','entry')),('partner_id','=',partner_id.id),('move_id.state','not in',['draft','cancel'])])
        
        if move_line_ids:
            for each in move_line_ids:
                payment_line_inv_id = self.env['account.move'].search([('name','=',payment_line_inv)])
                print('=============payment_line_inv_id=================',payment_line_inv_id)
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
            line_list = []
            ctx = dict(self.env.context or {}) 
            amount = 0
            payment_partner_id = False
            for raw in list_raw_data:
                print('raw++++++++++++++===============', raw)
                partner_name = raw.get('Partner', False)
                print('==========partner_name==========',partner_name)
                partner_id = self.env['res.partner'].search([('name','=',partner_name)])
                print('==========partner_id==========',partner_id)
                payment_type = raw.get('Payment Type', False)
                method_of_payment = raw.get('Method of Payment', False)
                partner_type = raw.get('Partner Type', False)
                payment_journal = raw.get('Payment Journal', False)
                payment_journal_id = self.env['account.journal'].search([('name','=',payment_journal)])
                payment_mode = raw.get('Payment Mode', False)
                description = raw.get('Description', False)
                acc_payee = raw.get('Account payee', False)
                cheque_no = raw.get('Cheque no', False)
                cheque_date = raw.get('Cheque Date', False)
                lang_code = self.env.user.lang
                lang = self.env['res.lang']
                lang_id = lang._lang_get(lang_code)
                date_format = lang_id.date_format
                cheque_date_format = False
                if cheque_date:
                    cheque_date_format = datetime.strptime(str(cheque_date),'%Y-%m-%d')
                cheque_bank = raw.get('Cheque Bank', False)
                cheque_bank_id = self.env['res.bank'].search([('name','=',cheque_bank)])
                name_on_cheque = raw.get('Name On Cheque', False)
                payment_method_code = raw.get('Payment Method Code')
                payment_method_code_value = self.env['account.payment.method'].search([('payment_type','=','outbound'),('code','=',payment_method_code)])
                date = raw.get('Date', False)
                payment_date_format = False
                if date:
                    payment_date_format = datetime.strptime(str(date),'%Y-%m-%d')
                memo = raw.get('Memo', False)
                if partner_id:
                    amount = raw.get('Amount', False)
                    payment_partner_id = partner_id
                    if raw.get('Payment Lines'):
                        print('Payment Lines++++++++++++++===============', raw.get('Payment Lines'))
                        payment_lines_vals = self._load_payment_lines(raw,payment_partner_id)
                        if payment_lines_vals:
                            line_list.append((0, 0, payment_lines_vals))
                    payment_vals = {
                        'payment_type':payment_type,
                        'method_type':method_of_payment,
                        'partner_type':partner_type,
                        'partner_id':partner_id.id,
                        'journal_id':payment_journal_id.id,
                        'payment_mode':payment_mode,
                        'notes':description,
                        'ac_payee':acc_payee,
                        'cheque_no':cheque_no,
                        'cheque_date':cheque_date_format,
                        'cheque_bank_id':cheque_bank_id.id,
                        'name_on_cheque':name_on_cheque,
                        'payment_method_id':payment_method_code_value.id,
                        'amount':0.000,
                        'payment_date':payment_date_format,
                        'communication':memo,
                        }
                    payment_id = self.env['account.payment'].create(payment_vals)
                    print('=====================payment',payment_id)
                else:
                    if raw.get('Payment Lines'):
                        print('Payment Lines++++++++++++++===============', raw.get('Payment Lines'))
                        payment_lines_vals = self._load_payment_lines(raw,payment_partner_id)
                        if payment_lines_vals:
                            line_list.append((0, 0, payment_lines_vals))
            if line_list:
                debit_allocation_total = 0.000
                credit_total = 0.000
                for each in line_list:
                    if each[2] and each[2]['allocation']:
                        if each[2]['credit'] > 0:
                            credit_total += each[2]['allocation']
                        elif each[2]['debit'] > 0:
                            debit_allocation_total += each[2]['allocation']
                total_amount = credit_total - debit_allocation_total
                print('=============total_amount==============',total_amount)
                payment_id.write({'amount':total_amount,
                                  'payment_line_ids':line_list})
