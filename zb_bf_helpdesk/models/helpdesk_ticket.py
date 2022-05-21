from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    def _compute_jobs(self):
        jobs = self.env['job.order'].search([('ticket_id','=',self.id)])
        self.job_count = len(jobs) 
        

    def view_job_orders(self):
        jobs = self.env['job.order'].search([('ticket_id','=',self.id)])
        action = self.env.ref('zb_bf_helpdesk.job_order_action').read()[0]
        if len(jobs) > 1:
            action['domain'] = [('id', 'in', jobs.ids)]
        elif len(jobs) == 1:
            action['views'] = [(self.env.ref('zb_bf_helpdesk.job_order_form_view').id, 'form')]
            action['res_id'] = jobs.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    

    def action_create_jobs(self):
        vals = {
            'ticket_id':self.id,
            'building_id':self.building_id.id,
            'module_id':self.module_id.id,
            'lease_id':self.lease_id.id,
            'user_id':self.user_id.id,
        }
        job_id = self.env['job.order'].create(vals)
        self.job_order_id = job_id
        return job_id



    @api.onchange('building_id','module_id')
    def _onchange_building_module(self):
        if self.building_id and self.module_id:
            lease_id = self.env['zbbm.module.lease.rent.agreement'].search([('building_id', '=', self.building_id.id),('subproperty', '=', self.module_id.id),('state', '=', 'active')],order="id desc",limit=1)
            if lease_id:
                self.lease_id = lease_id.id
        
    
    building_id = fields.Many2one("zbbm.building",string="Building",required=True)
    module_id = fields.Many2one("zbbm.module",string="Flat")
    job_count = fields.Integer(compute='_compute_jobs',string='Job count')
    complaint_date = fields.Date(string='Complaint Date',required=True)
    lease_id = fields.Many2one('zbbm.module.lease.rent.agreement',string="Lease" ,domain="[('building_id', '=', building_id),('subproperty', '=', module_id),('state', '=', 'active')]")
    job_order_id = fields.Many2one("job.order",string="Job Order",copy=False)



