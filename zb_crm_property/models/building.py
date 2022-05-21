from odoo import models, fields, api,exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools.translate import _
from datetime import datetime,date,timedelta
import pprint
from dateutil import relativedelta


class zbbm_Unit(models.Model):

    _inherit = "zbbm.unit"
    _description = "Modules / Flat"
    
    @api.depends('invoice_ids1','invoice_ids1.state','invoice_total','balance_invoice','balance_total')
    def get_state(self):
        for flat in self:
            lead = self.env['crm.lead'].search([('unit_id','=',flat.id)])
            stage = self.env['crm.stage'].search([('probability','=',90)])
            deal =  self.env['crm.stage'].search([('probability','=',100)])
            journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
            if flat.downpayment > 0:    
                if flat.invoice_total >= flat.downpayment:
                    if flat.lead_id and stage:
                        unwanted_lead = self.env['crm.lead'].search([('unit_id','=',flat.id),('id','!=',flat.lead_id.id)])
                        if flat.state !='sold':
                           flat.write({'state':'contract'})
                             
                        if flat.lead_id.stage_id != deal: 
                           flat.lead_id.stage_id = stage.id
                           flat.lead_id.write({'stage_id':stage.id})
                        if unwanted_lead:
                            for all in unwanted_lead:
                                x = self.env['crm.lead'].browse(all.id)
                                x.action_set_lost()
   
                        flat.dummy = not flat.dummy     
                 
                                          
    
    dummy = fields.Boolean('Dummy',compute='get_state',store =True)
    
    
    def butn_refresh(self):
        return True
    
    
    @api.onchange('dummy')
    def onchan_dummy(self):
        self.butn_refresh()
    
    
    @api.model
    def action_set_new(self):
         
        all = self.env['zbbm.unit'].search([('state','=','reserved')])
        all2 = self.env['crm.lead'].search([('probability','=',49)])
            
        for session in all:
            if session.state =="reserved":
                end_date = datetime.strptime(str(session.reservation_date), '%Y-%m-%d') +timedelta(days=(session.reservation_time-1))
                if datetime.today() > end_date:
                    if all2:
                        for sess2 in all:
                            mail_pool = self.env['mail.mail']
                            email_template_obj = self.env['mail.template']
                            mailmess_pool = self.env['mail.message']
                            mail_date = datetime.now()
                            ir_model_data = sess2.env['ir.model.data']
                            try:
                                template_id = ir_model_data.get_object_reference('zb_crm_property', 'email_template_session_mail2_crm')[1]
                            except ValueError:
                                template_id = False
                            if template_id:
                                mail_template_obj = self.env['mail.template'].browse(template_id)
                                mail_id = mail_template_obj.send_mail(sess2.id, force_send=True)
                            else:
                                raise Warning(_('Please provide Assigned user/Email'))
                    mail_pool = self.env['mail.mail']
                    email_template_obj = self.env['mail.template']
                    mailmess_pool = self.env['mail.message']
                    mail_date = datetime.now()
                    ir_model_data = session.env['ir.model.data']
                    try:
                        template_id = ir_model_data.get_object_reference('zb_building_management', 'email_template_session_mail')[1]
                    except ValueError:
                        template_id = False
                    if template_id:
                        mail_template_obj = self.env['mail.template'].browse(template_id)
                        mail_id = mail_template_obj.send_mail(session.id, force_send=True)
                    else:
                        raise Warning(_('Please provide Assigned user/Email'))
                    
                    
                if end_date > datetime.strptime(str(session.reservation_date), '%Y-%m-%d') +timedelta(days=(session.reservation_time)) :
                    session.lead_id.probability = 20
                 
                return True
        return True
    
    
    
    @api.model
    def action_set_new_reserved(self):
          
        all = self.env['zbbm.unit'].search(['|',('state','=','reserved'),('state','=','book')])
        new = all2 = self.env['crm.stage'].search([('probability','=',10)])   
         
        for session in all:
            if session.state =="reserved":
                end_date = datetime.strptime(str(session.reservation_date), '%Y-%m-%d') +timedelta(days=(session.reservation_time))
                if datetime.today() > end_date:
                    if session.state =="reserved":
                        res_lead = self.env['crm.lead'].search([('probability','=',50),('unit_id','=',session.id)])
                        if res_lead:
                            res_lead.write({'stage_id' : new and new.id})
                            res_lead.stage_id= new.id
                            res_lead.probability = new.probability
                            session.state='new'

#Multiple invoices generated should be handled manaually
#                     elif session.state =="book":
#                         book_lead = self.env['crm.lead'].search([('probability','=',70),('module_id','=',session.id)])
#                         if book_lead:
#                             book_lead.write({'stage_id' : new and new.id})
#                             book_lead.stage_id= new.id
#                             book_lead.probability = new.probability
#                             book_lead.expired = True
#                             session.state = 'new'
#                         
                    
                    
                    
                    