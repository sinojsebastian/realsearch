# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.tools.translate import _
from datetime import date,datetime,timedelta 
from odoo.exceptions import AccessError,UserError,Warning
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import re


import logging
_logger = logging.getLogger(__name__)


class AgreementInvoiceWizard(models.TransientModel):
    _name = 'agreement.invoice.wizard'
    _description = "Agreement Invoice"


    def get_date(self):
        # active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['zbbm.module.lease.rent.agreement'].browse(active_id)
        if agreement.agreement_start_date:
            return agreement.agreement_start_date
            
            
    def get_to_date(self,from_date,month):
        to_date = from_date + relativedelta(days=-1,months=month)
        return to_date
    
    
    @api.onchange('advance_payment_cycle')
    def set_advance_payment_month(self):
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['zbbm.module.lease.rent.agreement'].browse(active_id)
        for order in self:
            if order.advance_payment_cycle:
                order.advance_payment_mnth = agreement.invoice_cycle_num * order.advance_payment_cycle
            else:
                raise Warning(_('Payment cycle cannot be set to zero'))

        agreement.advance_pay_mnth = self.advance_payment_mnth
        self.onchange_date()
    
    
    @api.onchange('start_date','advance_payment_mnth')
    def onchange_date(self):
        # active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['zbbm.module.lease.rent.agreement'].browse(active_id)
#         num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)+1
#         no_of_days = 0
#         last_day = self.start_date.replace(day = monthrange(self.start_date.year, self.start_date.month)[1])
        no_of_days = (datetime.strptime(str(agreement.agreement_start_date), '%Y-%m-%d')-datetime.strptime(str(self.start_date), '%Y-%m-%d')).days
        params = self.env['ir.config_parameter'].sudo()  
        prorated_calc = params.get_param('zb_bf_custom.rent_prorated_calculation') or False
        if not prorated_calc:
            raise Warning(_('Please Configure Rent Prorated Calculation'))
        
        inv_amt = 0.000
        if prorated_calc == 'monthly':
            inv_amt = (self.advance_payment_mnth*agreement.monthly_rent)+(agreement.monthly_rent/30 * no_of_days)
        else:
            inv_amt = (self.advance_payment_mnth*agreement.monthly_rent) + (agreement.monthly_rent *(12/365) * no_of_days)
        if self.start_date < agreement.agreement_start_date:
#             if self.advance_payment_mnth>1:
            self.invoice_amount = inv_amt
#                 self.invoice_amount = (self.advance_payment_mnth*agreement.monthly_rent)-(agreement.monthly_rent-(agreement.monthly_rent/last_day.day * no_of_days))
#             else:
#                 self.invoice_amount = agreement.monthly_rent/last_day.day * no_of_days
        elif self.start_date == agreement.agreement_start_date:
            if self.advance_payment_mnth>1:
                self.invoice_amount = self.advance_payment_mnth*agreement.monthly_rent
            else:
                self.invoice_amount = agreement.monthly_rent
        if agreement.security_deposit:
            self.deposit_amount = agreement.security_deposit
        else:
            self.deposit_amount = 0.000
            
    
    def get_months(self,date1,date2):
        
        from_date = date2
        agreement_to_date = date1
        day = from_date.day
        month = 0
        year = 0
        while from_date <= agreement_to_date:
            to_date = from_date + relativedelta(months=1)
            if day <= monthrange(to_date.year,to_date.month)[1]:
                from_date = to_date.replace(day = day)
            else:
                last_day = to_date.replace(day = monthrange(to_date.year,to_date.month)[1])
                from_date = to_date.replace(day = last_day.day)
            month+=1
            
        return month
    
    
    def create_invoice_activate_agreement(self):
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['zbbm.module.lease.rent.agreement'].browse(active_id)
        
        if not agreement.invoice_cycle_num:
            raise Warning(_('Invoice cycle number should be greater than 0'))
        
        if agreement.subproperty:
            _logger.info("agreement........................................................ %s",agreement.subproperty)
            subproperty = agreement.subproperty
            subproperty.sudo().monthly_rate = agreement.monthly_rent
            subproperty.sudo().tenant_id = agreement.tenant_id.id
            leases = subproperty.agreement_ids.filtered(lambda r: r.state == 'active')
#             for lease in leases:
            if subproperty.state in ['available','book']:
                subproperty.sudo().state='occupied'
            elif subproperty.state == 'new':
                subproperty.sudo().state == 'available'
            else:
                raise UserError('Already Occupied!!!')
        else:
            raise UserError('Please Assign Subproperty!!!')
        agreement.state='active'
         
        if not agreement.tenant_id:
            raise Warning(_('Please Assign Tenant'))
        
        params = self.env['ir.config_parameter'].sudo()    
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        if not building_income_account_id:
            raise Warning(_('Please Configure Building Income Account'))
        
        
        building_expense_account_id = params.get_param('zb_bf_custom.building_expense_acccount_id') or False
        if not building_expense_account_id:
            raise Warning(_('Please Configure Building Expense Account'))
        
     
        if not building_income_account_id:
            journal = self.env.get('account.journal').search([('type','=', 'purchase')], limit=1)
            sales_journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
            if journal :
                acct_id = journal[0].default_debit_account_id.id
            if sales_journal:
                sales_acct_id = sales_journal[0].default_credit_account_id.id
        else:
            acct_id = int(building_expense_account_id)
            sales_acct_id = int(building_income_account_id)
         
        if agreement.subproperty.building_id.analytic_account_id:
            analytic = agreement.subproperty.building_id.analytic_account_id.id
        else:
            analytic = '' 
                 
        if agreement.subproperty.building_id.building_address.street:
            street = agreement.subproperty.building_id.building_address.street
        else:
            street = '' 
             
        if agreement.subproperty.building_id.building_address.street2:
            street2 = agreement.subproperty.building_id.building_address.street2
        else:
            street2 = ''
         
        if agreement.subproperty.building_id.building_address.city:
            city = agreement.subproperty.building_id.building_address.city
        else:
            city = ''
             
        if agreement.subproperty.building_id.building_address.country_id:
            country = agreement.subproperty.building_id.building_address.country_id.name
        else:
            country = ''
         
        f_date = self.start_date
        t_date = agreement.agreement_start_date + relativedelta(months=1)- timedelta(days=1)        
        from_date = datetime.strptime(str(f_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',       
        to_date = datetime.strptime(str(t_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',  
        end_date = datetime.strptime(str(agreement.agreement_end_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',       
        start_date = datetime.strptime(str(agreement.agreement_start_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',  
        lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
        date_format = lang_id.date_format
        formatted_start_date = datetime.strptime(str(f_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        formatted_end_date = datetime.strptime(str(agreement.agreement_end_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        
        tax_ids = params.get_param('zb_building_management.default_expense_tax_ids') or False,
        if tax_ids[0]:
            temp = re.findall(r'\d+', tax_ids[0]) 
            tax_list = list(map(int, temp))  
            
        invoice_starting_date = params.get_param('zb_bf_custom.invoice_start_date')
        if not invoice_starting_date:
            raise Warning(_('Please Configure Invoice Start Date'))
        invoice_startdate = datetime.strptime(invoice_starting_date, '%Y-%m-%d').date()
             
        commission=agreement.agent_commission_amount
        total_days = (datetime.strptime(str(agreement.agreement_end_date), '%Y-%m-%d')-datetime.strptime(str(agreement.agreement_start_date), '%Y-%m-%d')).days + 1
        ownr_commission = agreement.commission_percent_amount
                
         
        currnet_user = self.env['res.users'].browse(self._uid)
        company_id = currnet_user.company_id   
        
        contra_liability_account_id = params.get_param('zb_bf_custom.contra_liability_account_id') or False
        if not contra_liability_account_id:
            raise Warning(_('Please Configure Account'))
        
        deposit_liability_account_id = params.get_param('zb_bf_custom.deposit_liability_account_id') or False
        if not deposit_liability_account_id:
            raise Warning(_('Please Configure Deposit Account'))
        
        commission_journal_id = params.get_param('zb_bf_custom.commission_journal_id') or False
        if not commission_journal_id:
            raise Warning(_('Please Configure Commission Journal'))
        
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        if not rent_invoice_journal_id:
            raise Warning(_('Please Configure Rent Invoice Journal'))
        
        
        commission_product_id = params.get_param('zb_bf_custom.commission_product_id') or False
        if not commission_product_id:
            raise Warning(_('Please Configure Commission Product'))
        
        
        rent_invoice_product_id = params.get_param('zb_bf_custom.rent_invoice_product_id') or False
        if not rent_invoice_product_id:
            raise Warning(_('Please Configure Rent Invoice Product'))
        
        vendor_bill_journal_id = params.get_param('zb_bf_custom.agent_journal_id') or False
        if not vendor_bill_journal_id:
            raise Warning(_('Please Configure Agent Commission journal'))
        
        rent_commission_expense_acccount_id = params.get_param('zb_bf_custom.rent_commission_expense_acccount_id') or False
        if not rent_commission_expense_acccount_id:
            raise Warning(_('Please Configure Rent Commission Expense Account'))
        
        rent_commission_payable_acccount_id = params.get_param('zb_bf_custom.rent_commission_payable_acccount_id') or False
        if not rent_commission_payable_acccount_id:
            raise Warning(_('Please Configure Rent Commission Payable Account'))
        
        
        accruded_journal_id = params.get_param('zb_bf_custom.accruded_journal_id') or False
        if not accruded_journal_id:
            raise Warning(_('Please Configure Accruded Journal'))
        
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
        
        if agreement.subproperty.flat_on_offer == True:
            owner_id = config_owner_id
        else:
            owner_id = agreement.subproperty.owner_id
        
        
        product = self.env['product.product'].browse(int(commission_product_id))
        
        rent_cmsn_payable_val =  {
                        'product_id':int(commission_product_id),
                        'account_id':int(rent_commission_payable_acccount_id),
                        'analytic_account_id':analytic,
                        'partner_id': agreement.agent.id,
                        'debit':0,
                        'credit':commission,
                         }
                     
        rent_cmsn_expense_val = {
                    'product_id':int(commission_product_id),
                    'account_id': int(rent_commission_expense_acccount_id),
                    'analytic_account_id':analytic,
                    'partner_id': agreement.agent.id,
                    'debit':commission,
                    'credit':0,
                     }
        agent_vals = {
                'invoice_payment_term_id':agreement.agent.property_supplier_payment_term_id.id if agreement.agent.property_supplier_payment_term_id else '',
                'partner_id': agreement.agent.id,
#DB                 'type': 'in_invoice',
                'type': 'entry',
                'from_date' : agreement.agreement_start_date,
                'to_date' : agreement.agreement_end_date,
                'comment': company_id.agent_commission_comment,
                'module_id': agreement.subproperty.id,
                'building_id':agreement.subproperty.building_id and agreement.subproperty.building_id.id,
                'lease_id':agreement.id,
                'journal_id':int(accruded_journal_id),
                'line_ids':[(0, 0,rent_cmsn_expense_val),
                            (0, 0,rent_cmsn_payable_val)
                            ],
               
                }
        
        tenant_vals = {
            'building_id':agreement.building_id,
            'module_id':agreement.subproperty,
            'monthly_rent':agreement.monthly_rent,
            'lease_start_date':agreement.agreement_start_date,
            'lease_end_date':agreement.agreement_end_date
            }
        
        product = self.env['product.product'].browse(int(rent_invoice_product_id))
        
        agreemnt_from_date = agreement.agreement_start_date
        agreemnt_to_date = agreement.agreement_end_date
        from_date = agreemnt_from_date
        to_date = from_date
        day = from_date.day
        strt_date = self.start_date
        

        #Rent Invoice generation to Tenant         
        inv_to_date_format = ''
        start_date_format = ''
        inv_to_date = self.get_to_date(agreemnt_from_date, agreement.advance_pay_mnth)
        if inv_to_date:
            inv_to_date_format = datetime.strptime(str(inv_to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            # datetime.strptime(str(inv_to_date), '%Y-%m-%d').strftime('%d/%m/%Y') 
        if self.start_date: 
            start_date_format = datetime.strptime(str(self.start_date), '%Y-%m-%d').strftime('%d/%m/%Y')  
        rent_vals = {
                'partner_id': agreement.tenant_id.id,
                'type': 'out_invoice',
                'invoice_date':self.start_date,
                'from_date' : self.start_date,
                'to_date' : inv_to_date,
                'journal_id':int(rent_invoice_journal_id),
                'module_id': agreement.subproperty.id,
                'building_id':agreement.subproperty.building_id and agreement.subproperty.building_id.id,
                'lease_id':agreement.id,
                'invoice_line_ids': [(0, 0, {
                                            'product_id':int(rent_invoice_product_id),
                                            'name': 'Rent for the Period from %s to %s'%(formatted_start_date,inv_to_date_format),
                                            'price_unit' : self.invoice_amount,
                                            'quantity': 1,
                                            'tax_ids' : product.taxes_id.ids,
                                            'analytic_account_id':analytic,
                                            'account_id': product.property_account_income_id and product.property_account_income_id.id or acct_id,
                                             })],
               
                }
        
        #invoice plan updation based on advance payment month-Neha
        
        inv_list = []
        invoice_plan_dict = {}
        amount = self.invoice_amount
        from_date = to_date
        to_date = from_date + relativedelta(months=agreement.advance_pay_mnth)
        end_date = agreemnt_to_date + relativedelta(days=1)
        while to_date <= end_date:
            if from_date >= invoice_startdate:
                if not agreement.invoice_plan_ids.filtered(lambda r: r.inv_date == from_date):
                    
                    if day <= monthrange(from_date.year,from_date.month)[1]:
                        from_date = from_date.replace(day = day)
                    else:
                        last_day = from_date.replace(day = monthrange(from_date.year,from_date.month)[1])
                        from_date = from_date.replace(day = last_day.day)
                    
                    vals = {
                            'inv_date':from_date,
                            'amount':amount ,
                           }
                    inv_list.append((0,0,vals))
                
            strt_date = to_date + relativedelta(days=1)
            no_of_mnths = self.get_months(agreemnt_to_date,to_date)
            if (no_of_mnths < agreement.invoice_cycle_num and no_of_mnths != 0):
                from_date = to_date
                to_date = from_date + relativedelta(months=no_of_mnths)  
                amount = agreement.monthly_rent*no_of_mnths 
            elif no_of_mnths >= agreement.invoice_cycle_num:
                from_date = to_date
                to_date = from_date + relativedelta(months=agreement.invoice_cycle_num) 
                amount = agreement.monthly_rent*agreement.invoice_cycle_num
            else:
                break
        agreement.write({'invoice_plan_ids': inv_list}) 
        
        deposit_product_id = params.get_param('zb_bf_custom.deposit_product_id') or False
        deposit_journal_id = params.get_param('zb_bf_custom.deposit_journal_id') or False
        
        # agr_end_date = datetime.strptime(str(agreement.agreement_end_date), '%Y-%m-%d').strftime('%d-%m-%Y') or ''
        if agreement.security_deposit:
            if not deposit_product_id:
                raise Warning(_('Please Configure Deposit Product'))
            if not deposit_journal_id:
                raise Warning(_('Please Configure Deposit Journal'))
            
            product = self.env['product.product'].browse(int(deposit_product_id))
            
            #Tenant Deposit Invoice vals
            receipt_vals = {
                'partner_id': agreement.tenant_id.id,
                'type': 'out_invoice',
                'invoice_date':self.start_date,
                'from_date' : f_date,
                'to_date' : agreement.agreement_end_date,
                'module_id': agreement.subproperty.id,
                'building_id':agreement.subproperty.building_id and agreement.subproperty.building_id.id,
                'lease_id':agreement.id,
                'journal_id':int(deposit_journal_id),
                'deposit_jv_desc':'{},{},{},{},{},{}, Deposit Journal:{}  to {}, Tenant:{}'.format(agreement.building_id.name,agreement.subproperty.name,street,street2,city,country,formatted_start_date,formatted_end_date,agreement.tenant_id.name),
                'invoice_line_ids': [(0, 0, {
                                            'product_id':int(deposit_product_id),
                                            'name':'Tenant Deposit For the Period %s - %s'%(formatted_start_date,formatted_end_date),
                                            'account_id':product.property_account_income_id.id,
                                            'analytic_account_id':analytic,
                                            'partner_id':agreement.tenant_id.id,
                                            'tax_ids' : product.taxes_id.ids,
                                            'price_unit':agreement.security_deposit
                                             })],
                }
#         if not agreement.building_id.account_id:
#             raise Warning(_('Please Configure Income Account in Building'))
        
        if agreement.owner_id:
            pass
        elif agreement.subproperty.owner_id:
            pass
        elif params.get_param('zb_bf_custom.owner_id'):
            pass
        else:
            raise Warning(_('Please Configure Owner'))
         
        inv_id = False
        if agreement.tenant_id:
            tenant_ids = self.env['res.partner'].search([('id','=',agreement.tenant_id.id)])
            tenant_ids.update(tenant_vals)
            if self.start_date >= invoice_startdate:
                inv_id = self.env['account.move'].sudo().create(rent_vals)
                agreement.rent_invoice_id = inv_id.id
#             for line in inv_id.line_ids:
#                 if line.credit > 0.000:
# #                     line.partner_id = agreement.subproperty.owner_id.id
#                     line.account_id = int(contra_liability_account_id)
                inv_id.action_post()
            debit_val =  {
                        'account_id':int(contra_liability_account_id),
                        'analytic_account_id':analytic,
                        'partner_id':int(owner_id),
                        'debit':self.invoice_amount,
                        'credit':0.000,
                         }
            credit_val = {
                        'account_id': int(building_income_account_id),
                        'analytic_account_id':analytic,
#                         'partner_id':agreement.tenant_id.id,
                        'debit':0.000,
                        'credit':self.invoice_amount,
                         }
            
            product = self.env['product.product'].browse(int(commission_product_id))
            
            #Commision Invoice vals
            if agreement.subproperty.owner_id:
                partner_id = agreement.subproperty.owner_id.id
            else:
                partnerrr_id=params.get_param('zb_bf_custom.owner_id') or False,
                partner_id = self.env['res.partner'].browse(int(partnerrr_id[0]))
            commission_jv_vals = {
                        'partner_id': int(owner_id),
                        'type': 'out_invoice',
                        'invoice_date':self.start_date,
                        'from_date' : f_date,
                        'to_date' : agreement.agreement_end_date,
                        'module_id': agreement.subproperty.id,
                        'building_id':agreement.subproperty.building_id and agreement.subproperty.building_id.id,
                        'lease_id':agreement.id,
                        'journal_id':int(commission_journal_id),
                        'invoice_line_ids': [(0, 0, {
                                            'product_id':int(commission_product_id),
                                            'name': 'Commission for  {},{},for the period {} to {}'.format(agreement.subproperty.name,agreement.building_id.name,formatted_start_date,formatted_end_date)+'\n'+ 'Tenant:{}'.format(agreement.tenant_id.name),
                                            'price_unit': ownr_commission,
                                            'quantity': 1,
                                            'tax_ids' : product.taxes_id.ids,
                                            'analytic_account_id':analytic,
                                            'account_id': int(contra_liability_account_id),
                                             })]
                        }
            
            
        #     'name': '{},{},{},{},{},{}, Commission Journal:{}  to {}, Tenant:{}'.format(agreement.building_id.name,agreement.subproperty.name,street,street2,city,country,start_date[0],agr_end_date,agreement.tenant_id.name),
            
            if ownr_commission != 0:
                if self.start_date >= invoice_startdate:
                    commission_move_id = self.env['account.move'].sudo().create(commission_jv_vals)
                    # Commented based on ZB-6440-Configuration for commission account
                    # for line in commission_move_id.line_ids:
                    #     if line.credit > 0.000:
                    #         # line.partner_id = company_id.partner_id.id - as per 6351-Neha
                    #         line.account_id = int(building_income_account_id), 
                    agreement.commission_move_id = commission_move_id.id
                    move = commission_move_id.action_post()
            
            # invoice amount passed to invoice plan line-Neha
            for line in agreement.invoice_plan_ids:
                if inv_id:
                    if self.start_date < agreement.agreement_start_date:
                        if line.inv_date == agreement.agreement_start_date:
                            line.update({'move_id': inv_id.id,
                                         })
                    else:
                        if line.inv_date == inv_id.from_date:
                            line.update({'move_id': inv_id.id,
                                         })
                        else:
                            if not agreement.managed:    
                                line.unlink()
                
                
            if agreement.security_deposit:
                if self.start_date >= invoice_startdate:
                    receipt_id = self.env['account.move'].sudo().create(receipt_vals)
    #DB                 for line in receipt_id.line_ids:
    #                     if line.credit > 0.000:
    #                         line.partner_id = company_id.partner_id.id
    #                         line.account_id = int(deposit_liability_account_id)
                    
                    receipt_id.action_post()
                    agreement.voucher_move_id = receipt_id.id
        if agreement.agent and agreement.agent_commission_amount:
            if self.start_date >= invoice_startdate:
                invoice_id = self.env['account.move'].sudo().create(agent_vals)
                invoice_id.action_post()
                agreement.vendor_id = invoice_id.id
            
        '''
         =========== Fixed Service Invoice generation==============.
        '''
        service_journal_id=params.get_param('zb_bf_custom.service_invoice_journal_id') or False, 
        if not service_journal_id:
            raise UserError(_('Please Configure a Service Invoice Journal'))
        fixed_services = agreement.services_ids.filtered(lambda r: r.bill == 'fixed')
        if agreement.subproperty.owner_id:
            partner_id = agreement.subproperty.owner_id.id
        else:
            partnerrr_id=params.get_param('zb_bf_custom.owner_id') or False,
            partner_id = self.env['res.partner'].browse(int(partnerrr_id[0]))
        service_list = []
        for service in fixed_services:
                service_list.append(({
                                    'product_id':service.product_id.id,
                                    'name': '{},Fixed services for {},{}'.format(service.product_id.name,agreement.building_id.name,agreement.subproperty.name),
                                    'price_unit': service.owner_share,
                                    'quantity': 1,
                                    'tax_ids' : service.product_id.taxes_id.ids,
                                    'analytic_account_id':analytic,
                                    'account_id':service.product_id.property_account_income_id.id,
                                     }))
        if fixed_services:
            service_inv_vals = {
                          'partner_id': int(owner_id),
                          'type': 'out_invoice',
                          'invoice_date': self.start_date,
                          'building_id': agreement.subproperty.building_id and agreement.subproperty.building_id.id,
                          'module_id': agreement.subproperty.id,
                          'lease_id':agreement.id,
                          'journal_id':int(service_journal_id[0]),
                          'invoice_line_ids':[],
                        }
            service_inv_vals.update({'invoice_line_ids':service_list, })
            if agreement.managed:
                if self.start_date >= invoice_startdate:
                    service_invoice_id = self.env.get('account.move').sudo().create(service_inv_vals)
                    service_invoice_id.action_post()
        '''
         ===========Advance rent calculation and invoice generation==============.
        '''
        if not self.advance_payment_mnth:
            raise Warning(_("""Advance payment month should be more than 1"""))
        
        
        # Assign moving date in wizard to form 
        
        agreement.moving_date = self.start_date
#         agreement.commission_generated = True
        if agreement.crm_lead_id:
            stage = self.env['crm.stage'].search([('is_won','=',True)])
            agreement.crm_lead_id.action_set_won()
            agreement.crm_lead_id.stage_id = stage.id
            
    
    start_date = fields.Date("From Date",default=get_date)
    invoice_amount = fields.Float('Invoice Amount',digits = (12,3))
    deposit_amount = fields.Float("Deposit Amount",digits = (12,3))
    advance_payment_mnth = fields.Integer("Advance Payment Month",default=1)
    advance_payment_cycle = fields.Integer('Advance Payment',default=1)

             
                
