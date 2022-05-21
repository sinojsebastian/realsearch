# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.tools.translate import _
from datetime import date,datetime
from odoo.exceptions import AccessError,UserError,Warning
from lxml import etree
import re
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ServiceInvoiceWizard(models.TransientModel):
    _name = 'service.invoice.wizard'
    _description = "Service Charge Invoice"
    @api.model
    def default_get_date(self):
        '''
            Default getting of Date 
        '''
        
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        building_obj = self.env['zbbm.building'].browse(active_id)
        if building_obj.next_service_charge_invoice_date:
            return building_obj.next_service_charge_invoice_date
        elif building_obj.hand_over_date:
            return building_obj.hand_over_date
        elif building_obj.dlp_end_date: 
           return building_obj.dlp_end_date
            
 
    @api.model  
    def default_get_journal(self):
        '''
            Default getting of Journal from configuration 
        '''
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        building_obj = self.env['zbbm.building'].browse(active_id)
        params = self.env['ir.config_parameter'].sudo()        
        journall_id=params.get_param('zb_bf_custom.service_journal_id') or False, 
       
        if journall_id:
            j=journall_id[0]
            journal = self.env['account.journal'].search([('id','=',int(j))])
            if not journal:
                raise UserError(_('Please Configure a service journal'))
            else:
                return journal.id
            
    @api.onchange('date','duration')
    def compute_to_date(self):
        for rec in self:
            if rec.date:
                rec.to_date = rec.date + relativedelta(years=rec.duration,days=-1)

            
    date = fields.Date("From Date",default=default_get_date,required=True)
    to_date = fields.Date("To Date")
    invoice_date = fields.Date("Invoice Date",default=fields.Date.today)
    journal_id = fields.Many2one('account.journal','Service Journal', default=default_get_journal)
    duration = fields.Integer('Duration(years)',default=1)
    admin_fee_check = fields.Boolean('Include Admin fee',default=False)
    admin_fee = fields.Float('Admin Fees',required=True)
    
    
  
    
    def service_charge_inv_creation(self):
        '''
            Service Charge Invoice generation function for each Units.
        '''
        
     
        
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        building_obj = self.env['zbbm.building'].browse(active_id)
        params = self.env['ir.config_parameter'].sudo() 
        pdt_ids = params.get_param('zb_bf_custom.service_product_id') or False,
        
        
        if self.to_date and self.date:
            if self.to_date < self.date:
                raise Warning(_('To date should be always greater than From date!!'))
            
        if not self.duration:
            raise Warning(_('Duration should be greater than 0'))
        
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        if not building_income_account_id:
            raise Warning(_('Please Configure Building Income Account'))
        
        admin_fee_pdt_id = params.get_param('zb_bf_custom.admin_fee_product_id') or False,
        admin_fee_product = self.env['product.product'].search([('id','=',int(admin_fee_pdt_id[0]))])
        if admin_fee_pdt_id[0]:
            temp = re.findall(r'\d+', admin_fee_pdt_id[0]) 
            admin_fee_pdt_list = list(map(int, temp))
        else:
            raise Warning(_("""Please configure Product For Admin Fees in the Accounting Settings"""))
        
        admin_fee_journal = params.get_param('zb_bf_custom.admin_fee_journal_id') or False,
        if not admin_fee_journal:
            raise Warning(_('Please Configure Admin Fee Journal'))

        if pdt_ids[0]:
            temp = re.findall(r'\d+', pdt_ids[0]) 
            pdt_list = list(map(int, temp))
            service_product = self.env['product.product'].search([('id','=',int(pdt_ids[0]))])
        
        for building in building_obj:
            
            duration = self.duration
            
            for flat in building.module_ids:
                
                
                if flat.owner_id:
                    partner_id = flat.owner_id
                else:
                    owner_id=params.get_param('zb_bf_custom.owner_id') or False,
                    if owner_id:
                        owner=owner_id[0]
                        partner_id = self.env['res.partner'].search([('id','=',int(owner))])
                lease = self.env['zbbm.module.lease.rent.agreement'].search([('building_id','=',building.id),('owner_id','=',partner_id.id),('state','=','active'),('subproperty','=',flat.id)])
                
                
                if building.next_service_charge_invoice_date:
                    inv_date = building.next_service_charge_invoice_date
                elif building.hand_over_date:
                    inv_date = building.hand_over_date
                elif building.dlp_end_date:
                    inv_date =  building.dlp_end_date
                else:
                    inv_date = self.date
                    
                if building.analytic_account_id:
                    analytic = building.analytic_account_id.id
                else:
                    analytic = '' 
                    
                lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
                date_format = lang_id.date_format
                formatted_date = ''
                to_date = ''
                formatted_todate = ''
                if self.date:
                    formatted_date = datetime.datetime.strptime(str(self.date),DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%b-%Y')
                if self.to_date:
                    formatted_todate = datetime.datetime.strptime(str(self.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%b-%Y')

                if flat.service_charge:
                    inv_vals = {
                          'partner_id': partner_id,
                          'type': 'out_invoice',
    #                       'account_id': agreement.tenant_id.property_account_receivable_id.id,
                          'is_service_charge':True,
                          'from_date':self.date,
                          'to_date':self.to_date,
                          'invoice_date': self.invoice_date,
                          'building_id': building.id,
                          'module_id': flat.id,
                          'lease_id':lease.id,
                          'journal_id' :self.journal_id.id,
                          'invoice_line_ids': [(0, 0, {
                                                'price_unit': flat.service_charge,
                                                'name' : 'Service Charges for the period {} to {}'.format(formatted_date,formatted_todate),
                                                'product_id' : pdt_list[0] if pdt_ids[0] else '',
                                                'quantity': 1,
                                                'account_id': service_product.property_account_income_id.id if service_product.property_account_income_id else int(building_income_account_id),
                                                'analytic_account_id':analytic,
                                                'tax_ids' : service_product.taxes_id.ids
    #                                             'lease_id':self.name
                                                })]
                        }
                    invoice_id = self.env.get('account.move').create(inv_vals)
                    # invoice_id.action_post()
                
                if self.admin_fee:
                    building.admin_fee = self.admin_fee  
                    inv_admin_vals = {
                      'partner_id': partner_id,
                      'type': 'out_invoice',
                      'invoice_date': self.invoice_date,
                      'from_date':self.date,
                      'to_date':self.to_date,
                      'building_id': building.id,
                      'module_id': flat.id,
                      'lease_id':lease.id,
                      'journal_id':int(admin_fee_journal[0]),
                      'invoice_line_ids': [(0, 0, {'price_unit': self.admin_fee,
                                            'name' : 'Admin Fees for the period {} to {}'.format(formatted_date,formatted_todate),
                                            'product_id' : admin_fee_pdt_list[0] if admin_fee_pdt_id[0] else '',
                                            'quantity': 1,
                                            'account_id': admin_fee_product.property_account_income_id if admin_fee_pdt_id[0] else '',
                                            'analytic_account_id':analytic,
                                            'tax_ids' : admin_fee_product.taxes_id if admin_fee_pdt_id[0] else ''
                                            })]
                    }
                    
                    inv_admin_id = self.env.get('account.move').create(inv_admin_vals)
                    # inv_admin_id.action_post()
                else:
                    building.admin_fee = 0.00                                                      
                  
            if self.date:
                building.next_service_charge_invoice_date = self.date + relativedelta(years=duration)
            
            
            
            
