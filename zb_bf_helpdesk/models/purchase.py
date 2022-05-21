from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    
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
    
    
    
    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_building_id': self.building_id.id,
            'default_module_id': self.module_id.id,
            'default_lease_id': self.lease_id.id,
        }
        # Invoice_ids may be filtered depending on the user. To ensure we get all
        # invoices related to the purchase order, we read them in sudo to fill the
        # cache.
        self.sudo()._read(['invoice_ids'])
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_invoice_origin'] = self.name
        result['context']['default_ref'] = self.partner_ref
        return result

    

