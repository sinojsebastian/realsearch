from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning
from odoo import tools as openerp_tools
import os
import xlrd
from datetime import datetime,date,timedelta
import base64
import csv
from io import StringIO,BytesIO

class wizard_company_data(models.TransientModel):
    _name = 'wizard.customer.data'
    _inherit = 'data_import.wizard'

    
    csv_file_name = fields.Char('CSV File Name', size=64)
    csv_file = fields.Binary('CSV File', required=True)
    

    def upload_analytic_account(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
#             customer_pool = self.env['zbbm.module']
            for raw in list_raw_data:
                old_data = new_data = {}
                if raw.get('Particulars'): 
                    old_data['name'] = raw.get('Particulars')
                    old_data['company_id'] = 1
                    self.env['account.analytic.account'].create(old_data)
                

    def upload_customer_account(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
#             customer_pool = self.env['zbbm.module']
            for raw in list_raw_data:
                old_data = new_data = {}
                customer_id = self.find_customer(raw.get('Name'))
                if not customer_id:
                    old_data['name'] = raw.get('Name')
                    self.env['res.partner'].create(old_data)
                    
                    
    def find_asset_category(self,code):
        category_ids = False
        category_pool = self.env.get('account.asset.category')
        category_ids = category_pool.search([('name', '=', code)])
        if category_ids:
            category_ids = category_ids[0].id
        return category_ids
    
    
    
    def asset_update(self):
        if self.csv_file:
            asset_pool = self.env.get('account.asset.asset')
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            count = 0
            for raw in list_raw_data:
                asset_id = False
                asset_ids = asset_pool.search([('name','=',raw.get('Name'))])
                asset_data = {}
                asset_data['name'] = raw.get('Name')
                if raw.get('Date'):
                    ldate = datetime.strptime(raw.get('Date'), '%d/%m/%Y')
                if raw.get('Gross'):
                    asset_data['value'] = float(raw.get('Gross'))
                if raw.get('Category'):
                    if self.find_asset_category(raw.get('Category')):
                       asset_data['category_id'] = self.find_asset_category(raw.get('Category'))
                asset_data['method_period'] =  1
                asset_data['method_number'] =  1/float(raw.get('Dep'))*12
                asset_data['date'] =  ldate
                asset_data['method'] =  'linear'
                asset_data['prorata'] = True
                
                asset_id = asset_pool.create(asset_data)
                               
                    
    def upload_complaint_data(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
            for raw in list_raw_data:
                old_data = new_data = {}
                assignee =self.find_user(raw.get('Assignee'))
                building_id = self.find_building(raw.get('Building')) 
                module_id = self.find_module(raw.get('Flat'))                                                         
                category = 'gen'
                partner_id =  self.find_tenant(raw.get('Vendor'))   
                amount = raw.get('cost')
                date_assign = self.date_checking(raw.get('Date'))
                date_complete = self.date_checking(raw.get('completion'))
                project_name= self.find_prjtname(raw.get('Job Type'))
                if not project_name:
                    project_name = self.env['project.name'].create({'name':raw.get('Job Type')})
                if raw.get('status') == 'New':
                    state ='start' 
                if raw.get('status') == 'Done':
                    state ='done'      
                if raw.get('status') == 'In process':
                    state ='new' 
                if raw.get('status') == 'Waiting for Approval':
                    state ='Waiting' 
                if raw.get('status') == 'Rejected':
                    state ='rejected' 
                d1  = ''
                d2  = ''    
                if raw.get('Description'):
                    d1 = raw.get('Description')
                if raw.get('Desc'):  
                    d2 =  raw.get('Desc')
                d3 = str(d1) +  "<br></br>" +  str(d2)
                if raw.get('Job Type'):
                    old_data['building_id'] = building_id.id
                    old_data['pjt_name_id'] = project_name.id
                    old_data['user_id'] = assignee.id
                    old_data['module_id'] = module_id.id
                    old_data['category'] = category
                    old_data['date_assign'] = date_assign or False
                    old_data['partner_id'] = partner_id.id
                    old_data['amount'] = amount
                    old_data['state'] = state
                    old_data['date_done'] = date_complete
                    old_data['description'] = d3
                    old_data['name'] = 'Complaints'
                    complaints_id = self.env['project.task'].create(old_data) 
                    complaints_id.write({'date_assign':date_assign})      


    
    def upload_customer_data(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
#             customer_pool = self.env['zbbm.module']
            not_found = []
            for raw in list_raw_data:
                old_data = new_data = {}
                module_id = self.find_module(raw.get('Unit No.'))
                customer_id = self.find_customer(raw.get('Building'))
                if not customer_id:
                    customer_id = self.env['zbbm.building'].create({'name':raw.get('Building'),
                                                                            'building_address':1,
                                                                            })
                tenant_id = self.find_tenant(raw.get('Tenant'))
                if not tenant_id:
                    if raw.get('Tenant'):
                        tenant_id = self.env['res.partner'].create({'name':raw.get('Tenant'),
                                                                            'is_tenant':True,
                                                                            'phone':raw.get('Phone'),
                                                                            'email':raw.get('Email')
                                                                            })
                        tenant_id.write({'is_tenant':1})
                tenant_id.write({'is_tenant':1,'phone':raw.get('Phone'),'email':raw.get('Email')})
                account_analytic_id= self.account_analytic_id(raw.get('Cost centre'))
                if not account_analytic_id:
                    account_analytic_id = self.env['account.analytic.account'].create({'name':raw.get('Cost centre')})
                
                type_id = self.find_type(raw.get('Type'))
                if not type_id:
                    type_id = self.env['zbbm.type'].create({'name':raw.get('Type')})
                if raw.get('Unit No.'):
                    if len(raw.get('Unit No.')) == 2:
                        level= raw.get('Unit No.')[1]
                    else:
                        level= raw.get('Unit No.')[0]
                            
                if raw.get('Status') == 'Amendment Lease Signed':
                    status ='asigned'  
                elif raw.get('Status') == 'New Lease Signed':   
                    status = 'new' 
                elif raw.get('Status') == 'LEGAL':   
                    status = 'legal'
                elif raw.get('Status') == 'In Process':   
                    status = 'process'    
                elif raw.get('Status') == 'Amendment Lease Pending':   
                    status = 'pending'    
                else:
                    status = 'vacant' 
                if raw.get('State'):
                    state='occupied'     
                else:
                    state='available'     
                if raw.get('Start Date'):                                                              
                    ldate = datetime.strptime(raw.get('Start Date'), '%d/%m/%Y')
                
                if raw.get('End Date'):                                                              
                    rdate = datetime.strptime(raw.get('End Date'), '%d/%m/%Y') 
                area =raw.get('Size')
                if raw.get('Size') == 'Roof': 
                    area = 0  
                security = False
                if raw.get('Security Deposit(BD)'):
                    security =float(raw.get('Security Deposit(BD)'))
                rent =False
                if raw.get('Rent'):
                    rent = float(raw.get('Rent'))
                if raw.get('Unit No.'): 
                    old_data['building_id'] = customer_id.id
                    old_data['state'] = state
                    old_data['name'] = raw.get('Unit No.')
                    old_data['tenant_id'] = tenant_id.id
                    old_data['type'] = type_id.id
                    old_data['floor_area'] = area
                    old_data['rental_start_date'] = ldate
                    old_data['rental_end_date'] = rdate
                    old_data['status'] = status
                    old_data['level'] = level
                    old_data['feature_description'] = raw.get('Remarks')
                    old_data['monthly_rate'] = rent
                    old_data['advance'] = security
                    old_data['account_analytic_id']= account_analytic_id.id
                    
                       
                    module_id = self.env['zbbm.module'].create(old_data)       
        return True
    
    
    def upload_maintenance_data(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
            for raw in list_raw_data:
                old_data = new_data = {}
                building_id = self.find_building(raw.get('Unit No.'))
    
    
    
    def upload_product_data(self):
         pass
     
     
    def upload_unit_data(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
            for raw in list_raw_data:
                old_data = new_data = {}
                building_id = self.find_building(raw.get('Name'))
                type = self.find_unit_type(raw.get('type'))
                
                if  building_id:
                    old_data['building_id'] = building_id.id
                    old_data['name'] = raw.get('Units')
                    old_data['unit_area'] = raw.get('area')
                    old_data['balcony_area'] = raw.get('balcony')
                    old_data['total_area'] = float(raw.get('area'))+float(raw.get('balcony'))
                    if raw.get('type'):
                        if not type:
                            tp =self.env['zbbm.type.unit'].create({'name':raw.get('type')})
                            old_data['type'] = tp.id
                        else:
                            old_data['type'] = type.id
                    if not raw.get('price'):
                        old_data['price'] = 0
                    else:
                        old_data['price'] = raw.get('price')
                    
                    self.env['zbbm.unit'].create(old_data)
                    
                    
    def import_tijaria_account_data(self):
        not_found = []
        for entry in self:
            list_raw_data = self.get_data_from_attchment(entry.csv_file, entry.csv_file_name)
            count = 0
            sum_d = sum_c = 0
            line_list = []
            for raw in list_raw_data:
                move_line_data, move_vals = {}, {}
                Partner_id = self.find_tenant(raw.get('Partner'))
                count = count + 1
                if raw.get('Debit') and float(raw.get('Debit')) >0:
                    move_line_data['account_id'] = self.find_account(raw.get('Code')).id
                    
                    if not move_line_data['account_id']:
                        not_found.append(raw.get('Code'))
                    if  move_line_data['account_id']:
                          
                        move_line_data['partner_id'] = Partner_id.id or False
                        move_line_data['name'] = 'Debit'
                        move_line_data['debit'] = round(float(raw.get('Debit')), 3)
                        line_list.append((0, 0, move_line_data))
                        sum_d += round(abs(float(raw.get('Debit'))), 3)
                   
                if raw.get('Credit') and float(raw.get('Credit')) > 0:
                    move_line_data['account_id'] = self.find_account(raw.get('Code')).id
                    if not move_line_data['account_id']:
                        not_found.append(raw.get('Code'))
                    if  move_line_data['account_id']:
                        move_line_data['partner_id'] = Partner_id.id or False
                        move_line_data['name'] = 'Credit'
                        move_line_data['credit'] = round(abs(float(raw.get('Credit'))), 3)
                        sum_c += round(abs(float(raw.get('Credit'))), 3)
                        line_list.append((0, 0, move_line_data))
            if line_list:
                move_vals = {
                         'journal_id' : 3,
                         'ref' : 'Trial Balance Import',
                         'line_ids':line_list,
                         'date': datetime.strptime('01/01/2018', '%d/%m/%Y')
                            }
                
                move = self.env['account.move'].create(move_vals)
            

                    

    def upload_customer_details(self):
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
            for raw in list_raw_data:
                old_data = new_data = {}
                customer_id = self.find_cud(raw.get('Name'))
                if not customer_id:
                    old_data['name'] = raw.get('Name')
                    print(raw.get('Name'),"name-----")
                    self.env['res.partner'].create(old_data)               
                    
     
    def import_daybok_account_data(self):
        not_found = []
        for entry in self:
            list_raw_data = self.get_data_from_attchment(entry.csv_file, entry.csv_file_name)
            count = 0
            sum_d = sum_c = 0
            line_list = []
            for raw in list_raw_data:
                move_line_data, move_vals = {}, {}
                Partner_id = self.find_tenant(raw.get('Name'))
                count = count + 1
                date = self.date_checking(raw.get('Date'))
                if raw.get('Document type') == 'Sales':
                    move_line_data['account_id'] = self.find_account_name(raw.get('Account')).id
                    if not move_line_data['account_id']:
                        not_found.append(raw.get('Account'))
                    if  move_line_data['account_id']:
                        if raw.get('description'):
                            particular = raw.get('description')
                        if raw.get('Amount'):
                            amount = raw.get('Amount') 
                        if raw.get('source docu'):
                            origin = raw.get('source docu')     
                            
                        if raw.get('analytic account'):
                            account_analytic_id = self.account_analytic_id(raw.get('analytic account')).id         
                        
                        vals = {  
                                'name': 'Invoice Import',
                                'partner_id': Partner_id.id,
                                'type': 'out_invoice',
                                'account_id': Partner_id.property_account_receivable_id.id,
                                'date_invoice': date,
#                                 'building_id': building or '',
#                                 'module_id': module or '',
#                                 'unit_id':unit or '',
                                'origin':origin or '',
                                'invoice_line_ids': [(0, 0, {
                                                        'name': particular or '',
                                                        'price_unit': amount,
                                                        'quantity': 1,
                                                        'account_analytic_id':account_analytic_id,
                                                        'account_id': self.find_account_name(raw.get('Account')).id,
                                                        })],
                                        }
                        invoice_id = self.env['account.invoice'].create(vals)
                        invoice_id.action_invoice_open()
                    
                if raw.get('Document type') == 'Purchase':
                    move_line_data['account_id'] = self.find_account_name(raw.get('Account')).id
                    if not move_line_data['account_id']:
                        not_found.append(raw.get('Account'))
                    if  move_line_data['account_id']:
#                         if raw.get('Building'):
#                             building = self.find_building(raw.get('Building')).id
#                         if raw.get('Module'):
#                             module = self.find_module(raw.get('Module')).id
#                         if raw.get('Unit'):
#                             unit = self.find_unit(raw.get('Unit')).id        
                        if raw.get('description'):
                            particular = raw.get('description')
                        if raw.get('Amount'):
                            amount = raw.get('Amount') 
                        if raw.get('source docu'):
                            origin = raw.get('source docu')     
                            
                        if raw.get('analytic account'):
                            account_analytic_id = self.account_analytic_id(raw.get('analytic account')).id         
                        else:
                            account_analytic_id =False
                        vals = {  
                                'name': 'Bill Import',
                                'partner_id': Partner_id.id,
                                'type': 'in_invoice',
                                'account_id': Partner_id.property_account_payable_id.id,
                                'date_invoice': date,
#                                 'module_id': module,
#                                 'unit_id':unit,
                                'origin':origin or '',
                                'invoice_line_ids': [(0, 0, {
                                                        'name': particular or '',
                                                        'price_unit': amount,
                                                        'quantity': 1,
                                                        'account_analytic_id':account_analytic_id,
                                                        'account_id': self.find_account_name(raw.get('Account')).id,
                                                        })],
                                        }
                        invoice_id = self.env['account.invoice'].create(vals)
                        invoice_id.action_invoice_open()
                if raw.get('Document type') == 'Payment':
                    payment_type ='outbound'
                    if Partner_id.customer:
                        partner_type ='customer'   
                    else:
                        partner_type ='supplier' 
                    if raw.get('Payments'):
                        amount = raw.get('Payments')
                    if raw.get('Paid by'):
                        journal = self.find_journal(raw.get('Paid by'))
                    if raw.get('description'):
                        particular = raw.get('description')      
                     
                    vals = {    'communication':particular,
                                'partner_id': Partner_id.id,
                                'payment_type':payment_type,
                                'partner_type': partner_type,
                                'amount': amount,
                                'payment_method_id':journal.outbound_payment_method_ids.id,
                                'journal_id': journal.id,
                                'payment_date':date,}
                    payment_id = self.env['account.payment'].create(vals)
                    payment_id.post()
                if raw.get('Document type') == 'Receipt':
                    payment_type ='inbound'
                    if Partner_id.customer:
                        partner_type ='customer'   
                    else:
                        partner_type ='supplier' 
                    if raw.get('Payments'):
                        amount = raw.get('Payments')
                    if raw.get('Paid by'):
                        journal = self.find_journal(raw.get('Cash')) 
                     
                    vals = {    'communication':particular,
                                'payment_type':payment_type,
                                'partner_id': Partner_id.id,
                                'partner_type': partner_type,
                                'payment_method_id':journal.outbound_payment_method_ids.id,
                                'amount': amount,
                                'journal_id': journal.id,
                                'payment_date':date,}
                    payment_id = self.env['account.payment'].create(vals)
                    payment_id.post()
                    
      
    def import_payable_account_data(self):
        
        not_found = []
        for entry in self:
            list_raw_data = self.get_data_from_attchment(entry.csv_file, entry.csv_file_name)
            count = 0
            sum_d = 0
            sum_c =0
            line_list = []
            for raw in list_raw_data:
                move_line_data, move_vals = {}, {}
                Partner_id = self.find_tenant(raw.get('Partner'))
                count = count + 1
                if raw.get('Debit') and float(raw.get('Debit')) >0:

                    move_line_data['account_id'] = self.find_account_name(raw.get('Account Name')).id
                    
                    if not move_line_data['account_id']:
                        not_found.append(raw.get('Account Name'))
                    if  move_line_data['account_id']:
                        move_line_data['name'] = 'Debit'
                        move_line_data['debit'] = round(float(raw.get('Debit')), 3)
                        line_list.append((0, 0, move_line_data))
                        sum_d += round(abs(float(raw.get('Debit'))), 3)
                   
                if raw.get('Credit') and float(raw.get('Credit')) > 0:
                    move_line_data['account_id'] = self.find_account_name(raw.get('Account Name')).id
                    if  move_line_data['account_id']:
                        move_line_data['name'] = 'Credit'
                        move_line_data['credit'] = round(float(raw.get('Credit')), 3)
                        sum_c += round(abs(float(raw.get('Credit'))), 3)
                        line_list.append((0, 0, move_line_data))
            if sum_d != sum_c:
                if sum_c>sum_d:
                    line_list.append((0,0,{'name':'Adjusted Trial Balance',
                                               'debit':round(float(sum_c-sum_d), 3),
                                               'account_id':self.find_account('101600').id
                                               }))
                    
                    sum_c += round(abs(float(sum_d-sum_c)), 3)
                else:
                    line_list.append((0,0,{'name':'Adjusted Trial Balance',
                                               'credit':round(float(sum_d-sum_c), 3),
                                               'account_id':self.find_account('101600').id
                                               }))
                    
                    sum_d += round(abs(float(sum_c-sum_d)), 3)
                    
                         
            
            if line_list:
                move_vals = {
                         'journal_id' : 3,
                         'ref' : 'Trial Balance Import Payable',
                         'line_ids':line_list,
                         'date': datetime.strptime(raw.get('Date'), '%d/%m/%Y')
                            }
                
                move = self.env['account.move'].create(move_vals)

    
    def import_invoice(self):   
        not_found = []
        for entry in self:
            list_raw_data = self.get_data_from_attchment(entry.csv_file, entry.csv_file_name)
            count = 0
            sum_d = 0
            sum_c =0
            line_list = []
            line_list2 =[]
            for raw in list_raw_data:
                line_list = []
                line_list2 =[]
                move_line_data, move_vals = {}, {}
                Partner_id = self.find_tenant(raw.get('Particulars'))
                if not Partner_id:
                    if raw.get('Particulars'):
                        Partner_id = self.env['res.partner'].create({'name':raw.get('Particulars'),
                                                                            'is_tenant':True,
                                                                            'phone':raw.get('Phone'),
                                                                            'email':raw.get('Email')
                                                                            })
                count = count + 1
                date = self.date_checking(raw.get('Doc. Date'))
                 
                if Partner_id:
                    if raw.get('Debit'): 
                        move_line_data['name']='data import'
                        move_line_data['quantity'] = 1
                        move_line_data['price_unit'] = raw.get('Debit')
                        move_line_data['account_id'] = self.find_account('420000').id
                        line_list.append((0, 0, move_line_data))
                     
                        building_id= self.find_building(raw.get('Asset'))
                        if building_id:
                            
                            mod = self.env['zbbm.module'].search([('building_id','=', building_id.id),('name','=',raw.get('Unit No.'))]).id
                        else:
                            not_found.append(raw.get('Unit No.'))
                            mod =False  
                            building_id =False  
                        journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                        if journal:
                            acct_id = Partner_id.property_account_receivable_id.id 
                        if line_list:
                            move_vals = {
                                 'partner_id' : Partner_id.id,
                                 'module_id' : mod,
                                 'building_id':building_id.id,
                                 'invoice_line_dates_ids':line_list,
                                 'journal_id':journal.id,
                                 'account_id':Partner_id.property_account_receivable_id.id,
                                 'date_invoice':date or raw.get('Doc. Date')
                                    }
                         
                        move = self.env['account.invoice'].create(move_vals) 
                    if  raw.get('Credit'): 
                        
                        journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                        building_id= self.find_building(raw.get('Asset'))
                        if building_id:
                            module = self.env['zbbm.module'].search([('building_id','=', building_id.id),('name','=',raw.get('Unit No.'))])
                        payment = self.env['account.payment'].create({'name':'data import',
                                                                          'payment_type':'inbound',
                                                                          'amount':float(raw.get('Credit')),
                                                                          'journal_id':self.find_journal('Cash').id,
                                                                          'payment_date':datetime.strptime(raw.get('Doc. Date'), '%d-%m-%Y'),
                                                                          'module_id':module.id,
                                                                          'building_id':building_id.id,
                                                                          'partner_type':'customer',
                                                                          'partner_id':Partner_id.id,
                                                                          'payment_method_id': journal.inbound_payment_method_ids.id
                                                                          })  
                    
                
        
        
        
                
    def find_journal(self,Name):  
        account_ids = False
        account_pool = self.env['account.journal']
        account_ids = account_pool.search([('name', '=', Name)])
        if account_ids:
            account_ids = account_ids[0]
        return account_ids               
                 
     
     
                    
                    
    def find_account(self,Account):
        account_ids = False
        account_pool = self.env['account.account']
        account_ids = account_pool.search([('code', '=', Account)])
        if account_ids:
            account_ids = account_ids[0]
        return account_ids 
    
    def account_analytic_id(self,Account):
        account_ids = False
        account_pool = self.env['account.analytic.account']
        account_ids = account_pool.search([('name', '=', Account)])
        if account_ids:
            account_ids = account_ids[0]
        return account_ids 
    
    def find_account_name(self,Account):
        account_ids = False
        account_pool = self.env['account.account']
        account_ids = account_pool.search([('name', '=', Account)])
        if account_ids:
            account_ids = account_ids[0]
        return account_ids               
                    
    
    def find_module(self,customer):
        supplier_ids = False
        supplier_pool = self.env['zbbm.module']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids
    
    
    def find_unit(self,customer):
        supplier_ids = False
        supplier_pool = self.env['zbbm.unit']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids
    
    
    
    def find_unit_type(self,customer):
        supplier_ids = False
        supplier_pool = self.env['zbbm.type.unit']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids 
         
    
    def find_building(self,customer):
        supplier_ids = False
        supplier_pool = self.env['zbbm.building']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids     
    
    
        
    
    def find_type(self,customer):
        supplier_ids = False
        supplier_pool = self.env['zbbm.type']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids     
    
    
    def find_tenant(self,customer):
        supplier_ids = False
        supplier_pool = self.env['res.partner']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids     
    
    def find_user(self,customer):
        supplier_ids = False
        supplier_pool = self.env['res.users']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids  
    
    
    
    
    def find_customer(self,customer):
        supplier_ids = False
        supplier_pool = self.env['zbbm.building']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids     
    
    def find_prjtname(self,customer):
        supplier_ids = False
        supplier_pool = self.env['project.name']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids     
    
    
    def find_cud(self,customer):
        supplier_ids = False
        supplier_pool = self.env['res.partner']
        supplier_ids =  supplier_pool.search([('name','=',customer)])
        if supplier_ids:
            supplier_ids = supplier_ids[0]
        return supplier_ids
    
    def date_checking(self,date):
        if date:
            if date.find('/') > 0:
                date = datetime.strptime(date.strip(),'%d/%m/%Y').strftime("%Y-%m-%d")
            elif date.find('.') > 0:
                date = datetime.strptime(date.strip(),'%d.%m.%Y').strftime("%Y-%m-%d")
            elif date.find('-') > 0:
                date = datetime.strptime(date.strip(),'%d-%m-%Y').strftime("%Y-%m-%d")
            else:
                date = datetime.strptime(date.strip(),'%d-%m-%Y').strftime("%Y-%m-%d")
            return date
         