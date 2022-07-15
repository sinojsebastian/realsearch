from odoo import models, fields, api,exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools.translate import _
from datetime import datetime,date,timedelta
import pprint
from dateutil import relativedelta




# class PartnerBinding(models.TransientModel):
#     """
#         Handle the partner binding or generation in any CRM wizard that requires
#         such feature, like the lead2opportunity wizard, or the
#         phonecall2opportunity wizard.  Try to find a matching partner from the
#         CRM model's information (name, email, phone number, etc) or create a new
#         one on the fly.
#         Use it like a mixin with the wizard of your choice.
#     """
  
#     _inherit = 'crm.partner.binding'  
      
#     action = fields.Selection([
#         ('exist', 'Link to an existing customer'),
#         ('create', 'Create a new Prospect customer'),
#         ('nothing', 'Do not link to a customer')
#     ], 'Related Customer', required=True)

class Lead(models.Model):
    _inherit = "crm.lead"  
    _description = "Lead/Opportunity"
    
    def _default_probability(self):
        stage_id = self._default_stage_id()
        if stage_id:
            return self.env['crm.stage'].browse(stage_id).probability
        return 10

    def _default_stage_id(self):
        team = self.env['crm.team'].sudo()._get_default_team_id(user_id=self.env.uid)
        return self._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id
    
    dum_name= fields.Char('Representative Name')
    dum_phone = fields.Char('Representative Phone:')
    probability = fields.Float('Probability', group_operator="avg", default=lambda self: self._default_probability(),readonly=True)
    store_prob = fields.Float('probabilitystore', group_operator="avg",readonly=True)
    type1 = fields.Boolean(related='partner_id.is_a_prospect', string="nothing")
    reff_type = fields.Selection([('indi','Individual'),('bro','Broker')],string='Referral Type',default="indi")
    ref_phn = fields.Char('Phone No')
    ref_mail = fields.Char('Email')
    compni = fields.Char('Company')
    rep = fields.Boolean('Representative',default =False)
    building_id = fields.Many2one('zbbm.building', 'Building', 
                     domain=[('state','=','available')])
     
   #Commented by JEENA.latest feedback task 5650 ('building_type', 'in', ['sell','both'])
    
    unit_id = fields.Many2one('zbbm.unit', 'Building Units') 
    msg = fields.Text('Message')     
    nationality_id = fields.Many2one('res.country', string='Nationality')   
    mail_address = fields.Text('Mailing Address')
    isd = fields.Many2one('res.country','ISD')
    isd2 = fields.Many2one('res.country','ISD')

    @api.onchange('isd2')
    def on_change_phone(self):
        for all in self:
            if all.isd2 and all.mobile:
                if '(' in all.mobile:
                    all.mobile = '('+str(all.isd2.phone_code)+')'+all.mobile[(all.mobile.index(")")+1):]
            else:
                if all.isd2 and all.mobile:
                    all.mobile = '('+str(all.isd2.phone_code)+')'+all.mobile
                    
    @api.onchange('isd')
    def on_change_phone2(self):
        for all in self:
            if all.isd and all.phone:
                if '(' in all.phone:
                    all.phone = '('+str(all.isd.phone_code)+')'+all.phone[(all.phone.index(")")+1):]
                else:
                    all.phone = '('+str(all.isd.phone_code)+')'+all.phone

    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        partner = super(Lead, self)._create_lead_partner_data(
            name, is_company, parent_id=parent_id)
        partner.update({'is_a_prospect': True, 'customer': False,'nationality':self.nationality_id.id})
        return partner

    def _check_color(self):
        pp = pprint.PrettyPrinter(indent=4)
        res = {}
        for record in self:
            color = 0
            color= 1
            res[record.id] = color
        return res

    def action_set_lost(self,**additional_values):
        """ Lost semantic: probability = 0, active = False """
        if self.process in ['sale','resale']:
            if self.unit_id:
                new = self.env['zbbm.unit'].browse(self.unit_id.id)
                new.write({'state':'new',
                    'buyer_id': False,
                    'agent_id':False,
                    'payments_ids':False,
                    'invoice_total':False,
                    'payment_total':False,
                    'balance_total':False,
                    'balance_invoice':False,
                })
                self.unit_id.payment_total = False
                self.unit_id.las_date = False
                self.unit_id.balance_total = False
                self.unit_id.invoice_total = False
                self.unit_id.balance_invoice = False
                self.unit_id.buyer_id = False
                self.unit_id.lead_id = False
                self.unit_id.contract_date = False
                
                if self._context.get('booked')!= 'make_open':
                    for items in self.unit_id.installment_ids:
                        items.unlink()
                        items = False
                self.unit_id.message_post(body=_('{} cancelled booking').format(self.partner_id.name))   
                 
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
                #neha
                # self.unit_id.write({'reservation_time':0})
            return self.write({'probability': 0, 'active': False,'store_prob':0})
     
    def action_set_won(self):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            stage_fields =[]
            if lead.stage_id.field_ids:
                for items in self.env['crm.stage'].search([('probability','=',100)]).field_ids:
                    stage_fields.append(items.name)
                self.env.cr.execute("""select * from crm_lead where id=%s""",(lead.id,))
                lead_list = [i for i in self.env.cr.dictfetchall()]
                for stage_field in stage_fields:
                    if not lead_list[0].get('%s'%(stage_field)):
                        raise Warning(_('Please provide %s'%(self._fields[stage_field].string)))
            
            stage_id = lead._stage_find(domain=[('probability', '=', 100.0)])
#             ('on_change', '=', True)
            lead.write({'stage_id': stage_id.id, 'probability': 100,'store_prob':100})
            if lead.user_id and lead.team_id and lead.planned_revenue:
                query = """
                     SELECT
                         SUM(CASE WHEN user_id = %(user_id)s THEN 1 ELSE 0 END) as total_won,
                         MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '30 days' AND user_id = %(user_id)s THEN planned_revenue ELSE 0 END) as max_user_30,
                         MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '7 days' AND user_id = %(user_id)s THEN planned_revenue ELSE 0 END) as max_user_7,
                         MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '30 days' AND team_id = %(team_id)s THEN planned_revenue ELSE 0 END) as max_team_30,
                         MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '7 days' AND team_id = %(team_id)s THEN planned_revenue ELSE 0 END) as max_team_7
                     FROM crm_lead
                     WHERE
                         type = 'opportunity'
                     AND
                         active = True
                     AND
                         probability = 100
                     AND
                         DATE_TRUNC('year', date_closed) = DATE_TRUNC('year', CURRENT_DATE)
                     AND
                         (user_id = %(user_id)s OR team_id = %(team_id)s)
                 """
                lead.env.cr.execute(query, {'user_id': lead.user_id.id,
                                             'team_id': lead.team_id.id})
                query_result = self.env.cr.dictfetchone()
 
                message = False
                if query_result['total_won'] == 1:
                    message = _('Go, go, go! Congrats for your first deal.')
                elif query_result['max_team_30'] == lead.planned_revenue:
                    message = _('Boom! Team record for the past 30 days.')
                elif query_result['max_team_7'] == lead.planned_revenue:
                    message = _('Yeah! Deal of the last 7 days for the team.')
                elif query_result['max_user_30'] == lead.planned_revenue:
                    message = _('You just beat your personal record for the past 30 days.')
                elif query_result['max_user_7'] == lead.planned_revenue:
                    message = _('You just beat your personal record for the past 7 days.')
                if message:
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': message,
                            'img_url': '/web/image/%s/%s/image' % (lead.team_id.user_id._name, lead.team_id.user_id.id) if lead.team_id.user_id.image else '/web/static/src/img/smile.svg',
                            'type': 'rainbow_man',
                        }
                    }
            if self.process in ['sale','resale']:       
                if lead.unit_id:
                    new = self.env['zbbm.unit'].browse(lead.unit_id.id)
                    new.write({'state':'sold'})
            return True

    def set_member_color(self):
        res = {}     
        for record in self:
            if not self.building_id:
                raise Warning(_("""Please configure Building """))
            if not self.partner_id:
                raise Warning(_("""Please configure Customer """))
            stage_fields = []
            if record.stage_id.field_ids:
                 for items in self.env['crm.stage'].search([('probability','=',50)]).field_ids:
                     stage_fields.append(items.name)
                 
                 self.env.cr.execute("""select * from crm_lead where id=%s""",(record.id,))
                 lead_list = [i for i in self.env.cr.dictfetchall()]
                 print(lead_list,stage_fields)
                 for stage_field in stage_fields:
                     if not lead_list[0].get('%s'%(stage_field)):
                         raise Warning(_('Please provide %s'%(self._fields[stage_field].string)))
                 
             
            if self.process in ['sale','resale']:
                if not record.unit_id:
                    raise Warning(_("""Please configure Unit """))
                buid = self.env['zbbm.unit'].browse(self.unit_id.id)
                if buid:
                    if buid.state=='reserved':
                        if self._context.get('booked')!= 'make_open':
                            raise Warning(_('Unit already reserved by  %s'%buid.agent_id.name))
                        stage = self.env['crm.stage'].search([('probability','=',49)])
                        if stage:
                             msg ='Reserved by: %s on %s'%(buid.agent_id.name,buid.reservation_date)
                             record.stage_id = stage.id
                             record.store_prob = stage.probability
                             record.msg = msg
                             record.probability = stage.probability
                    else:
                        buid.write({'state':'reserved',
                                     'reservation_date':date.today(),
                                     'agent_id':self.user_id.id
                                    })
                         
                        stage = self.env['crm.stage'].search([('probability','=',50)])
                        if stage:
                            record.stage_id = stage.id
                            record.probability = stage.probability
                

    def set_unreserve_color(self):
        pp = pprint.PrettyPrinter(indent=4)
        res = {}     
#         for record in self:
#             buid = self.env['zbbm.unit'].browse(self.unit_id.id)
#             if buid:
#                 buid.write({'state':'new',
#                              'reservation_date':False,
#                              'reservation_time':5})
#                   
#                 stage = self.env['crm.stage'].search([('probability','=',record.store_prob)])
#                 if stage:
#                     record.stage_id = stage.id
#                     record.probability = stage.probability
#                     record.store_prob = stage.probability
#                 mail_pool = self.env['mail.mail']
#                 email_template_obj = self.env['mail.template']
#                 mailmess_pool = self.env['mail.message']
#                 mail_date = datetime.now()
#                 ir_model_data = self.env['ir.model.data']
#                 try:
#                     template_id = ir_model_data.get_object_reference('zb_crm_property', 'email_template_session_mail5_crm')[1]
#                 except ValueError:
#                     template_id = False
#                 if template_id:
#                     mail_template_obj = self.env['mail.template'].browse(template_id)
#                     body_html = self.env['mail.template']._render_template(mail_template_obj.body_html, 'crm.lead', record.id)    
#                     mail_values = {
# #                             'name': mail_template_obj.name,
#                         'subject': 'Reservation expiry  - Reminder ',
# #                             'model_id':record.id,
#                         'email_to': self.user_id.partner_id.email,
#                         'scheduled_date':(datetime.now() + timedelta(hours=1,minutes=30)),
#                         'body_html': body_html,
#                         'notification': True,
#                     }
#                     mail = self.env['mail.mail'].create(mail_values)
#                 else:
#                     raise Warning(_('Please provide Assigned user/Email'))
    
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
              
        if self._context.get('booked')!= 'make_open' and self.stage_id.probability not in [70.00,50.00,15.00,20.00,10.00,100.00,0.00]:
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
         
             

    def call_stage(self):
        stage = self.env['crm.stage'].search([('probability','=',15)])
        if stage:
            for items in self:
                items.stage_id = stage.id
                items.probability = stage.probability
                items.store_prob = stage.probability

     
    def followup_stage(self):
        stage = self.env['crm.stage'].search([('probability','=',20)])
        if stage:
            for items in self:
                items.stage_id = stage.id
                items.probability = stage.probability
                items.store_prob = stage.probability

#Commented the onchange as per the latest feedback for task 5650

#     @api.onchange('building_id','unit_id')
#     def get_description(self):
#         for items in self:
#             if items.building_id and items.unit_id:
#                 s= str(items.unit_id.name)
#                 u =items.building_id.name
#                 items.name = "Enquiry for Flat {} in {}".format(s,u)
    
    def make_buy(self):
        for items in self:
            journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
            if journal:
                acct_id = journal[0].default_credit_account_id.id
            vals = {
                'name': items.id,
                'partner_id': items.partner_id and items.partner_id.id,
                'type': 'out_invoice',
                'unit_id': items.unit_id and items.unit_id.id,
                'building_id':self.building_id and self.building_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': 'Unit Sale',
                    'price_unit': items.unit_id.price,
                    'quantity': 1,
                    'account_id': acct_id,
                })],
            }
            invoice_id = self.env['account.move'].create(vals)
            invoice_id.action_post()
            items.state = 'sold'
    
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.move'].search([('name','=',order.id)])
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)       
    
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.invoice_supplier_tree').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
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
        if self.process in ['sale','resale']:
            if not self.unit_id:
                raise Warning(_("""Please configure Unit """))
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
            if not self.partner_id:
                raise Warning(_('Please Select Customer'))
            if not self.unit_id.booking_per:
                raise Warning(_("Booking fee and Payment plan and hasn't been configured on the unit"))
            similar = self.search([('unit_id','=',self.unit_id.id),('id','!=',self.id)])
            if similar:
                for sim in similar:
                    if self._context.get('booked')!= 'make_open': 
                        sim.write({'probability': 0, 'active': False})
                    else:
                        sim.action_set_lost()
            module_ids = self.env.get('zbbm.unit').search([('id','=',self.unit_id.id),('building_id','=',self.building_id.id)])
            for idss in module_ids:
                l.append(idss.id)
            module_ids.write({'buyer_id':self.partner_id.id,
                              'state':'book',
                               'contract_date':datetime.today() })
            journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
            if journal:
                acct_id = journal[0].default_credit_account_id.id
     
            module_ids.write({
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
                    'res_model': 'zbbm.unit',
                    'res_id': module_ids.id or False,
                }
    
    def generate_vendor_bill(self):
        """
        Commission to agent on booking:vendor bill
        """
        if self.process in ['sale','resale']:
            unit = self.env['zbbm.unit'].search([('id','=',self.unit_id.id)])
            if unit.state == 'book':
                journal = self.env.get('account.journal').search([('type','=', 'purchase')], limit=1)
                if journal:
                    acct_id = journal[0].default_credit_account_id.id
                
                if unit.account_analytic_id:
                    analytic = unit.account_analytic_id.id
                else:
                    analytic = '' 
                        
                if unit.building_id.building_address.street:
                    street = unit.building_id.building_address.street
                else:
                    street = '' 
                    
                if unit.building_id.building_address.street2:
                    street2 = unit.building_id.building_address.street2
                else:
                    street2 = ''
                
                if unit.building_id.building_address.city:
                    city = unit.building_id.building_address.city
                else:
                    city = ''
                    
                if unit.building_id.building_address.country_id:
                    country = unit.building_id.building_address.country_id.name
                else:
                    country = ''
                        
                        
    #             company_id = self.env['res.company']._company_default_get()    
                currnet_user = self.env['res.users'].browse(self._uid)
                company_id = currnet_user.company_id  
                vals = {
                        'name':unit.name,
                        'invoice_payment_term_id':self.agent_id.property_supplier_payment_term_id.id if self.agent_id.property_supplier_payment_term_id else '',
                        'partner_id': self.agent_id.id,
                        'type': 'in_invoice',
                        'building_id':unit.building_id.id,
                        'unit_id':unit.id,
                        'lead_id':unit.lead_id.id,
                        'invoice_line_ids': [(0, 0, {
                                                    'name': '{},{},{},{},Area {},{},  Client:{},  {}% of {}'.format(unit.building_id.name,unit.name,street,street2,city,country,unit.buyer_id.name,self.commission_percent,unit.price),
                                                    'price_unit': unit.price *(self.commission_percent/100) if self.commission_percent else 0,
                                                    'quantity': 1,
                                                    'account_analytic_id':analytic,
                                                    'account_id': acct_id,
                                                     })],
                            }
    
                invoice_id = self.env['account.move'].create(vals)
                unit.vendor_id = invoice_id.id            
                self.unit_id.message_post(body=_('{} - Agent commission invoice generated').format(self.agent_id.name))
                return True
    
    def generate_customer_refund(self):
        """
            Customer refund on contract cancellation
         """

        customer_inv_obj = self.env['account.move'].search([('lead_id','=',self.id),('state','in',['paid','open']),('type','=','out_invoice')])
        agent_inv_obj = self.env['account.move'].search([('lead_id','=',self.id),('state','in',['paid','open']),('type','=','in_invoice')])
        unit = self.env['zbbm.unit'].search([('lead_id','=',self.id)])
        inv_amt = 0.00
        commission_amt = 0.00
        for inv in customer_inv_obj:
            inv_amt += (inv.amount_total - inv.residual)
        for invoice in agent_inv_obj:
            commission_amt += (invoice.amount_total - invoice.residual)
        amount = inv_amt - commission_amt
        if amount > 0:
            if not unit.building_id.account_id:
                journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                if journal:
                    acct_id = journal[0].default_debit_account_id.id
            else:
                acct_id = unit.building_id.account_id.id
            if unit.account_analytic_id:
                analytic = unit.account_analytic_id.id
            else:
                analytic = '' 
             
            vals = {
                'name':unit.name,
                'partner_id': self.partner_id.id,
                'type': 'out_refund',
#               'account_id': self.partner_id.property_account_receivable_id.id,
                'building_id':unit.building_id.id,
                'unit_id':unit.id,
                'lead_id':unit.lead_id.id,
                'invoice_line_ids': [(0, 0, {
                        'name': 'Refund on {}, {},   Client: {}'.format(unit.building_id.name,unit.name,unit.buyer_id.name),
                        'price_unit': amount or 0,
                        'quantity': 1,
                        'account_analytic_id':analytic,
                        'account_id': acct_id,
                         })],
                }
             
             
            invoice_id = self.env['account.move'].create(vals)
         
         
         
         
         
    
class Lead2OpportunityPartner(models.TransientModel):
 
    _inherit = 'crm.lead2opportunity.partner'
    
    need_asssign = fields.Boolean('Do you want to assign this lead to different salesperson',default =False)
     
     
    


   
class NewStage(models.Model):
    _inherit = 'crm.stage'
     
     
    field_ids = fields.Many2many('ir.model.fields',
                                  string='Required Fields',domain=[('model','=','crm.lead')])
    
    
    probability = fields.Float('Probability (%)', required=True, default=10.0, help="This percentage depicts the default/average probability of the Case for this stage to be a success")








