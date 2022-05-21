# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo import _, tools
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError 
 
    
class CustomerStatement(models.Model):
    _name = "customer.statement"
    _description = 'Customer Statement'
    
    sl_no = fields.Char('Sl.No')
    name=fields.Char('Ref')
    date = fields.Date('Date')
    debit = fields.Float('Debit',digits='Product Price')
    credit = fields.Float('Credit',digits='Product Price')
    balance = fields.Float('Balance',digits='Product Price')
    
    