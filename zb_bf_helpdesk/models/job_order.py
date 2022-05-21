from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from datetime import date


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    job_order_id = fields.Many2one('job.order','Purchase')


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    job_order_id = fields.Many2one('job.order','Sale')




class Job_Order(models.Model):
    _name = 'job.order'
    _description = 'Job Order'
    _inherit = ['mail.thread']
    _order ='name desc'


    def _compute_invoice(self):  
        invoice = self.env['account.move'].search([('job_id','=',self.id)])
        self.invoice_count= len(invoice) 


    def action_view_invoice(self):
        invoice = self.env['account.move'].search([('job_id','=',self.id)])
        action =  self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoice) > 1:
            action['domain'] = [('id', 'in', invoice.ids)]
        elif len(invoice) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoice.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

   
    def view_job_invoice_wizard_view(self):
        job_order = self
        ctx = self._context.copy()
        # for x in job_order.time_material_ids:
        #     print (x,'sdsdsd')
        # print ([(0, 0, {'product_id': x.product_id.id, 'description': x.description,'qty':x.qty,'unit_price':x.unit_price,'amount':x.amount}) for x in job_order.time_material_ids])
        ctx.update({'default_job_invoice_line_ids': [(0, 0, {'product_id': x.product_id.id,'time_material_id':x.id, 'description': x.description,'qty':x.qty,'unit_price':x.unit_price,'amount':x.amount}) for x in job_order.time_material_ids if x.invoice_id.state != 'posted' ]})
        return {
            'name': _('Create Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'job.invoice.wizard',
            'view_id': self.env.ref('zb_bf_helpdesk.job_invoice_wiz_form_view').id,
            'target': 'new',
            'context': ctx
        }
    
    
    name = fields.Char(String = "Job Order Number" , size = 20, Translate = True, readonly = True,default='/',copy=False)
    module_id = fields.Many2one("zbbm.module",string="Flat")
    building_id = fields.Many2one("zbbm.building",string="Building")
    user_id = fields.Many2one("res.users",string="Responsible",default=lambda self: self.env.user)
    date = fields.Date('Create Date',default=fields.Date.context_today)
    ticket_id = fields.Many2one("helpdesk.ticket",string="Ticket")
    state = fields.Selection([
            ('new', 'New'),
            ('waiting_approval', 'Waiting Approval'),
            ('confirmed', 'Confirmed'),
            ('inprogress', 'In Progress'),
            ('pending', 'Pending'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
            ],default='new',string='State',track_visibility='onchange')
    purchase_id = fields.Many2one('purchase.order',string="Purchase Id")
    sale_id = fields.Many2one('sale.order',string="Order Id")
    purchase_order_ids = fields.One2many('purchase.order','job_order_id','Purchase Order')
    invoice_count = fields.Integer(compute='_compute_invoice',string='Invoice count')
    sale_order_ids = fields.One2many('sale.order','job_order_id','Sale Order')
    time_material_ids = fields.One2many('time.material','job_id','Time And Material')
    lease_id = fields.Many2one('zbbm.module.lease.rent.agreement',string="Lease" ,domain="[('building_id', '=', building_id),('subproperty', '=', module_id),('state', '=', 'active')]")
    


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('job.order') 
        result = super(Job_Order,self).create(vals)
        return result
    
    
class TimeMaterial(models.Model):
    _name = "time.material"
    _description = "Time and Materials"
    
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.lst_price
            self.amount = self.unit_price*self.qty
     
    
    
    @api.depends('qty','unit_price')
    def _calculate_costs(self):
        for rec in self:
            rec.amount = rec.qty * rec.unit_price
            
    job_id = fields.Many2one('job.order',string='Job Order')
    product_id = fields.Many2one('product.product',string="Product")
    description = fields.Char(string='Description')
    qty = fields.Float(string = 'Quantity',default=1)
    unit_price = fields.Float(string='Unit Price',digits=(6, 3))
    amount = fields.Float(string='Amount',compute='_calculate_costs',store=True,digits=(6, 3))
    invoice_id = fields.Many2one('account.move', 'Invoice',copy=False, readonly=True, tracking=True,domain=[('type', '=', 'out_invoice')])
    


    def unlink(self):
        for move_line in self:
            if move_line.invoice_id:
                raise UserError(_('Cannot delete if it  already invoiced..!'))
        return super(TimeMaterial, self).unlink()