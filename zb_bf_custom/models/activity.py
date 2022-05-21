import time
from odoo import models, fields, api,exceptions,_


class Activity(models.Model):
    _name = 'activity.details'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
#     @api.one
#     def schedule_activity(self):
#       self.state = 'schedule'
#       self.message_post(body=("Activity Scheduled"))
       
    @api.model   
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('activity_seq') or 'New'       
        result = super(Activity, self).create(vals)       
        return result
    
    
    def create_lease_agreement(self):
         
        partner_id = ''
        if self.action == 'existing':
            partner_id = self.client_id.id
        elif self.action == 'new':
            partner_id = self._create_lead_partner()
            self.action = 'existing'
            self.client_id = partner_id
        form_view_id = self.env.ref('zb_building_management.view_lease_rent_agreement_form').id 
         
        return{
                        'name':'Lease Agreement form View',
                        'type': 'ir.actions.act_window',
                        'views': [(form_view_id, 'form')],
                        'res_model': 'zbbm.module.lease.rent.agreement',
                        'view_mode': 'form',
                        'context' : {'default_building_id' : self.building_id.id,
                                    'default_subproperty' : self.module_id.id,
                                    'default_lead_id' : self.id,
                                    'default_tenant_id' : partner_id
                                    },
                        }
        
    def _create_lead_partner(self):
        """ Create a partner from lead data
            :returns res.partner record
        """
        Partner = self.env['res.partner']
        partner_record = Partner.create(self._create_lead_partner_data(self.client_name, False))
        return partner_record.id
    
    def _create_lead_partner_data(self, name, parent_id=False):
        """ extract data from lead to create a partner
            :param name : furtur name of the partner
            :param is_company : True if the partner is a company
            :param parent_id : id of the parent partner (False if no parent)
            :returns res.partner record
        """
        res = {
            'name': name,
            'is_tenant':True,
            'type': 'contact'
        }
        return res    
    
    
#     @api.model
#     def _get_matching_partner(self):
# 
#         if self.client_name:  # search through the existing partners based on the lead's partner or contact name
#             partner = self.env['res.partner'].search([('name', 'ilike', '%' + self.client_name + '%')], limit=1)
#             return partner
# 
#         return False
        
    def view_agreements(self):
        
        agreements = self.env['zbbm.module.lease.rent.agreement'].search([('lead_id','=',self.id)])
        action = self.env.ref('zb_building_management.action_zbbm_module_lease_rent_view').read()[0]
        if len(agreements) > 1:
            action['domain'] = [('id', 'in', agreements.ids)]
        elif len(agreements) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_lease_rent_agreement_form').id, 'form')]
            action['res_id'] = agreements.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def _compute_agreement_count(self):
        for order in self:
            agreement_ids = self.env['zbbm.module.lease.rent.agreement'].search([('lead_id','=',self.id)])
            order.agreement_count = len(agreement_ids) 
    
    
    name = fields.Char(string="Sequence Number", readonly=True, required=True, copy=False, default='New') 
    partner_id = fields.Many2one('res.partner','Customer',readonly=True,states={'new': [('readonly', False)]})
    create_date = fields.Datetime('Create date',readonly=True)
    building_id = fields.Many2one('zbbm.building', 'Building', track_visibility='onchange',readonly=True,states={'new': [('readonly', False)]})
    module_id = fields.Many2one('zbbm.module', 'Flat/Office', track_visibility='onchange',readonly=True,states={'new': [('readonly', False)]})
    date = fields.Date('Schedule Date', track_visibility='onchange',readonly=True,states={'new': [('readonly', False)]})
    report_id = fields.Many2one('res.users','Property Advisor', track_visibility='onchange',default=lambda self: self.env.user,readonly=True,states={'new': [('readonly', False)]})
    notes = fields.Text('Comment',readonly=True,states={'new': [('readonly', False)]})
    summary = fields.Text('Summary',readonly=True,states={'new': [('readonly', False)]})
    state = fields.Selection([
            ('new', 'New'),
            ('schedule', 'Schedule'),
            ('follow_up', 'Follow up'),
            ('done', 'Done'),
            ],default='new')
    
    action = fields.Selection([
        ('existing', 'Existing Client'),
        ('new', 'New Client')
    ], 'Action', required=True)
    client_name = fields.Char('Client Name', track_visibility='onchange',)
    client_id = fields.Many2one('res.partner','Client Name')
    street = fields.Char('Street')
    build_no = fields.Char('Building No')
    road_no = fields.Char('Road No')
    area = fields.Char('Area')
    po = fields.Char('PO Box')
    country_id = fields.Many2one('res.country','Country')
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')
    agreement_count = fields.Integer(compute='_compute_agreement_count',string='Lease Agreements')