
from odoo import api, fields, models,_
from datetime import date,datetime,timedelta 
from odoo.exceptions import UserError,Warning,ValidationError
import json

class Lead(models.Model):
    _inherit = "crm.lead"
    _description = "CRM Lead"
    
    
    def _default_store_probability(self):
        stage_id = self._default_stage_id()
        if stage_id:
            return self.env['crm.stage'].browse(stage_id).probability
        return 10
    
    cust_satisfaction = fields.Selection(
        [
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
        ('4', 'Excellent'),
        ('5', 'Outstanding'),
        ], 'Customer Satisfaction', index=True)
    process = fields.Selection(
        [
        ('sale', 'Sale'),
        ('resale', 'Resale'),
        ('rental', 'Rental Activity'),
        ], 'Process')
    action = fields.Selection([
        ('existing', 'Existing Client'),
        ('new', 'New Client')
    ], 'Action', required=True)
    client_name = fields.Char('Client Name', track_visibility='onchange',)
    client_id = fields.Many2one('res.partner','Client Name')
    module_id = fields.Many2one('zbbm.module','Flat/Module')
    agreement_count = fields.Integer(compute='_compute_agreement_count',string='Lease Agreements')
    reserve_expired = fields.Boolean('Reservation Expired',default=False)
    book_expired = fields.Boolean('Booking Expired',default=False)
    store_prob = fields.Float('probabilitystore', group_operator="avg",readonly=True,default=lambda self: self._default_store_probability())
    building_ids = fields.Many2many('zbbm.building',compute="_compute_building_id_domain",readonly=True)
    
    
    # @api.model
    # def create(self, vals):
    #     print('============================vals',vals,self._context)
    #     if 'process' in vals and vals['process'] in ['resale','sale']:
    #         if 'partner_id' in vals:
    #             partner_id = self.env['res.partner'].browse(vals['partner_id'])
    #             if not partner_id.cpr and not partner_id.passport:
    #                 raise Warning(_("""Passport or CPR is mandatory for the Customer"""))
    #     return super(Lead, self).create(vals)
    
    def view_agreements(self):
        
        agreements = self.env['zbbm.module.lease.rent.agreement'].search([('crm_lead_id','=',self.id)])
        action = self.env.ref('zb_building_management.action_zbbm_module_lease_rent_view').read()[0]
        if len(agreements) > 1:
            action['domain'] = [('id', 'in', agreements.ids)]
        elif len(agreements) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_lease_rent_agreement_form').id, 'form')]
            action['res_id'] = agreements.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    @api.onchange('stage_id')
    def onchage_stage_id(self):
        if self._context.get('booked')!= 'make_open' and self.stage_id.probability == 50.00:
            if self._origin.stage_id.probability > self.stage_id.probability:
                raise ValidationError("No, you can cancel only")
            self._origin.set_member_color()
              
        if self._context.get('booked')!= 'make_open' and self.stage_id.probability == 100.00:
            if self._origin.stage_id.probability > self.stage_id.probability:
                raise ValidationError("No, Contract Already Closed")
            self._origin.action_set_won()
              
        if self._context.get('booked')!= 'make_open' and self.stage_id.probability == 70.00:
            if self._origin.stage_id.probability > self.stage_id.probability:
                raise ValidationError("No, you can cancel only")
            self._origin.make_open()  
            
        if self._context.get('booked')!= 'make_open' and self.stage_id.probability == 15.00:
            if self._origin.stage_id.probability > self.stage_id.probability:
                raise ValidationError("No, you can cancel only")
            self._origin.call_stage()
            
        if self._context.get('booked')!= 'make_open' and self.stage_id.probability == 20.00:
            if self._origin.stage_id.probability > self.stage_id.probability:
                raise ValidationError("No, you can cancel only")
            self._origin.followup_stage()  
              
        if self._context.get('booked')!= 'make_open' and self.stage_id.probability not in [70.00,50.00,15.00,20.00,10.00,100.00,0.00]:
            raise ValidationError("You can't perform that move !.")
        
        if self._context.get('booked')!= 'make_open' or self._context.get('booked')!= 'None':
            if self.stage_id.probability in [70.00]:
                raise ValidationError("You can't perform that move !.")
           
        # if self.stage_id.probability == 10.00:
        #    raise ValidationError("You can't perform that move!.")
        if self.stage_id.probability == 15:
            stage_fields= []
            if self.stage_id.field_ids:
                for items in self.env['crm.stage'].search([('probability','=',15)]).field_ids:
                    stage_fields.append(items.name)
                  
                self.env.cr.execute("""select * from crm_lead where id=%s""",(self._origin.id,))
                lead_list = [i for i in self.env.cr.dictfetchall()]
                for stage_field in stage_fields:
                    if not lead_list[0].get('%s'%(stage_field)):
                        raise Warning(_('Please provide %s'%(self._fields[stage_field].string)))
        if self.stage_id.probability == 20:
            stage_fields= []
            if self.stage_id.field_ids:
                for items in self.env['crm.stage'].search([('probability','=',20)]).field_ids:
                     
                    stage_fields.append(items.name)
                  
                self.env.cr.execute("""select * from crm_lead where id=%s""",(self._origin.id,))
                lead_list = [i for i in self.env.cr.dictfetchall()]
                for stage_field in stage_fields:
                    if not lead_list[0].get('%s'%(stage_field)):
                        raise Warning(_('Please provide %s'%(self._fields[stage_field].string)))           
          
          
        if self._origin.stage_id.probability == 70.00:
            if self._origin.stage_id.probability > self.stage_id.probability:
                raise ValidationError("No, you can cancel only")
        if self._origin.stage_id.probability in [50.00,49.00]:
            if self._origin.stage_id.probability > self.stage_id.probability:
                raise ValidationError("You can't perform that move !.")    
              
        if self._origin.stage_id.probability == 100.00:
            if self._origin.stage_id.probability != self.stage_id.probability:
                raise ValidationError("Contract Already Closed")
              
              
        if self._origin.stage_id.probability == 90.00:
            if self._origin.stage_id.probability > self.stage_id.probability:
                raise ValidationError("Contract Already Signed")  
    
    def toggle_active(self):
        res = super(Lead, self).toggle_active()
        self.probability = self.stage_id.probability
        return res
    
    
    def _compute_agreement_count(self):
        for order in self:
            agreement_ids = self.env['zbbm.module.lease.rent.agreement'].search([('crm_lead_id','=',self.id)])
            order.agreement_count = len(agreement_ids) 
    
    def create_lease_agreement(self):
#         partner_id = ''
#         if self.action == 'existing':
#             partner_id = self.client_id.id
#         elif self.action == 'new':
#             partner_id = self._create_lead_partner()
#             self.action = 'existing'
#             self.client_id = partner_id
        form_view_id = self.env.ref('zb_building_management.view_lease_rent_agreement_form').id 
        if not self.partner_id:
            raise Warning(_('Please Select Customer'))
        return{
                        'name':'Lease Agreement form View',
                        'type': 'ir.actions.act_window',
                        'views': [(form_view_id, 'form')],
                        'res_model': 'zbbm.module.lease.rent.agreement',
                        'view_mode': 'form',
                        'context' : {'default_building_id' : self.building_id.id,
                                    'default_subproperty' : self.module_id.id,
                                    'default_crm_lead_id' : self.id,
                                    'default_tenant_id' : self.partner_id.id,
                                    'default_campaign_id' : self.campaign_id.id,
                                    'default_source_id' : self.source_id.id,
                                    },
                        }
        
    @api.depends('process')
    def _compute_building_id_domain(self):
        building_list = []
        for order in self:
            sellable = self.env['zbbm.building'].search([('building_type','in',['sell','both'])])
            leasable = self.env['zbbm.building'].search([('building_type','in',['rent','both'])])
            if self.process in ['sale','resale']:
                for building in sellable:
                    building_list.append(building.id)
            else:
                for building in leasable:
                    building_list.append(building.id)
            order.building_ids = [(6,0,building_list)]
    
    
    def set_member_color(self):
        res = super(Lead, self).set_member_color()
        if self.reserve_expired == True:
            if not self.user_has_groups('zb_bf_custom.group_crm_manager'):
                raise Warning(_('Only manager is allowed to re-reserve'))
        for record in self:
            if self.process in ['rental']:
                if not record.module_id:
                    raise Warning(_("""Please configure Module """))
                buid = self.env['zbbm.module'].browse(self.module_id.id)
                if buid:
                    if buid.state=='reserve':
                        if self._context.get('booked')!= 'make_open':
                            raise Warning(_('Unit already reserved by  %s'%buid.tenant_id.name))
                        stage = self.env['crm.stage'].search([('probability','=',49)])
                        if stage:
                            if buid.tenant_id:
                                msg ='Reserved by: %s on %s'%(buid.tenant_id.name,buid.reservation_date)
                            else:
                                msg ='Reserved by: %s on %s'%(buid.user_id.name,buid.reservation_date)
                            record.store_prob = record.stage_id.probability
                            record.stage_id = stage.id
                            record.msg = msg
                            record.probability = stage.probability
                    else:
                        buid.sudo().write({'state':'reserve',
                                    'reservation_date':date.today(),
                                    'user_id':self.user_id.id,
                                    })
                         
                        stage = self.env['crm.stage'].search([('probability','=',50)])
                        if stage:
                            record.stage_id = stage.id
                            record.probability = stage.probability
        return res
    
    def set_unreserve_color(self):
        for record in self:
            res = super(Lead, self).set_unreserve_color()
            self.action_set_lost()
#                 buid = self.env['zbbm.module'].browse(self.module_id.id)
#                 if buid:
#                     buid.write({'state':'new',
#                                  'reservation_date':False,
#                                  'reservation_time':5})
#                      
#                     stage = self.env['crm.stage'].search([('probability','=',record.store_prob)])
#                     if stage:
#                         record.stage_id = stage.id
#                         record.probability = stage.probability
#                         record.store_prob = stage.probability
            mail_pool = self.env['mail.mail']
            email_template_obj = self.env['mail.template']
            mailmess_pool = self.env['mail.message']
            mail_date = datetime.now()
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference('zb_crm_property', 'email_template_session_mail5_crm')[1]
            except ValueError:
                template_id = False
            if template_id:
                mail_template_obj = self.env['mail.template'].browse(template_id)
                body_html = self.env['mail.template']._render_template(mail_template_obj.body_html, 'crm.lead', record.id)    
                mail_values = {
#                             'name': mail_template_obj.name,
                    'subject': 'Reservation expiry  - Reminder ',
#                             'model_id':record.id,
                    'email_to': self.user_id.partner_id.email,
                    'scheduled_date':(datetime.now() + timedelta(hours=1,minutes=30)),
                    'body_html': body_html,
                    'notification': True,
                }
                mail = self.env['mail.mail'].create(mail_values)
            else:
                raise Warning(_('Please provide Assigned user/Email'))
        return super(Lead, self).set_unreserve_color()

    
    def create_resale_invoices_(self):
        params = self.env['ir.config_parameter'].sudo() 
        resale_commission_journal_id = params.get_param('zb_bf_custom.resale_commission_journal_id') or False
        resale_commission_product_id = params.get_param('zb_bf_custom.resale_commission_product_id') or False
        resale_vendor_journal_id = params.get_param('zb_bf_custom.resale_vendor_journal_id') or False
        if not resale_commission_journal_id:
            raise Warning(_('Please Configure Resale Commisiion Journal'))
        
        if not resale_commission_product_id:
            raise Warning(_('Please Configure Resale Commisiion Product'))
        
        if not resale_vendor_journal_id:
            raise Warning(_('Please Configure Resale Vendor Journal'))
        
        product = self.env['product.product'].browse(int(resale_commission_product_id))
    
        for items in self:
            unit_ids = self.env.get('zbbm.unit').search([('id','=',items.unit_id.id),('building_id','=',items.building_id.id)])
            if unit_ids:
                if self.unit_id.instlm_total == self.unit_id.price or self.unit_id.invoice_total == self.unit_id.price and self.unit_id.price != 0:
                    owner_description = 'Resale Commission for the Owner '+ str(unit_ids.owner_id.name) if unit_ids.owner_id else ''
                    buyer_description = 'Resale Commission for the Buyer '+ str(items.partner_id.name) if unit_ids.buyer_id else ''
                    
                    invoice_owner_commsn = {
                        'partner_id':unit_ids.owner_id.id,
                        'type': 'out_invoice',
                        'invoice_date': datetime.today(),
                        'from_date':datetime.today(),
                        'to_date':datetime.today(),
                        'building_id': items.building_id.id,
                        'unit_id':items.unit_id.id,
                        'comment': owner_description,
                        'journal_id':int(resale_commission_journal_id),
                        'invoice_line_ids': [(0, 0, {
                                            'product_id':int(resale_commission_product_id),
                                            'name': owner_description,
                                            'price_unit': unit_ids.resale_owner_commission,
                                            'tax_ids' : product.taxes_id.ids,
                                            'quantity': 1,
                                            'account_analytic_id':items.building_id.analytic_account_id.id if items.building_id.analytic_account_id else '',
                                            'account_id':product.property_account_income_id.id,
                                            })],
                        }
                    if unit_ids.resale_owner_commission > 0:
                        resale_owner_commission_inv_id = self.env['account.move'].create(invoice_owner_commsn)
                        resale_owner_commission_inv_id.action_post()
    #                     items.resale_move_id = resale_commission_inv_id.id
                    
                    
                    invoice_buyer_commsn = {
                            'partner_id': items.partner_id.id,
                            'type': 'out_invoice',
                            'invoice_date':datetime.today(),
                            'from_date':datetime.today(),
                            'to_date':datetime.today(),
                            'unit_id':items.unit_id.id,
                            'building_id':items.building_id.id,
                            'comment': buyer_description,
                            'journal_id':int(resale_commission_journal_id),
                            'invoice_line_ids': [(0, 0, {
                                            'product_id':int(resale_commission_product_id),
                                            'name': buyer_description,
                                            'price_unit': unit_ids.resale_buyer_commission,
                                            'tax_ids' : product.taxes_id.ids,
                                            'quantity': 1,
                                            'account_analytic_id':items.building_id.analytic_account_id.id if items.building_id.analytic_account_id else '',
                                            'account_id':product.property_account_income_id.id,
                                            })],
                            }
                    if unit_ids.resale_buyer_commission > 0:
                        resale_buyer_commission_inv_id = self.env['account.move'].create(invoice_buyer_commsn)
                        resale_buyer_commission_inv_id.action_post()
                    
                    if unit_ids.unit_agent_id:
                        agent_description = 'Resale Commission for the Agent '+ str(unit_ids.unit_agent_id.name) if unit_ids.unit_agent_id else ''
            
                        invoice_agent_commsn = {
                            'partner_id': unit_ids.unit_agent_id.id,
                            'type': 'in_invoice',
                            'invoice_date':datetime.today(),
                            'from_date':datetime.today(),
                            'to_date':datetime.today(),
                            'unit_id':items.unit_id.id,
                            'building_id':items.building_id.id,
                            'comment': agent_description,
                            'journal_id':int(resale_vendor_journal_id),
                            'invoice_line_ids': [(0, 0, {
                                            'product_id':int(resale_commission_product_id),
                                            'name': agent_description,
                                            'price_unit': unit_ids.resale_agent_commission,
                                            'tax_ids' : product.taxes_id.ids,
                                            'quantity': 1,
                                            'account_analytic_id':items.building_id.analytic_account_id.id if items.building_id.analytic_account_id else '',
                                            'account_id':product.property_account_income_id.id,
                                            })],
                            }
                        if unit_ids.resale_agent_commission > 0:
                            resale_agent_commission_inv_id = self.env['account.move'].create(invoice_agent_commsn)
                            resale_agent_commission_inv_id.action_post()
    
    
    def make_open(self):
        stage_fields = []

        if self.stage_id.field_ids:
            for items in self.env['crm.stage'].search([('probability','=',70)]).field_ids:
                stage_fields.append(items.name)
            self.env.cr.execute("""select * from crm_lead where id=%s""",(self.id,))
            lead_list = [i for i in self.env.cr.dictfetchall()]
            for stage_field in stage_fields:
                if not lead_list[0].get('%s'%(stage_field)):
                    raise Warning(_('Please provide %s'%(self._fields[stage_field].string)))
        l = []
        if not self.building_id:
            raise Warning(_("""Please configure Building """))
        
        if self.process in ['rental']:
            if self.partner_id.company_type == 'person':
                if not self.partner_id.cpr and not self.partner_id.passport:
                    raise Warning(_("""Passport or CPR is mandatory for the Customer"""))
        
        if self.book_expired == True:
            if not self.user_has_groups('zb_bf_custom.group_crm_manager'):
                raise Warning(_('Only manager is allowed to re-book'))
        
        if self.process in ['sale','resale']:
            if not self.unit_id:
                raise Warning(_("""Please configure Unit """))
            
            if not self.partner_id:
                raise Warning(_('Please Select Customer'))
            
            if self.unit_id.booking_fee_payment == 'installment':
                if self.unit_id.instlm_total != self.unit_id.price or self.unit_id.price == 0:
                    view_id = self.env.ref('zb_crm_property.'
                                       'view_open-unit_wizard')
                    return {
                        'name':'Payment Schedule is  not Configured',
                        'type': 'ir.actions.act_window',
                        'res_model': 'unit.unit.wizard',
                        'view_mode': 'form',
                        'view_id': view_id.id or False,
                        'views': [(False, 'form')],
                        'target': 'new',
                    }
                if not self.unit_id.booking_per:
                    raise Warning(_("Booking fee and Payment plan and hasn't been configured on the unit"))
            
            elif self.unit_id.invoice_total < self.unit_id.price or self.unit_id.price == 0:
                view_id = self.env.ref('zb_crm_property.'
                                   'view_open-unit_wizard')
                return {
                    'name':'Payment Schedule is  not Configured',
                    'type': 'ir.actions.act_window',
                    'res_model': 'unit.unit.wizard',
                    'view_mode': 'form',
                    'view_id': view_id.id or False,
                    'views': [(False, 'form')],
                    'target': 'new',
                }
            
            similar = self.search([('unit_id','=',self.unit_id.id),('id','!=',self.id),('process','in',['sale','resale']),('probability','=',self.probability)])
            if similar:
                for sim in similar:
                    if self._context.get('booked')!= 'make_open': 
                        sim.write({'probability': 0, 'active': False})
                    else:
                        sim.action_set_lost()
            module_ids = self.env.get('zbbm.unit').search([('id','=',self.unit_id.id),('building_id','=',self.building_id.id)])
            stage_reserved = self.env['crm.stage'].search([('probability','=',50)])
            msg =''
            if module_ids:
                if module_ids.state=='reserved' and not self.stage_id == stage_reserved:
                    if self._context.get('booked')!= 'make_open':
                        raise Warning(_('Module already reserved by  %s'%module_ids.buyer_id.name))
                    stage = self.env['crm.stage'].search([('probability','=',49)])
                    if stage:
                        if module_ids.buyer_id:
                            msg ='Reserved by: %s on %s'%(module_ids.buyer_id.name,module_ids.buyer_id.reservation_date)
                        else:
                            msg ='Reserved by: %s on %s'%(module_ids.agent_id.name,module_ids.reservation_date)
                        self.store_prob = self.stage_id.probability
                        self.stage_id = stage.id
                        self.msg = msg
                        self.probability = stage.probability
            
                else:
                    for idss in module_ids:
                        l.append(idss.id)
                    if module_ids.state != 'book':
                        module_ids.sudo().write({'buyer_id':self.partner_id.id,
                                          'state':'book',
                                           'contract_date':datetime.today() })
                        self.create_resale_invoices_()
                    
                    journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                    if journal:
                        acct_id = journal[0].default_credit_account_id.id
             
                    module_ids.sudo().write({
                                      'agent_id':self.user_id.id,
                                      'lead_id':self.id,
                                      'reservation_time':0
                                      })
                    if  self._context.get('booked') == 'make_open':
                        module_ids.message_post(body=_(' {} booked  on {}').format(self.partner_id.name,datetime.today()))
                    if module_ids.buyer_id:
                            d = self.env['res.partner'].browse(module_ids.buyer_id.id)
                            d.write({'is_a_prospect':False,
                                          'customer':True,
                                           
                                           })
                    if not module_ids.buyer_id.passport and module_ids.buyer_id.cpr:
                        raise Warning(_('Please provide Passport and CPR '))
                    domain  = [('id', '=',module_ids.id)]
                    stage = self.env['crm.stage'].search([('probability','=',70),('name','=','Booked')])
                    stage2 = self.env['crm.stage'].search([('probability','=',70)])
                    if self.stage_id.id != stage.id:
                        if stage:
                            self.stage_id = stage.id
                            self.probability = stage.probability
                            self.store_prob = stage.probability
                    
                    if self._context.get('booked')!= 'make_open':
                        return self
                    if self._context.get('booked')== 'make_open':
                        return {
                            'name': _('Sale Unit'),
                            'view_id':False,
                            'view_mode': 'form',
                            'res_model': 'zbbm.unit',
                            'type': 'ir.actions.act_window',
                            'res_id': module_ids.id or False,
                    }

        # res = super(Lead, self).make_open()
        
        else:
            if not self.module_id:
                raise Warning(_("""Please configure Module """))
#             similar = self.search([('module_id','=',self.module_id.id),('id','!=',self.id)])
#             if similar:
#                 for sim in similar:
#                     if self._context.get('booked')!= 'make_open': 
#                         sim.write({'probability': 0, 'active': False})
#                     else:
#                         sim.action_set_lost()
            
            if self.partner_id:
                    d = self.env['res.partner'].browse(self.partner_id.id)
                    d.write({'is_tenant':True,
                                  'customer':True,
                                  'is_a_prospect':False,

                                   })
            if self._context.get('booked')!= 'make_open':
                return self
            
            created_lease = self.env['zbbm.module.lease.rent.agreement'].search([('subproperty','=',self.module_id.id),('state','in',['approval_waiting','approved'])])
            if created_lease:
                if self._context.get('booked') == 'make_open':
                    raise Warning(_('Module is in Approval Stage !!'))
            
            buid = self.env['zbbm.module'].browse(self.module_id.id)
            buid.sudo().booking_date = date.today()
            stage_reserved = self.env['crm.stage'].search([('probability','=',50)])
            if buid:
                if buid.state=='reserve' and not self.stage_id == stage_reserved:
                    if self._context.get('booked')!= 'make_open':
                        raise Warning(_('Module already reserved by  %s'%buid.tenant_id.name))
                    stage = self.env['crm.stage'].search([('probability','=',49)])
                    if stage:
                        if buid.tenant_id:
                            msg ='Reserved by: %s on %s'%(buid.tenant_id.name,buid.reservation_date)
                        else:
                            msg ='Reserved by: %s on %s'%(buid.user_id.name,buid.reservation_date)
                        self.store_prob = self.stage_id.probability
                        self.stage_id = stage.id
                        self.msg = msg
                        self.probability = stage.probability
                
                else:
                    return self.create_lease_agreement()
            
        # return res
    
    def action_set_lost(self,**additional_values):
        """ Lost semantic: probability = 0, active = False """
        if self.process in ['rental']:
            if self.module_id:
#                 new = self.env['zbbm.module'].browse(self.module_id.id)
#                 new.write({'state':'available',
#                     'tenant_id': False,
#                     'payments_ids':False,
#                     'receipt_ids':False,
#                     'invoice_total':False,
#                     'payment_total':False,
#                     'balance_total':False,
#                 })
#                 self.module_id.payment_total = False
#                 self.module_id.balance_total = False
#                 self.module_id.invoice_total = False
#                 self.module_id.tenant_id = False
#                 self.module_id.lead_id = False
                agreement_ids = self.env['zbbm.module.lease.rent.agreement'].search([('crm_lead_id','=',self.id)])
                
                for lease in agreement_ids:
                    if lease.state not in ['active']:
                        lease.state = 'terminate'
                    else:
                        raise Warning(_('Active lease cannot be terminate'))
                
                mail_pool = self.env['mail.mail']
                email_template_obj = self.env['mail.template']
                mailmess_pool = self.env['mail.message']
                mail_date = datetime.now()
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('zb_crm_property', 'email_template_session_mail6_crm')[1]
                except ValueError:
                    print("no_template")
                    template_id = False
                if template_id:
                    mail_template_obj = self.env['mail.template'].browse(template_id)
                    body_html = self.env['mail.template']._render_template(mail_template_obj.body_html, 'crm.lead', self.id)    
                    email_to = self.env['mail.template']._render_template(mail_template_obj.email_to, 'crm.lead', self.id)    
                    mail_values = {
    #                          'name': mail_template_obj.name,
                             'subject': 'Cancellation - Reminder ',
                             'id':self.id,
                             'email_to': email_to,
                             'scheduled_date':(datetime.now() + timedelta(hours=1,minutes=30)),
                             'body_html': body_html,
                             'notification': True,
                    }
                    mail = self.env['mail.mail'].create(mail_values)
                else:
                    raise Warning(_('Please provide Assigned user/Email'))
                self.module_id.sudo().write({'reservation_time':0})
            return self.write({'probability': 0, 'active': False})
        return super(Lead, self).action_set_lost(**additional_values)
    
    
    def reserve_extend(self):
        params = self.env['ir.config_parameter'].sudo()
        reservation_time = params.get_param('zb_building_management.reservation_time') or 0.0
        max_lease_reservation_time = params.get_param('zb_bf_custom.max_reservation_time_lease') or 0.0
        max_reservation_time = params.get_param('zb_building_management.max_reservation_time') or 0.0
        if self.process in ['rental']:
            if not self.module_id.reservation_time:
                self.module_id.reservation_time = reservation_time
            else:
                self.module_id.reservation_time = max_lease_reservation_time
        else:
            if not self.unit_id.reservation_time:
                self.unit_id.reservation_time = reservation_time
            else:
                self.unit_id.reservation_time = max_reservation_time
                
                
    def action_new_quotation(self):
        action = super().action_new_quotation()
        # Make the lead's Assigned Partner the quotation's Referrer.
        if self.building_id:
            action['context']['default_building_id'] = self.building_id.id
        if self.process in ['sale','resale']:
            if self.unit_id:
                action['context']['default_unit_id'] = self.unit_id.id
        else:
            if self.module_id:
                action['context']['default_module_id'] = self.module_id.id
        return action
                
        
    
    
    
    
    
    
    
    
    
    
    
    
    
