from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    @api.onchange('job_order_id')
    def get_building(self):
        if self.job_order_id:
            self.building_id = self.job_order_id.building_id.id
            self.module_id = self.job_order_id.module_id.id
            self.lease_id = self.job_order_id.lease_id.id
            self.ticket_id = self.job_order_id.ticket_id.id
    
    
    job_order_id = fields.Many2one('job.order',string="Job Order")
    building_id = fields.Many2one("zbbm.building",string="Building")
    module_id = fields.Many2one("zbbm.module",string="Flat")
    lease_id = fields.Many2one('zbbm.module.lease.rent.agreement',string="Lease" ,domain="[('building_id', '=', building_id),('subproperty', '=', module_id),('state', '=', 'active')]")
    ticket_id = fields.Many2one('helpdesk.ticket',string="Ticket")
    

