# -*- coding: utf-8 -*-
import os
import xlrd
import datetime
import base64
import csv
from io import StringIO,BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
from odoo import tools as openerp_tools

class wizard_company_data(models.TransientModel):
    _name = 'wizard.customer.data'
    _inherit = 'data_import.wizard'

    
    csv_file_name = fields.Char('CSV File Name', size=64)
    csv_file = fields.Binary('CSV File', required=True)
    
    def upload_customer_data(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
            customer_pool = self.env['res.partner']
            for raw in list_raw_data:
                old_data = new_data = {}
                
                customer_id = self.find_customer(raw.get('Name'))
                if raw.get('Name'): 
                    old_data['name'] = raw.get('Name')
                    old_data['mobile'] = raw.get('mobile')
                    old_data['email'] = raw.get('E-email')
                    old_data['supplier'] = False
                    old_data['customer'] = True
                    old_data['phone'] = raw.get('Tel #')
                    
                    if raw.get('Address'):
                        add = raw.get('Address').split(',') 
                        old_data['street'] = add[0]
                        old_data['street2'] = add[1:]
                    
                    
                    if not customer_id:
                            customer_id = self.env['res.partner'].create(old_data)
                    else:
                        customer_id.write(old_data)
                        
    
    
        return True
    

    def find_customer(self,customer):
        supplier_ids = False
        supplier_pool = self.env['res.partner']
        supplier_ids =  supplier_pool.search([('customer','=',True),('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids     
    
         