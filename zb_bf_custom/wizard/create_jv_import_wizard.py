# -*- coding: utf-8 -*-v
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, Warning
from odoo import tools as openerp_tools
import os
import xlrd
import xlwt
import xlsxwriter
import csv
import base64
from io import StringIO
import glob
import tempfile
from datetime import datetime,date



import logging
_logger = logging.getLogger(__name__)


class CreateJvImportWizard(models.TransientModel):
    _name = 'create.jv.import.wizard'
    _inherit = 'data_import.wizard'
    _description = 'Wizard for JV Creation'
    
    
    csv_file_name = fields.Char('Xls File Name', size=64)
    csv_file = fields.Binary('Xls File')
    building_id = fields.Many2one('zbbm.building',string="Building")
    

    def upload_data(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
            
            account_id = self.env['account.account'].search([('internal_group','=', 'equity')],limit=1)
            
            for raw in list_raw_data:
                date = raw.get('Date')
                ref_no = raw.get('Ref. No.')
                building = raw.get('Building')
                flat_no = raw.get('Flat No')
                owner_name = raw.get('Owner Name')
                pending_amount = raw.get('Pending Amount')
                

                building_id = self.building_id
                owner_obj = self.env['res.partner']
                owner_id = self.env['res.partner'].search([('name','=',owner_name)])
                
                module_obj = self.env['zbbm.module']
                module_id = self.env['zbbm.module'].search([('name','=',flat_no),('building_id','=',building_id.id)])
                
                
                if date:
                    date = datetime.strptime(date, '%d-%m-%Y').date()
                else:
                    date = ''
                
                
                user_obj = self.env['res.users']
                
                if owner_name:
                    owner = self.env['res.users'].search([('name','=',owner_name)])
                    if not owner:
                        owner_data_obj ={
                            'name':owner_name,
                            'owner':True
                            }
                        owner_id = owner_obj.create(owner_data_obj)
                else:
                    owner_id = ''
                        
                
                
                if flat_no != None:
                    if not module_id:
                        module_data = {
                            'name':flat_no,
                            'building_id':building_id.id,
                            }    
                        
                        module_id = module_obj.create(module_data)
                        module_id.make_available()
                
                
                if owner_id:
#                     _logger.info("Acountttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt %s",account_id)
                
                    owner_payable_val =  {
                        'name':ref_no,
                        'account_id': account_id.id,
#                         'analytic_account_id':analytic,
                        'partner_id': owner_id.id,
                        'debit':0,
                        'credit':pending_amount,
                         }
                     
                    owner_expense_val = {
                                'name':ref_no,
                                'account_id': owner_id.property_account_receivable_id.id,
#                                 'analytic_account_id':analytic,
                                'partner_id': owner_id.id,
                                'debit':pending_amount,
                                'credit':0,
                                 }
                    vals = {
                            'partner_id': owner_id.id,
                            'type': 'entry',
                            'date' : date,
                            'ref':ref_no ,
                            'module_id': module_id.id,
                            'building_id':building_id.id,
                            'line_ids':[(0, 0,owner_payable_val),
                                        (0, 0,owner_expense_val)
                                        ],
                            }
                            
                    
                    
                    move_id = self.env['account.move'].create(vals)

#                     move_id.action_post()
                        
                   
                    
            
                    
