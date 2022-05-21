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


class DataImport(models.TransientModel):
    _name = 'wizard.import.data'
    _inherit = 'data_import.wizard'
    _description = 'Wizard for Import Data'
    
    
    csv_file_name = fields.Char('Xls File Name', size=64)
    csv_file = fields.Binary('Xls File')
    building_id = fields.Many2one('zbbm.building',string="Building")
    
    
    def get_service_vals(self, service_id, raw, service_type):
        
        by_owner = raw.get('By Owner')
        by_tenant = raw.get('By Tenant ')
        by_owner_tabreed = raw.get('Tabreed  By Owner ')
        batelco_package = raw.get('Batelco Pakage')
        cleaning = raw.get('Cleaning Service ')
        
        tenant_share,owner_share = 0,0
        bill = ''
        if service_type =='ewa':
            #EWA Services
            if by_owner:
                if by_owner.find('+') > 0:
                    owner_share = float(by_owner.split('+')[0])
                elif by_owner.upper() == 'paid by tenant' or by_owner =='by tenant':
                    bill = 'tenant'
                elif by_owner == 'By Owner':
                    bill = 'owner'
                else:
                    if by_owner not in 'NA':
                        owner_share = float(by_owner)
            if by_tenant:    
                if by_tenant.upper() == 'EXCESS':
                    bill = 'tenant'
                elif by_tenant.find('+') > 0:
                    tenant_share = float(by_tenant.split('+')[0])
                elif by_tenant.upper() == 'BY TENANT' or by_tenant == 'by tenat' or by_tenant == 'Actual':
                    bill = 'tenant'
                else:
                    if by_tenant not in 'NA':
                        tenant_share = float(by_tenant)
                        
        elif service_type =='internet':
            #Internet Services
            if batelco_package:
                if batelco_package == 'by tenant':
                    bill = 'tenant'
                elif batelco_package == 'By Owner' :
                    bill = 'owner'
                else:
                    owner_share = float(batelco_package)
                    bill = 'owner'
                    
        elif service_type == 'tabreed':
            #Tabreed Services
            if by_owner_tabreed:
                bill = 'owner'
                owner_share = float(by_owner_tabreed)
                
        elif service_type == 'cleaning':
            #Cleaning Services
            if cleaning:
                bill = 'fixed'
                owner_share = float(cleaning)
        
        service_vals = {'bill':bill, 'owner_share':owner_share,'tenant_share':tenant_share,'managed_by_rs':True}
        return service_vals   
        
        

    def upload_data(self):
        
        lease_agreement_obj =  self.env['zbbm.module.lease.rent.agreement']
        module_obj = self.env['zbbm.module']
        user_obj = self.env['res.users']
        
        if self.csv_file:
            list_raw_data = self.get_data_from_attchment(self.csv_file, self.csv_file_name)
            if not list_raw_data:
                raise UserError(_("Cannot import blank sheet."))
            
            for raw in list_raw_data:
                
                #Raw data fetched and assigned
                flat_no = raw.get('Flat No')
                mgt_status = raw.get('Mgt Status')
                occupancy_status = raw.get('Occupancy Status')
                tenant_name = raw.get('Tenant Name')
                tenant_type = raw.get('Tenant Type ')
                telephone_no = raw.get('Telephone No ')
                mobile_no = raw.get('Mobile No ')
                email_1 = raw.get('Email-1')
                email_2 = raw.get('Email-2')
                deposit = raw.get('Deposit ')
                rent_amount = raw.get('Rent Amount')
                pmt_mode = raw.get('PMT Mode')
                lease_start_date = raw.get('Lease Start date')
                lease_end_date = raw.get('Lease End Date')
                by_owner = raw.get('By Owner')
                by_tenant = raw.get('By Tenant ')
                batelco_package = raw.get('Batelco Pakage')
                property_advisor = raw.get('Property Advisor')
                date_of_vacancy = raw.get('Date of Vacancy ')
                cpr_no = raw.get('CPR No')
                passport_no = raw.get('Passport No')
                nationality_id = raw.get('Nationality ')
                building_id = self.building_id
                by_tenant = raw.get('By Owner')
                by_owner = raw.get('By Tenant ')
                by_owner_tabreed = raw.get('Tabreed  By Owner ')
                batelco_package = raw.get('Batelco Pakage')
                clenaing = raw.get('Cleaning Service ')
                updated_date = raw.get('Updated after 27/6/2021')
                
                nationality = False
                if nationality_id and nationality_id != 'N/A':
                    nationality_ids = self.env['res.nationality'].search([('name','=',nationality_id)],limit=1)
                    if len(nationality_ids) > 0:
                       nationality =  nationality_ids
                    else:
                       nationality = self.env['res.nationality'].create({'name':nationality_id})
                
                #Checking Partner and Creation
                tenant_obj = self.env['res.partner']
                tenant_id = self.env['res.partner'].search([('name','=',tenant_name)])
                type_tenant =''
                if tenant_type == 'Individual':
                    type_tenant = 'person'
                    cpr = cpr_no
                    cr = ''
                else:
                    type_tenant = 'company'
                    cr = cpr_no
                    cpr = ''
                     
                tenant_data = {
                                    'name':tenant_name,
                                    'is_tenant':True,
                                    'company_type':type_tenant,
                                    'phone':telephone_no if telephone_no != 'N/A' else '',
                                    'mobile':mobile_no if mobile_no != 'N/A' else '',
                                    'email':email_1,
                                    'cpr': cpr if cpr_no != 'N/A' else False,
                                    'cr': cr if cpr_no != 'N/A' else False,
                                    'passport': passport_no if passport_no != 'N/A' else '',
                                    'nationality_id':nationality.id if nationality else False,
                                  }
                
                if not tenant_id:    
                    tenant_id = tenant_obj.create(tenant_data)
                else:
                    tenant_id.write(tenant_data)
                
                #Finding Module and Creation
                if mgt_status == 'M':
                    managed = True
                else:
                    managed = False
                module_id = module_obj.search([('name','=',flat_no),('building_id','=',building_id.id)])
                module_data = {
                        'name':flat_no,
                        'building_id':building_id.id,
                        'managed':managed,
                        'monthly_rate':rent_amount,
                        'deposit':deposit,
                        }   
                if flat_no != None:
                    if not module_id:
                        module_id = module_obj.create(module_data)
                        module_id.make_available()
                    else:
                        module_id.write(module_data)
                        
                #Add Services in Flat
                ewa_service_ids = self.env['zbbm.services'].search([('product_id.id','=',3),('module_id','=',module_id.id)])
                if len(ewa_service_ids) > 0:
                   ewa_vals = self.get_service_vals(ewa_service_ids, raw, 'ewa')
                   ewa_service_ids.write(ewa_vals) 
                
                internet_service_ids = self.env['zbbm.services'].search([('product_id.id','=',5),('module_id','=',module_id.id)],limit=1)
                if len(internet_service_ids) > 0:
                   internet_vals = self.get_service_vals(internet_service_ids, raw, 'internet')
                   internet_service_ids.write(internet_vals) 
                   
                tabreed_service_ids = self.env['zbbm.services'].search([('product_id.id','=',11),('module_id','=',module_id.id)],limit=1)
                if len(tabreed_service_ids) > 0:
                   tabreed_vals = self.get_service_vals(tabreed_service_ids, raw, 'tabreed')
                   tabreed_service_ids.write(tabreed_vals) 
                   
                cleaning_service_ids = self.env['zbbm.services'].search([('product_id.id','=',9),('module_id','=',module_id.id)],limit=1)
                if len(cleaning_service_ids) > 0:
                   cleaning_vals = self.get_service_vals(cleaning_service_ids, raw, 'cleaning')
                   cleaning_service_ids.write(cleaning_vals) 
                
                #checking Property Advisor    
                if property_advisor:
                    user_id = self.env['res.users'].search([('name','=',property_advisor)])
                    if not user_id:
                        user_data_obj ={
                            'name':property_advisor,
                            'login':property_advisor,
                            }
                        user_id = user_obj.create(user_data_obj)
                else:
                    user_id = False
                    
                # Managed Checking   
                if mgt_status == 'M':
                    managed = True
                else:
                    managed = False
                 
                #Agreement Date Checking    
                if lease_start_date:
                    startdate = datetime.strptime(lease_start_date, '%d-%m-%Y').date()
                else:
                    startdate = ''
                if lease_end_date:
                    enddate = datetime.strptime(lease_end_date, '%d-%m-%Y').date()
                else:
                    enddate = ''
                
                lease_id = lease_agreement_obj.search([('building_id','=',building_id.id),('subproperty','=',module_id.id),('state','in',['new','active','approval_waiting','approved'])],limit=1)
                
#                to fetch lease having end date >= july 1st

                params = self.env['ir.config_parameter'].sudo()   
                starting_date = params.get_param('zb_bf_custom.invoice_start_date')
                if not starting_date:
                    raise Warning(_('Please Configure Start Date'))
                start_date = datetime.strptime(starting_date, '%Y-%m-%d').date()

                 
                if startdate and enddate and enddate >= start_date:
                    
                    lease_date_dict ={
                        'tenant_id':tenant_id.id,
                        'building_id':building_id.id,
                        'subproperty':module_id.id if module_id else '',
                        'monthly_rent':rent_amount,
                        'security_deposit':deposit,
                        'adviser_id':user_id.id if user_id else False,
                        'agreement_start_date':startdate,
                        'agreement_end_date':enddate,
                        'managed':managed,
                        }
                    if updated_date != '':
                    
                        if len(lease_id) > 0:
                            lease_id.write(lease_date_dict)
                        else:
                            lease_id = lease_agreement_obj.create(lease_date_dict)
                    
                    
                    lease_id.property_change()
                    lease_id.calculate_commission()
                    lease_id.compute_management_fee()
                    lease_id.state = 'approved'
                    
                    
 #                   Lease Activation Code
#                     wiz_data = {
#                         'start_date':lease_id.agreement_start_date,
#                         'invoice_amount':0.000,
#                         'deposit_amount':deposit,
#                         'advance_payment_mnth':1
#                         }
#                     
#                     agreement_wizard = self.env['agreement.invoice.wizard'].with_context(active_id=lease_id.id).create(wiz_data)
#                     _logger.info("agreeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee %s",agreement_wizard)
#                     agreement_wizard.onchange_date()
#                     _logger.info("onchangeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                    # agreement_wizard.create_invoice_activate_agreement()
                    # _logger.info("activateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                
                    