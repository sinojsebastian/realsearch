# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
import time
from odoo.tools.safe_eval import safe_eval

class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountMove, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        default_type = self._context.get('default_type', False)
        
        if default_type and default_type in ['out_invoice','out_refund','out_receipt','in_receipt']:
            vendor_bill = self.env.ref('zb_account_reports.report_vendor_bill')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == vendor_bill.id:
                    res['toolbar']['print'].remove(print_submenu)
        
        if default_type and default_type in ['in_invoice','in_refund','out_receipt','in_receipt']:
            customer_invoice = self.env.ref('zb_account_reports.report_customer_invoice')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == customer_invoice.id:
                    res['toolbar']['print'].remove(print_submenu)   
                      
        if default_type and default_type in ['out_invoice','out_refund','in_invoice','in_refund']:
            voucher = self.env.ref('zb_account_reports.action_voucher_report')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == voucher.id:
                    res['toolbar']['print'].remove(print_submenu)                           
                    
        return res
         

