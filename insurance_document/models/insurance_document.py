# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)
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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp import api, fields, models, _
from openerp.tools.translate import _
import smtplib
from smtplib import SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class InsuranceDocument(models.Model):
    _name = 'insurance.document'
    _description = 'Insurance Document'
#     _rec_name = 'insurer_partner_id'

    
    name = fields.Char(string="Document")
    insurer_partner_id = fields.Many2one('res.partner',string="Vendor/Supplier")
    building_id = fields.Many2one('zbbm.building',string="Building")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    insured_value = fields.Float(string="Value", digits='Product Price')
    state = fields.Selection([('new', 'New'), ('active', 'Active'), ('expired', 'Expired'),('cancel', 'Cancel'), ('renewed', 'Renewed')],
            'Status', readonly=True,default='new')
    document_number = fields.Char('Document Number')
    insurance_document_type = fields.Many2one('insurance.document.type',string="Document Type")
    

    def action_state_active(self):
        return self.write({'state': 'active'})


    def action_state_expired(self):
        return self.write({'state': 'expired'})


    def action_state_cancel(self):
        return self.write({'state': 'cancel'})


    def action_state_renewed(self):
        return self.write({'state': 'renewed'})


    def action_state_reactivate(self):
        return self.write({'state': 'active'})
    
    
    
    
class InsuranceDocumentType(models.Model):
    _name = 'insurance.document.type'
    
    name = fields.Char('Name')
    partner_ids = fields.Many2many('res.partner', string='Recipients')


   