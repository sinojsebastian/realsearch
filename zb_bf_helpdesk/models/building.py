from odoo import fields, models, api,_
from datetime import date,datetime,timedelta 

import logging
_logger = logging.getLogger(__name__)

class helpdesk_building(models.Model):
    _inherit = 'zbbm.building'
    
    
    def tickets_count(self):
         
        for building in self:
            tickets = self.env['helpdesk.ticket'].search([('building_id','=',building.id)])
            building.total_tickets = len(tickets) 
         
    def action_total_tickets(self):
        '''Function return the total no of Tickets'''
        ticket = [] 
        ticket_ids = self.env.get('helpdesk.ticket').search([('building_id','in',self.ids)])
        for idss in ticket_ids:
            ticket.append(idss.id)
             
        domain  = [('id', 'in',ticket)]
        return {
            'view_id':False,
            'name' : "Tickets",
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
            }   
         
    def open_tickets_count(self):
         
        new_ticket_ids = self.env.ref('helpdesk.stage_new')
        progress_ticket_ids = self.env.ref('helpdesk.stage_in_progress')
        for building in self:
            tickets = self.env['helpdesk.ticket'].search([('building_id','=',building.id),'|',('stage_id.running_stage','=',True),('stage_id.id','in',[new_ticket_ids.id,progress_ticket_ids.id])])
            building.open_tickets = len(tickets) 
         
    def action_open_tickets(self):
        '''Function return the total Open Tickets'''
         
        new_ticket_ids = self.env.ref('helpdesk.stage_new')
        progress_ticket_ids = self.env.ref('helpdesk.stage_in_progress')
        ticket = []
        open_ticket_ids = self.env.get('helpdesk.ticket').search([('building_id','in',self.ids),'|',('stage_id.running_stage','=',True),('stage_id.id','in',[new_ticket_ids.id,progress_ticket_ids.id])])
        for idss in open_ticket_ids:
            ticket.append(idss.id)
             
        domain  = [('id', 'in',ticket)]
        return {
            'view_id':False,
            'name' : "Tickets",
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
            }   
    
    
    
    total_tickets = fields.Integer(compute='tickets_count',
                                 string='Total Tickets')
    open_tickets = fields.Integer(compute='open_tickets_count',string='Open Tickets')