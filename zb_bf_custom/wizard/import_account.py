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

class DirectAccountWizard(models.TransientModel):
    _name = 'import.opening.balance'
    _inherit = 'data_import.wizard'
    _description = 'Wizard for Import Data'

    account_id = fields.Many2one('account.account',string="Opening Balance Account",required=True)
    journal_id = fields.Many2one('account.journal',string="Journal",required=True)
    date = fields.Date("Date",required=True)
    csv_file_name = fields.Char('CSV File Name')
    csv_file = fields.Binary('CSV File', required=True)
    
    def import_opening_balance(self):
        for rec in self:
            list_raw_data = self.get_data_from_attchment(rec.csv_file, 
                                                       rec.csv_file_name)
            
            date_wiz = rec.date
            date_move= date_wiz.strftime("%Y-%m-%d") 
            account_id = rec.account_id
            journal = rec.journal_id.id
            partner_list=[]
            building_list = []
            f = open("MissingPartner.csv", "w")
            header_data = "Account Name"+','+"Account Code"+','+"Partner"+','+"Ref. No."+','+"Building Code"+','+"Building"+','+"Flat No"+','+"Due Date"+','+"Debit Amount"+','+"Credit Amount"+'\n'
            f.write(header_data)
            p = open("MissingBuilding.csv", "w")
            header_data = "Account Name"+','+"Account Code"+','+"Partner"+','+"Ref. No."+','+"Building Code"+','+"Building"+','+"Flat No"+','+"Due Date"+','+"Debit Amount"+','+"Credit Amount"+'\n'
            p.write(header_data)
            missed_row = []
            for raw in list_raw_data:
                print('==============raw================',raw)
                date_line = raw['Due Date']
                if date_line:
                    d = datetime.strptime(date_line, '%d/%b/%Y')
                    date = d.strftime('%Y-%m-%d')
                account_obj = self.env['account.account'].search([('code','=',raw['Account Code'])])
                debit_line_dict = {}
                credit_line_dict = {}
                line_list = []
                partner= self.env['res.partner'].search([('name','=',str(raw['Partner']))])
                building = self.env['zbbm.building'].search([('code','=',raw['Building Code'])])
                module = self.env['zbbm.module'].search([('name','=',str(raw['Flat No'])),('building_id','=',building.id)])
                if building:
                    building_id = building.id
                else:
                    building_id = False
                if module:
                    module_id = module.id
                else:
                    module_id = False
                
                if partner:
                    if raw['Debit Amount']:
                        debit_line_dict = {
                            'partner_id':partner[0].id,
                            'account_id':account_obj.id,
                            'building_id':building_id,
                            'module_id':module_id,
                            'name':str(raw['Ref. No.']),
                            'date_maturity':date if date else '',
                            'debit':raw['Debit Amount'] if raw['Debit Amount'] != ' -   ' else 0.00,
                            'credit':0.00,
                           
                            }
                        # line_list.append((0,0,debit_line_dict))
                        credit_line_dict = {
                            'partner_id':partner[0].id,
                            'account_id':account_id.id,
                            'building_id':building_id,
                            'module_id':module_id,
                            'name':str(raw['Ref. No.']),
                            'debit':0.00,
                            'credit':raw['Debit Amount'] if raw['Debit Amount'] != ' -   ' else 0.00,
                            
                            }
                        if debit_line_dict['debit'] or debit_line_dict['credit']:
                            line_list.append((0, 0,debit_line_dict))
                        if credit_line_dict['debit'] or credit_line_dict['credit']:
                            line_list.append((0, 0,credit_line_dict))
                        # line_list.append((0,0,credit_line_dict))
                    if raw['Credit Amount']:
                        credit_line_dict = {
                                    'partner_id':partner[0].id,
                                    'account_id':account_obj.id,
                                    'name':str(raw['Ref. No.']),
                                    'date_maturity':date if date else '',
                                    'building_id':building_id,
                                    'module_id':module_id,
                                    'debit':0.00,
                                    'credit':raw['Credit Amount'] if raw['Credit Amount'] != ' -   ' else 0.00
                                    
                                    }
                        # line_list.append((0,0,credit_line_dict))
                        debit_line_dict = {
                                    'partner_id':partner[0].id,
                                    'account_id':account_id.id,
                                    'building_id':building_id,
                                    'module_id':module_id,
                                    'name':str(raw['Ref. No.']),
                                    'debit':raw['Credit Amount'] if raw['Credit Amount'] != ' -   ' else 0.00,
                                    'credit':0.00
                                   
                                    
                                    }
                        if debit_line_dict['debit'] or debit_line_dict['credit']:
                            line_list.append((0, 0,debit_line_dict))
                        if credit_line_dict['debit'] or credit_line_dict['credit']:
                            line_list.append((0, 0,credit_line_dict))
                        # line_list.append((0,0,debit_line_dict))
                    move_data = {
                                    
                                    'ref':'Balance As on'+' '+str(rec.date),
                                    'journal_id':journal,
                                    'building_id':building_id,
                                    'module_id':module_id,
                                    # 'line_ids':line_list,
                                    'date':date_move
                                    }
                               
                    move = self.env['account.move'].create(move_data) 
                    move.line_ids = line_list
                else:
                    missed_row.append(str(raw['Ref. No.']))
                    _logger.warning('%s-%s-Debit amount-%s,Credit amount-%s'%(partner,str(raw['Ref. No.']),raw['Debit Amount'],raw['Credit Amount']))
                    partner_list.append(raw)  
                    values = list(raw.values())
                    lines_data = ''
                    for data in range (0,len(values)):
                        lines_data += values[data] if type(values[data]) == 'str' else str(values[data]) + ','
                        # if data < len(values)-1:
                        #     lines_data += lines_data + ','
                        #     print('===============lines_data*******=====================',lines_data)
                    lines_data = lines_data +'\n'
                    f.write(lines_data)
                
                if not building:
                    building_list.append(raw)  
                    build_values = list(raw.values())
                    build_lines_data = ''
                    for data in range (0,len(build_values)):
                        build_lines_data += build_values[data] if type(build_values[data]) == 'str' else str(build_values[data]) + ','
                        # if data < len(build_values)-1:
                        #     build_lines_data = build_lines_data + ','
                        #     print('===============build_lines_data*******=====================',build_lines_data)
                    build_lines_data = build_lines_data +'\n'
                    p.write(build_lines_data)
            
            p.close()
            f.close()  
            _logger.info('Misssed Rows while importing=====================>',missed_row)
                # worksheet.write(row,0,count,table_value_format)
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                            