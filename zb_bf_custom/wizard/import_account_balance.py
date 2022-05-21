from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
import os
import xlrd
import xlwt
import xlsxwriter
import csv
import base64
import logging
_logger = logging.getLogger(__name__)

class DirectAccountBalanceWizard(models.TransientModel):
    _name = 'import.account.opening.balance'
    _inherit = 'data_import.wizard'
    _description = 'Wizard for Import Account Opening Balance'

    account_id = fields.Many2one('account.account',string="Opening Balance Account",required=True)
    journal_id = fields.Many2one('account.journal',string="Journal",required=True)
    date = fields.Date("Date",required=True)
    csv_file_name = fields.Char('CSV File Name')
    csv_file = fields.Binary('CSV File', required=True)
    
    def import_opening_balance(self):
        missed_row = []
        for rec in self:
            list_raw_data = self.get_data_from_attchment(rec.csv_file, 
                                                       rec.csv_file_name)
            
            date_wiz = rec.date
            date_move= date_wiz.strftime("%Y-%m-%d") 
            account_id = rec.account_id
            journal = rec.journal_id.id
            
            for raw in list_raw_data:
                print('==============raw================',raw)
                date = '2021-06-30'
                aa = raw['Analytical Account']
                
                account_obj = self.env['account.account'].search([('code','=',raw['Account Code'])])
                debit_line_dict = {}
                credit_line_dict = {}
                line_list = []
                if account_obj:
                    aa_obj = self.env['account.analytic.account'].search([('name','=',aa)])
                    if aa_obj:
                        aa_id= aa_obj.id
                    else:
                        aa_id = self.env['account.analytic.account'].create({'name':aa})
                        
                    print(aa_id,'=====================')
                    
                    if raw['Debit']:
                        
                        debit_line_dict = {
                            'account_id':account_obj.id,
                            'name':'Opening Balance as on 2021-06-30',
                            'date_maturity':date if date else '',
                            'debit':raw['Debit'] if raw['Debit'] != ' -   ' else 0.00,
                            'credit':0.00,
                            'analytic_account_id':aa_id
                            }
                        
                        credit_line_dict = {
                            'account_id':account_id.id,
                            'name':'Opening Balance as on 2021-06-30',
                            'debit':0.00,
                            'credit':raw['Debit'] if raw['Debit'] != ' -   ' else 0.00,
                            
                            }
                        if debit_line_dict['debit'] or debit_line_dict['credit']:
                            line_list.append((0, 0,debit_line_dict))
                        if credit_line_dict['debit'] or credit_line_dict['credit']:
                            line_list.append((0, 0,credit_line_dict))
                        
                    if raw['Credit']:
                        
                        credit_line_dict = {
                                    'account_id':account_obj.id,
                                    'name':'Opening Balance as on 2021-06-30',
                                    'date_maturity':date if date else '',
                                    'debit':0.00,
                                    'credit':raw['Credit'] if raw['Credit'] != ' -   ' else 0.00,
                                    'analytic_account_id':aa_id
                                    }
                        
                        debit_line_dict = {
                                    'account_id':account_id.id,
                                    'name': 'Opening Balance as on 2021-06-30',
                                    'debit':raw['Credit'] if raw['Credit'] != ' -   ' else 0.00,
                                    'credit':0.00
                                    }
                        if debit_line_dict['debit'] or debit_line_dict['credit']:
                            line_list.append((0, 0,debit_line_dict))
                        if credit_line_dict['debit'] or credit_line_dict['credit']:
                            line_list.append((0, 0,credit_line_dict))
                    move_data = {
                                    'ref':'Balance As on'+' '+str(date),
                                    'journal_id':journal,
                                    'date':date_move
                                    }
                               
                    move = self.env['account.move'].create(move_data) 
                    print(line_list)
                    move.line_ids = line_list
                  
                else:  
                    missed_row.append(raw['Account Code'])
                    
            _logger.info('Misssed Rows while importing=====================>',missed_row)
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                            