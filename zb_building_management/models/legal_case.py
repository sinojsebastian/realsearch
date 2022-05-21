from lxml import etree
from odoo import models, fields, api,exceptions,tools
from odoo.tools.translate import _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import logging
from dateutil import relativedelta
from odoo.tools.float_utils import float_round 
import odoo.addons.decimal_precision as dp
from datetime import date, timedelta
# from talloc import total_blocks
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


    
    
class Isdcodes(models.Model):   
    _name='isd.codes'
    _description = "Isd Codes"
    

    @api.depends('name')
    def name_get(self):
        result = []
        for event in self:
            result.append((event.id, '%s' % (event.country_id.name)))
        return result
    
    
    name=fields.Char('ISD')
    country_id = fields.Many2one('res.country', string='Nationality') 
    
    
""" Legal cases """

class Legal_Module(models.Model):    
    _name = 'legal.cases'
    _description = "Legal Cases"
    
    
    @api.model
    def create(self, vals):
        if vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('legal.cases')
        return super(Legal_Module, self).create(vals)
    
    
    @api.onchange('tenant_id')
    def get_contact(self):
        for tenant in self:
            if tenant.tenant_id.phone:
                tenant.phone = tenant.tenant_id.phone
    
    
    name= fields.Char('Case No',readonly = True)  
    tenant_id = fields.Many2one('res.partner', 'Tenant',copy =False)
    building_id = fields.Many2one('zbbm.building', 'Building',domain=[('building_type','=','rent')],copy =False)
    module_id = fields.Many2one('zbbm.module', 'Flat/Office',copy =False)
    rental_start_date = fields.Date('Lease Start Date')
    rental_end_date = fields.Date('Lease End Date')
    phone = fields.Char('Contact No',copy =False)
    note =fields.Text('Notes')
    state = fields.Selection([
        ('legal', 'Legal'),
        ('set', 'Settled'),
        ], 'Status', readonly=False,default='legal',copy =False)
            
    
    