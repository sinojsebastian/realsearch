from odoo import fields, models, api,_
import re
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError,Warning
from dateutil import relativedelta
from datetime import date,datetime,timedelta 
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import math

import odoo.addons.decimal_precision as dp


import logging
# from future.backports.email.policy import default
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    purchase_id = fields.Many2one('zbbm.unit','Unit')


class zbbm_building(models.Model):
    _inherit = 'zbbm.building'
    
    
    image_building_1920 = fields.Image("Building Image", max_width=1920, max_height=1920)
    image_building_1024 = fields.Image("Building Image 1024", related="image_building_1920", max_width=1024, max_height=1024, store=True)
    image_building_512 = fields.Image("Building Image 512", related="image_building_1920", max_width=512, max_height=512, store=True)
    image_building_256 = fields.Image("Building Image 256", related="image_building_1920", max_width=256, max_height=256, store=True)
    image_building_128 = fields.Image("Building Image 128", related="image_building_1920", max_width=128, max_height=128, store=True)
    
    image_1920 = fields.Image("Original Image", compute='_compute_image_1920', inverse='_set_image_1920')
    image_1024 = fields.Image("Image 1024", compute='_compute_image_1024')
    image_512 = fields.Image("Image 512", compute='_compute_image_512')
    image_256 = fields.Image("Image 256", compute='_compute_image_256')
    image_128 = fields.Image("Image 128", compute='_compute_image_128')
    pa_ids = fields.Many2many('res.users', 'building_pa_rel', 'building_id', 'pa_id',string="Property Advisor")
    
#     Commented to Solve PA Building issue    
#     Date : 16/07/2021
#     By : PV
    def read(self, fields, load='_classic_read'):
        return super(zbbm_building, self.sudo()).read(fields, load=load)
    
    
    def _compute_image_1920(self):
       
        for record in self:
            record.image_1920 = record.image_building_1920
            
    def _set_image_1920(self):
        for record in self:
            if (
                # We are trying to remove an image even though it is already
                # not set, remove it from the template instead.
                not record.image_1920 and not record.image_building_1920
                # We are trying to add an image, but the template image is
                # not set, write on the template instead.
                # There is only one variant, always write on the template.
            ):
                record.image_building_1920 = False
            else:
                record.image_building_1920 = record.image_1920
    
    
    def _compute_image_1024(self):
        
        for record in self:
            record.image_1024 = record.image_building_1024 

    def _compute_image_512(self):
       
        for record in self:
            record.image_512 = record.image_building_512

    def _compute_image_256(self):
        
        for record in self:
            record.image_256 = record.image_building_256 

    def _compute_image_128(self):
       
        for record in self:
            record.image_128 = record.image_building_128 

    
    def _compute_service(self):
        invoices = self.env['account.move'].search([('building_id','=',self.id)])
        self.services_count = len(invoices) 
        

    def view_service_charge_invoice(self):
        invoices = self.env['account.move'].search([('building_id','=',self.id)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def action_view_services(self):
        params = self.env['ir.config_parameter'].sudo() 
        service_journal_id=params.get_param('zb_bf_custom.service_invoice_journal_id') or False
        if not service_journal_id:
            raise UserError(_('Please Configure a Service Invoice Journal'))
        serv_invoices = self.env['account.move'].search([('building_id','=',self.id),('type','=','out_invoice'),('journal_id','=',int(service_journal_id))])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(serv_invoices) > 1:
            action['domain'] = [('id', 'in', serv_invoices.ids)]
        elif len(serv_invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = serv_invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def action_view_rent_invs(self):
        params = self.env['ir.config_parameter'].sudo() 
        commission_journal_id = params.get_param('zb_bf_custom.commission_journal_id') or False
        if not commission_journal_id:
            raise Warning(_('Please Configure Commission Journal'))
        comm_invoices = self.env['account.move'].search([('building_id','=',self.id),('type','=','out_invoice'),('journal_id','=',int(commission_journal_id))])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(comm_invoices) > 1:
            action['domain'] = [('id', 'in', comm_invoices.ids)]
        elif len(comm_invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = comm_invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def _compute_serv_inv_count(self):
        for order in self:
            params = self.env['ir.config_parameter'].sudo() 
            service_journal_id=params.get_param('zb_bf_custom.service_invoice_journal_id') or False
            if service_journal_id:
                serv_invoices =  self.env['account.move'].search([('building_id','=',self.id),('type','=','out_invoice'),('journal_id','=',int(service_journal_id))])
                order.service_inv_count = len(serv_invoices) 
    
    
    def _compute_comm_inv_count(self):
        for order in self:
            params = self.env['ir.config_parameter'].sudo() 
            commission_journal_id = params.get_param('zb_bf_custom.commission_journal_id') or False
            if commission_journal_id:
                comm_invoices =  self.env['account.move'].search([('building_id','=',self.id),('type','=','out_invoice'),('journal_id','=',int(commission_journal_id))])
                order.comm_inv_count = len(comm_invoices) 
                
                
    def _compute_invoices(self):
        invoices = self.env['account.move'].search([('building_id','=',self.id),('type','in',['out_invoice','out_refund'])])
        self.invoices_count = len(invoices) 
        
        
    def action_view_invoices(self):
        invoices = self.env['account.move'].search([('building_id','=',self.id),('type','in',['out_invoice','out_refund'])])
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
            action['context'] = {'group_by':'journal_id'}
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
            action['context'] = {'group_by':'journal_id'}
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def _compute_expenses(self):
        expenses = self.env['account.move'].search([('building_id','=',self.id),('type','in',['in_invoice','in_refund'])])
        self.expenses_count = len(expenses) 
        
         
    def action_view_expenses(self):
        expenses = self.env['account.move'].search([('building_id','=',self.id),('type','in',['in_invoice','in_refund'])])
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if len(expenses) > 1:
            action['domain'] = [('id', 'in', expenses.ids)]
            action['context'] = {'group_by':'journal_id'}
        elif len(expenses) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = expenses.ids[0]
            action['context'] = {'group_by':'journal_id'}
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def _compute_service_charge_total(self):
        service_total = 0
        params = self.env['ir.config_parameter'].sudo()
        service_journal_ids = params.get_param('zb_bf_custom.service_journal_id')
        if service_journal_ids:
            services = self.env['account.move'].search([('building_id','=',self.id),('state','=','posted'),('journal_id','=',int(service_journal_ids))])
            for rec in services:
                service_total += rec.amount_total
        self.service_charge_total = service_total
        
        
    def _compute_service_charge_collected(self):
        service_collected = 0
        params = self.env['ir.config_parameter'].sudo()
        service_journal_ids = params.get_param('zb_bf_custom.service_journal_id')
        if service_journal_ids:
            services = self.env['account.move'].search([('building_id','=',self.id),('state','=','posted'),('journal_id','=',int(service_journal_ids))])
            for rec in services:
                service_collected += rec.amount_total-rec.amount_residual
        self.service_charge_collected = service_collected
        
        
    def _compute_service_charge_remaining(self):
        service_remaining = 0
        params = self.env['ir.config_parameter'].sudo()
        service_journal_ids = params.get_param('zb_bf_custom.service_journal_id')
        if service_journal_ids:
            services = self.env['account.move'].search([('building_id','=',self.id),('state','=','posted'),('journal_id','=',int(service_journal_ids))])
            for rec in services:
                service_remaining += rec.amount_residual
        self.service_charge_remaining = service_remaining
        
        
    def _compute_rs_total_income(self):
        total_income = 0
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        invoices = self.env['account.move'].search([('building_id','=',self.id),('state','=','posted'),('type','in',('out_invoice','out_refund')),('journal_id','in',journal_ids)])
        for rec in invoices:
            total_income += rec.amount_total
        self.rs_total_income = total_income
        
        
    def _compute_rs_total_expense(self):
        total_expense = 0
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        invoices = self.env['account.move'].search([('building_id','=',self.id),('state','=','posted'),('type','in',('in_invoice','in_refund')),('journal_id','in',journal_ids)])
        for rec in invoices:
            total_expense += rec.amount_total
        self.rs_total_expense = total_expense
        
        
    def _compute_owner_total_income(self):
        total_owner_income = 0
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        invoices = self.env['account.move'].search([('building_id','=',self.id),('state','=','posted'),('type','in',('out_invoice','out_refund')),('journal_id','in',journal_ids)])
        for rec in invoices:
            total_owner_income += rec.amount_total
        self.owner_total_income = total_owner_income
        
        
    def _compute_owner_total_expense(self):
        total_owner_expense = 0
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        invoices = self.env['account.move'].search([('building_id','=',self.id),('state','=','posted'),('type','in',('in_invoice','in_refund')),('journal_id','in',journal_ids)])
        for rec in invoices:
            total_owner_expense += rec.amount_total
        self.owner_total_expense = total_owner_expense
        
        
    def total_enquires_count(self):
        
        for building in self:
            enquires = self.env.get('crm.lead').search([('building_id','in',[building.id]),('process','=','rental')])
            building.total_enquires = len(enquires) 
            
        
    def action_total_enquires(self):
        '''Function return the total Enquires'''
        
        enquires = [] 
        enquires_ids = self.env.get('crm.lead').search([('building_id','in',self.ids),('process','=','rental')])
        for idss in enquires_ids:
            enquires.append(idss.id)
        domain  = [('id', 'in',enquires)]
        return {
            'view_id':False,
            'name' : "Rental Activity",
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
            }   
        
        
    def open_enquires_count(self):
        
        new_satge_ids  = self.env['crm.stage'].search([('probability','=',10.00)])
        for building in self:
            if len(new_satge_ids) > 0:
                enquires = self.env.get('crm.lead').search([('building_id','in',[building.id]),('process','=','rental'),('stage_id','=',new_satge_ids[0].id)])
            else:
                enquires = self.env.get('crm.lead').search([('building_id','in',[building.id]),('process','=','rental')])
            building.open_enquires = len(enquires) 
        
        
    def action_open_enquires(self):
        '''Function return the total Open Enquires'''
        
        open_enquires = [] 
        new_satge_ids  = self.env['crm.stage'].search([('probability','=',10.00)])
        if len(new_satge_ids) > 0:
            open_enquires_ids = self.env.get('crm.lead').search([('building_id','in',self.ids),('process','=','rental'),('stage_id','=',new_satge_ids[0].id)])
        else:
            open_enquires_ids = self.env.get('crm.lead').search([('building_id','in',self.ids),('process','=','rental')])

        for idss in open_enquires_ids:
            open_enquires.append(idss.id)
            
        domain  = [('id', 'in',open_enquires)]
        return {
            'view_id':False,
            'name' : "Rental Activity",
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
            }   
        
    @api.model
    def create(self, vals):
        res = super(zbbm_building, self).create(vals)
        if vals.get('pa_ids'):
            partner_ids = []
            partner_ids = [x.owner_id.id for x in res.module_ids]
            partner_ids += [x.tenant_id.id for x in res.module_ids]
            if partner_ids:
                partner_obj = self.env['res.partner'].browse(list(set(partner_ids)))
                partner_obj._compute_pa()
        return res
    
    def write(self, vals):
        if self.env.user.has_group('zb_bf_custom.group_property_advisor') and self.env.user.has_group('sales_team.group_sale_salesman'):
            if 'pending_type' not in vals:
                raise UserError(_('Property Advisor has no write permission'))
                
        res = super(zbbm_building, self).write(vals)
        if vals.get('pa_ids') or vals.get('module_ids'):
            partner_ids = []
            partner_ids = [x.owner_id.id for x in self.module_ids]
            partner_ids += [x.tenant_id.id for x in self.module_ids]
            if partner_ids:
                partner_obj = self.env['res.partner'].browse(list(set(partner_ids)))
                partner_obj._compute_pa()
        return res
    
    def unlink(self):
        for items in self:
            if not self.env.user.has_group('zb_building_management.group_tijaria_admin') and not self.env.user.has_group('zb_building_management.group_user_management'):
                raise UserError(_('You are not allowed to do this operation'))
        return super(zbbm_building, self).unlink()
    
    
    
    unit_ids = fields.One2many('zbbm.unit', 'building_id', string='Unit', readonly=True)
    area_manager = fields.Many2one('res.users','Area Manager')
    dlp_end_date = fields.Date('DLP End Date')
    service_charge = fields.Float('Service Charge(m²)',digits = (12,3))
    next_service_charge_invoice_date = fields.Date('Next Service Charge Invoice Date')
    services_count = fields.Integer(compute='_compute_service',string='Service Charges')
    management_fees_percent = fields.Float(string="Management Fees(%)")
    raw_service_ids = fields.One2many('raw.services','building_id',string="Services")
    service_ids=fields.One2many('zbbm.services', 'building_id', string='Services',track_visibility='onchange')
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    total_commission_percent = fields.Float(string="Total Commission(%)")
    resale_commission_percent = fields.Float(string="Resale Commission(%)")
    building_area = fields.Float('Building Area')
    hand_over_date =fields.Date('Hand over Date')
    admin_fee = fields.Float('Default Admin Fee',digits = (12,3))
    service_inv_count = fields.Integer(compute='_compute_serv_inv_count',string='Service Count')
    comm_inv_count = fields.Integer(compute='_compute_comm_inv_count',string='Commission Count')
    invoices_count = fields.Integer(compute='_compute_invoices',string='Invoices')
    expenses_count = fields.Integer(compute='_compute_expenses',string='Expenses')
    service_charge_total = fields.Float(compute='_compute_service_charge_total',string='Service Charge Total',digits = (12,3))
    service_charge_collected = fields.Float(compute='_compute_service_charge_collected',string='Service Charge Collected',digits = (12,3))
    service_charge_remaining = fields.Float(compute='_compute_service_charge_remaining',string='Service Charge Remaining',digits = (12,3))
    rs_total_income = fields.Float(compute='_compute_rs_total_income',string='RS Total Income',digits = (12,3))
    rs_total_expense = fields.Float(compute='_compute_rs_total_expense',string='RS Total Expense',digits = (12,3))
    owner_total_income = fields.Float(compute='_compute_owner_total_income',string='Owner Total Income',digits = (12,3))
    owner_total_expense = fields.Float(compute='_compute_owner_total_expense',string='Owner Total Expense',digits = (12,3))
    total_enquires = fields.Integer(compute='total_enquires_count',string='Total Enquires')
    open_enquires = fields.Integer(compute='open_enquires_count',string='Open Enquires')
    resale_owner_commission_percent = fields.Float(string="Resale Owner Commission(%)")
    resale_buyer_commission_percent = fields.Float(string="Resale Buyer Commission(%)")
    resale_agent_commission_percent = fields.Float(string="Resale Agent Commission(%)")
    address_arabic = fields.Text(string='Building Address in Arabic')
    is_locked = fields.Boolean('Locked',default=False)


class ServiceLines(models.Model):

    _name = "service.lines"
    _description = "Service Lines"
    
    
    service_id = fields.Many2one('zbbm.unit','Service ID')
    services_id = fields.Many2one('zbbm.unit','Services ID')
    
    bill = fields.Selection([
                    ('fixed', 'Fixed'),
                    ('owner', 'Extra By Owner'),
                    ('tenant','Extra By Tenant')
                    ], 'Bill',default='fixed')
    owner_share = fields.Float('Owner Share')
    tenant_share = fields.Float('Tenant Share')
    date = fields.Date('Date')
    owner_id = fields.Many2one('res.partner','Owner')
    tenant_id = fields.Many2one('res.partner','Tenant')
    billing_status = fields.Selection([
                    ('to_be_invoiced', 'To Be Invoiced'),
                    ('invoiced', 'Invoiced'),
                    ], 'Billing Status',default='to_be_invoiced')
    product_id = fields.Many2one('product.product','Service')
    
    
class zbbm_module(models.Model):

    _inherit = 'zbbm.module'
    _description = "Module / Flat"
    
    
    _sql_constraints = [('unit_uniq', 'UNIQUE(name,building_id)', 'Unit cannot be duplicated')]
    
#     @api.constrains('service_ids')
#     def _check_exist_product_in_line(self):
#     
#       service_ids = self.env['zbbm.services'].search([])
#       for order in self:
#           exist_product_list = []
#           for line in order.service_ids:
#              if line.account_no in exist_product_list:
#                 raise ValidationError(_('A Product with same Account No Already Exists.'))
#              exist_product_list.append(line.account_no)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(zbbm_module, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         default_type = self._context.get('default_type', False)
        if self.env.user.has_group('zb_bf_custom.group_property_advisor'):
            contract_report = self.env.ref('zb_bf_custom.report_management_contract_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == contract_report.id:
                    res['toolbar']['print'].remove(print_submenu)
            
        return res
    
    
    def unlink(self):
        for items in self:
            if not self.env.user.has_group('zb_building_management.group_tijaria_admin') and not self.env.user.has_group('zb_building_management.group_user_management'):
                raise UserError(_('You are not allowed to do this operation'))
            if items.building_id.state not in ['new'] and items.building_id.is_locked == True:
                raise Warning(_('You cannot delete the unit!!'))
        return super(zbbm_module, self).unlink()
    
    
    @api.constrains('reservation_time')
    def _check_maximum(self):
        params = self.env['ir.config_parameter'].sudo()
        max_reservation_time = params.get_param('zb_bf_custom.max_reservation_time_lease') or 0.0
        if self.reservation_time > int(max_reservation_time):
            raise Warning(_('Maximum reservation time is %s days'%(max_reservation_time)))
    
    
    def generate_sellable_unit(self):
        for order in self:
            sellable_unit_obj = self.env['zbbm.unit']
            sellable_unit_dict = {
                'name':order.name,
                'building_id':order.building_id.id,
                'owner_id':order.owner_id.id,
                'floor':order.floor_number,
                'unit_area':order.unit_area_final_contract,
                'price':0.000,
                'resale':True,
#                 'floor_plan':
                }
            
            sellable_unit_id = sellable_unit_obj.create(sellable_unit_dict)
            order.unit_id = sellable_unit_id.id
            
    
    @api.model
    def create(self,vals):
        res = super(zbbm_module,self).create(vals)
        params = self.env['ir.config_parameter'].sudo()      
        owner_id = params.get_param('zb_bf_custom.owner_id') or False,
        owner = self.env['res.partner'].search([('id','=',int(owner_id[0]))])
        if not vals.get('owner_id'):
            res.owner_id = owner
        if vals.get('building_id'):
            building = self.env['zbbm.building'].browse(vals.get('building_id'))
            if building.state not in ['new'] and building.is_locked == True:
                raise Warning(_('You cannot create the unit!!'))
        return res
    
    
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.move'].search([('module_id.id','=',self.id),('type','=','out_invoice'),('management_fees_boolean','=',True)])
            order.invoices_count = len(invoices) 
            
    
    
    def action_view_invoice(self):
        invoices = self.env['account.move'].search([('module_id','=',self.id),('management_fees_boolean','=',True),('type','=','out_invoice')])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    
    def action_view_payment_advises(self):
        invoices = self.env['account.payment'].search([('module_id','=',self.id),('payment_type','=','outbound'),('payment_advise','=',True)])
        action = self.env.ref('account.action_account_payments_payable').read()[0]
        action['context'] = {'default_payment_advise': 'True',
                'default_partner_type': 'customer',
                'search_default_inbound_filter': 1,
                'res_partner_search_mode': 'customer',}
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action  
    
    
    
    def action_view_rs_inv(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        invoices = self.env['account.move'].search([('module_id','=',self.id),('type','in',('out_invoice','out_refund','entry')),('journal_id','in',journal_ids)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_account_move_inherit_zb').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action  
    
    
    def action_view_owner_inv(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        invoices = self.env['account.move'].search([('module_id','=',self.id),('type','in',('out_invoice','out_refund','entry')),('journal_id','in',journal_ids)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_account_move_inherit_zb').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def action_view_owner_expense(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        invoices = self.env['account.move'].search([('module_id','=',self.id),('type','in',('in_invoice','in_refund','entry')),('journal_id','in',journal_ids)])
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]        
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_account_move_inherit_zb').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    
    def action_view_rs_expense(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        invoices = self.env['account.move'].search([('module_id','=',self.id),('type','in',('in_invoice','in_refund','entry')),('journal_id','in',journal_ids)])
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]        
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_account_move_inherit_zb').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action  
    
    
    def action_view_receipts(self):
        receipts = self.env['account.payment'].search([('module_id','=',self.id),('payment_type','in',['inbound'])])
        action = self.env.ref('account.action_account_payments').read()[0]
        if len(receipts) > 1:
            action['domain'] = [('id', 'in', receipts.ids)]
        elif len(receipts) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = receipts.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def action_view_payments(self):
        payments = self.env['account.payment'].search([('module_id','=',self.id),('payment_type','in',['outbound'])])
        action = self.env.ref('account.action_account_payments_payable').read()[0]
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = payments.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action   
    
    
    def _compute_owner_inv_count(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        for order in self:
            move_ids = self.env['account.move'].search([('module_id','=',self.id),('type','in',('out_invoice','out_refund')),('journal_id','in',journal_ids)])
            order.owner_inv_count = len(move_ids) 
            
            
    def _compute_rs_inv_count(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        for order in self:
            move_ids = self.env['account.move'].search([('module_id','=',self.id),('type','in',('out_invoice','out_refund')),('journal_id','in',journal_ids)])
            order.rs_inv_count = len(move_ids) 
            
            
    def _compute_rs_exp_count(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        for order in self:
            move_ids = self.env['account.move'].search([('module_id','=',self.id),('type','in',('in_invoice','in_refund')),('journal_id','in',journal_ids)])
            order.rs_exp_count = len(move_ids) 
            
            
    def _compute_owner_exp_count(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        for order in self:
            move_ids = self.env['account.move'].search([('module_id','=',self.id),('type','in',('in_invoice','in_refund')),('journal_id','in',journal_ids)])
            order.owner_exp_count = len(move_ids) 
             
             
    def _compute_receipts_count(self):
        for order in self:
            payment_ids = self.env['account.payment'].search([('module_id','=',self.id),('payment_type','=','inbound')])
            order.receipts_count = len(payment_ids)
            
            
    def _compute_payments_count(self):
        for order in self:
            payment_ids = self.env['account.payment'].search([('module_id','=',self.id),('payment_type','=','outbound'),('payment_advise','=',False)])
            order.payments_count = len(payment_ids) 
    
    
    def _compute_payment_advises(self):
        for order in self:
            payment_ids = self.env['account.payment'].search([('module_id','=',self.id),('payment_type','=','outbound'),('payment_advise','=',True)])
            order.payment_advise_count = len(payment_ids)
            
    def write(self, vals):
        '''Modified for Message Post'''
        msg = ''
        if self.ids:
            if vals.get('potential_rent', False):
                msg = '<b>Potential Rent Changed </b> to %.3f </br>' %vals['potential_rent']
                self.message_post(body=msg)
            if vals.get('management_fees_percent', False):
                msg = '<b>Management Fees Changed </b> to %s</br>' %vals['management_fees_percent']+'%'
                self.message_post(body=msg)
            if vals.get('service_charge', False):
                msg = '<b>Service Charge Changed </b> to %.3f </br>' %vals['service_charge']
                self.message_post(body=msg)
        
        if vals.get('building_id'):
            building = self.env['zbbm.building'].browse(vals.get('building_id'))
            if building.state not in ['new'] and building.is_locked == True:
                raise Warning(_('You cannot Modify the unit!!'))
            elif self.building_id.state not in ['new'] and self.building_id.is_locked == True:
                raise Warning(_('You cannot Modify the unit!!'))
#             if msg:
#                 self.message_post(body=msg)
                     
        res = super(zbbm_module, self).write(vals)
        return res
    
    def get_las_reser(self):
        for items in self:
            if items.reservation_date and items.reservation_time:
                items.las_reser = datetime.strptime(str(items.reservation_date), '%Y-%m-%d') + timedelta(days=items.reservation_time)
            else:
                items.las_reser = ''
    
    @api.model  
    def default_reservation_time(self):
        '''
            Default getting of reservation time from configuration 
        '''
        params = self.env['ir.config_parameter'].sudo()
        default_reservation_time = params.get_param('zb_building_management.reservation_time') or 0.0
        return default_reservation_time

    @api.model
    def action_set_new_module(self):
         
        all = self.env['zbbm.module'].search([('state','=','reserve')])
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
    def action_set_new_reserved_module(self):
#         all = self.env['zbbm.module'].search(['|',('state','=','reserve'),('state','=','book')])
        reserved_unit = self.env['zbbm.module'].search([('state','=','reserve')])
#         booked_unit = self.env['zbbm.module'].search([('state','=','book')])
        new = all2 = self.env['crm.stage'].search([('probability','=',10)],limit=1) 
        reserved = self.env['crm.stage'].search([('probability','=',50)]) 
        booked = self.env['crm.stage'].search([('probability','=',70)]) 
        end_date = ''
        book_date = ''
        for session in reserved_unit:
            if session.reservation_date and session.reservation_time:
                end_date = datetime.strptime(str(session.reservation_date), '%Y-%m-%d') +timedelta(days=(session.reservation_time))
            if end_date:
                if datetime.today() > end_date:
                    if session.state =="reserve":
                        res_lead = self.env['crm.lead'].search([('probability','=',50),('module_id','=',session.id),('process','in',['rental'])])
                        wait_lead = self.env['crm.lead'].search([('probability','=',49),('module_id','=',session.id)])
                        if res_lead:
                            res_lead.write({'stage_id' : new and new.id})
                            res_lead.stage_id= new.id
                            res_lead.probability = new.probability
                            res_lead.reserve_expired = True
                            session.state = 'available'
#                         res_lead.action_set_lost()
#                     if wait_lead:
#                         wait_lead.stage_id = reserved.id
#                         wait_lead.probability = reserved.probability
#                         wait_lead.module_id.state = 'reserve'
 #[ZB-5652] Rental activity booked stage changesMultiple leads should be manually handed
        book_lead = self.env['crm.lead'].search([('probability','=',70),('process','in',['rental'])])
        for lead in book_lead:
            if lead.module_id.booking_date and lead.module_id.booking_time:
                book_date = datetime.strptime(str(lead.module_id.booking_date), '%Y-%m-%d') +timedelta(days=(lead.module_id.booking_time))
            if book_date:
                if datetime.today() > book_date: 
#                     if session.state =="book":
                    created_lease = self.env['zbbm.module.lease.rent.agreement'].search([('crm_lead_id','=',lead.id)])
                    if not created_lease:
                        lead.write({'stage_id' : new and new.id})
                        lead.stage_id= new.id
                        lead.probability = new.probability
                        lead.book_expired = True
                        lead.module_id.state = 'available'
#Sellable units invoices should be manually handed [ZB-5652] Rental activity booked stage changes
#                         res_lead.action_set_lost()
    
#                         res_lead.action_set_lost()

      # commented by Ansu. ZB-6184-code changes: is_salesperson
    # def _compute_salesperson(self):
    #     for module in self:
    #         current_user = self.env['res.users'].browse(self._uid)
    #         if module.user_id == current_user:
    #             module.is_salesperson = True
    #         else:
    #             module.is_salesperson =  False
    
    name = fields.Char('Unit/Office', required=True, size=32)
    unit_arabic = fields.Char('Unit in Arabic')
    owner_id=fields.Many2one('res.partner','Owner',track_visibility='onchange')
    flat_on_offer = fields.Boolean('Flat On Offer')
    offer_start_date = fields.Date('Offer Start Date')
    offer_end_date = fields.Date('Offer End Date')
    managed = fields.Boolean('Managed',default=False,track_visibility='onchange')
    have_pool = fields.Boolean('Pool',default=False)
    balcony = fields.Boolean('Balcony',default=False)
    gym = fields.Boolean('Gym',default=False)
    no_of_washroom = fields.Integer('No.Of Washrooms')
    no_of_rooms = fields.Integer('No.Of Rooms')
    floor_area = fields.Float('Floor Area')
    title_deed_id = fields.Many2one('title.deed','Title Deed')
    service_charge = fields.Float('Service Charge',digits = (12,3))
    feature_id = fields.Many2one('other.features',string="Feature")
    other_features_ids = fields.Many2many('other.features','module_features_rel','module_id','feature_id',string="Other Features") 
#     other_features_ids = fields.Many2many('other.features','lease_features_reltn','lease_agreement_id','feature_id',string="Other Features") 
    purchase_id = fields.Many2one('purchase.order',string="Purchase Id")
    purchase_order_ids = fields.One2many('purchase.order','module_id','Purchase Order')
    deposit = fields.Float(string="Deposit",digits = (12,3))
    raw_service_ids = fields.One2many('raw.services','module_id',string="Services")
    services_id = fields.Many2one('zbbm.services',string="Service")
    service_ids=fields.One2many('zbbm.services', 'module_id', string='Services',track_visibility='onchange')
    management_fees_percent = fields.Float(string="Management Fees(%)")
    service_move_id = fields.Many2one('account.move',string="Owner/Tenant/Invoice")
    total_commission_percent = fields.Float(string="Total Commission Percent",related="building_id.total_commission_percent")
    invoices_count = fields.Integer(compute='_compute_invoice',string='Invoice Counts') 
    receipt_ids = fields.One2many('account.payment', 'module_id', 'Receipts')
    floor_number = fields.Char('Floor Number')
    unit_view_id = fields.Many2one('unit.view','View')
    unit_area_final_contract = fields.Integer('Unit Area(As Per Final Contract)')
    unit_area_title_deed = fields.Integer('Unit Area(As Per Title Deed)')
    owner_inv_count = fields.Integer(compute='_compute_owner_inv_count',string='Owner Invoices') 
    rs_inv_count = fields.Integer(compute='_compute_rs_inv_count',string='Real search Invoices')
    owner_exp_count = fields.Integer(compute='_compute_owner_exp_count',string='Owner Expenses') 
    rs_exp_count = fields.Integer(compute='_compute_rs_exp_count',string='Real search Expenses') 
    receipts_count = fields.Integer(compute='_compute_receipts_count',string='Receipts') 
    payments_count = fields.Integer(compute='_compute_payments_count',string='Payments') 
    payment_advise_count = fields.Integer(compute='_compute_payment_advises',string='Payment Advises') 
    unit_id = fields.Many2one('zbbm.unit',string="Sellable Unit")
    state = fields.Selection(selection_add=[('reserve', 'Reserved'),('book', 'Booked'),('occupied',)])
    lead_id = fields.Many2one('crm.lead',string="Lead")
    reservation_date= fields.Date('Reservation Date')
    reservation_time = fields.Integer('Reservation time', default=default_reservation_time)
    booking_date = fields.Date('Booking Date')
    booking_time = fields.Integer('Booking Time', default=default_reservation_time)
    las_reser = fields.Date('Reservation Ends', compute = 'get_las_reser')
    entry_date = fields.Date('Entry Date')
    feature_arabic = fields.Char('Feature in Arabic')
    is_salesperson = fields.Boolean('')
    management_contract_ids=fields.One2many('owner.management.contract', 'module_id', string='Management Contracts',track_visibility='onchange')
    owner_history_ids = fields.One2many('owner.history','module_id',string="Owner History")

    
    @api.model
    def action_management_invoice_generate(self):
        ''' Scheduler Function for Invoice Generation'''
        context = self._context or {}
        vals = {}
        cron_obj = self.env['ir.cron']
        ir_cron_ids = cron_obj.search([('model_id.model', '=', 'zbbm.module'),('name','=','Management Fees - Invoice')])
        if ir_cron_ids:
            last_date = ir_cron_ids.nextcall.date()
            updated_last_date = datetime.strptime(str(last_date), '%Y-%m-%d')
        module_ids = self.search([('state', '!=', 'delisted'),('managed','=',True),('owner_id','!=',False)])
        
        params = self.env['ir.config_parameter'].sudo()        
        management_fee_journal_id = params.get_param('zb_bf_custom.management_fee_journal_id') or False
        management_product_id = params.get_param('zb_bf_custom.management_product_id') or False
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
#         if not rent_invoice_journal_id:
#             raise Warning(_('Please Configure Rent Invoice Journal'))
    
#         company_id = self.env['res.company']._company_default_get()    
        currnet_user = self.env['res.users'].browse(self._uid)
        company_id = currnet_user.company_id
        
        for module_id in module_ids:
            if not building_income_account_id:
                journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                if journal :
                    acct_id = journal[0].default_credit_account_id.id
            else:
                acct_id = int(building_income_account_id)
            description = 'Management Fee for the Period for the Month '+ updated_last_date.strftime("%B")+' '+ updated_last_date.strftime("%Y")
            params = self.env['ir.config_parameter'].sudo()        
            tax_ids = params.get_param('zb_building_management.default_rental_tax_ids') or False,
            if tax_ids[0]:
                temp = re.findall(r'\d+', tax_ids[0]) 
                tax_list = list(map(int, temp))
            
            product = self.env['product.product'].browse(int(management_product_id))
            
            if module_id.flat_on_offer == True:
                owner_id = config_owner_id
            else:
                owner_id = module_id.owner_id
            
            amt = 0.000
            if module_id.management_fees_percent:
                perc = module_id.management_fees_percent/100
                amt = perc * module_id.monthly_rate
            
                vals = {
                      'partner_id': int(owner_id),
                      'type': 'out_invoice',
                      'invoice_date': last_date,
                      'building_id': module_id.building_id.id,
                      'module_id': module_id.id,
                      'comment': description,
                      'journal_id':int(management_fee_journal_id),
                      'management_fees_boolean':True,
                      'invoice_line_ids': [(0, 0, {
                                            'product_id':int(management_product_id),
                                            'name': description,
                                            'price_unit': amt,
                                            'tax_ids' : product.taxes_id.ids,
                                            'quantity': 1,
                                            'account_analytic_id':module_id.building_id.analytic_account_id.id if module_id.building_id.analytic_account_id else '',
                                            'account_id':product.property_account_income_id.id,
                                            })],
                    }
                invoice_id = self.env.get('account.move').create(vals)
                #NJ for line in invoice_id.line_ids:
                #     if line.credit > 0.000:
                #         line.partner_id = company_id.partner_id.id
                invoice_id.action_post()
                
        return True
    
    @api.model
    def fixed_service_invoice_generate(self):
        ''' Scheduler Function for Fixed Service Invoice Generation'''
        context = self._context or {}
        vals = {}
        cron_obj = self.env['ir.cron']
        ir_cron_ids = self.env.ref('zb_bf_custom.fixed_service_invoice_generation')
        params = self.env['ir.config_parameter'].sudo()
        if ir_cron_ids:
            last_date = ir_cron_ids.nextcall.date()
            updated_last_date = datetime.strptime(str(last_date), '%Y-%m-%d')
        
        today_date = date.today()   
        invoice_generation_days = params.get_param('zb_bf_custom.invoice_generation_days') or 0
        post_date = today_date + timedelta(days=int(invoice_generation_days))  
        module_ids = self.search([('state', '!=', 'delisted')])
        
        service_journal_id=params.get_param('zb_bf_custom.service_invoice_journal_id') or False
        
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        
        invoice_starting_date = params.get_param('zb_bf_custom.invoice_start_date')
        if invoice_starting_date:
            invoice_startdate = datetime.strptime(invoice_starting_date, '%Y-%m-%d').date()
        
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
            
        for module_id in module_ids:
            if module_id.flat_on_offer == True:
                owner_id = config_owner_id
            else:
                owner_id = module_id.owner_id
            
            if module_id.owner_id:
                partner_id = module_id.owner_id.id
            else:
                partner_id=params.get_param('zb_bf_custom.owner_id') or False,
            for agreement in module_id.agreement_ids.filtered(lambda r: r.state == 'active'):
                for line in agreement.invoice_plan_ids:
                    if line.inv_date and invoice_startdate and post_date:
                        if line.inv_date >= invoice_startdate and line.inv_date <= post_date:
                        # if line.inv_date == last_date:
                            
                            fixed_services = agreement.lease_services_ids.filtered(lambda r: r.bill == 'fixed')
                            service_list = []
                            description = 'Fixed service invoice for the Period for the Month '+ updated_last_date.strftime("%Y")+' '+ updated_last_date.strftime("%B")
                            for service in fixed_services:
                                if service.product_id:
                                    service_list.append(({
                                                        'product_id':service.product_id.id, ###9029
                                                        'name':description,
                                                        'price_unit': service.owner_share,
                                                        'quantity': 1,
                                                        'tax_ids' : service.product_id.taxes_id.ids,
                                                        'analytic_account_id':module_id.building_id.analytic_account_id.id if module_id.building_id.analytic_account_id else '',
                                                        'account_id':service.product_id.property_account_income_id,
                                                         }))


                            if fixed_services and service_list:
                                vals = {
                                          'partner_id':int(owner_id),
                                          'type': 'out_invoice',
                                          'invoice_date': line.inv_date,
                                          'building_id': module_id.building_id.id,
                                          'module_id': module_id.id,
                                          'journal_id':int(service_journal_id),
                                          'lease_id':agreement.id,
                                          'invoice_line_ids':[],
                                            }
                                vals.update({'invoice_line_ids':service_list})
                                invoice_id = self.env.get('account.move').create(vals)
                                invoice_id.action_post()
                    
        return True           
    
                    
    
    @api.onchange('building_id')
    def set_managemnt_fees(self):
        for order in self:
            if order.building_id.management_fees_percent:
                order.management_fees_percent = order.building_id.management_fees_percent
            else:
                order.management_fees_percent = 0.00
                
class OwnerManagementContract(models.Model):
    _name = "owner.management.contract"
    _description = "Owner Management Contract"
    
    module_id = fields.Many2one('zbbm.module','Module')
    owner_id = fields.Many2one('res.partner','Owner')
    from_date = fields.Date('Start Date')
    from_date_arabic = fields.Char('From Date Arabic')
    to_date_arabic = fields.Char('To Date Arabic')
    to_date = fields.Date('End Date')
    duration_arabic = fields.Char('Duration Arabic')
    contract_fees = fields.Float('Contract Fees')


class LeaseRentAgreement(models.Model):

    _inherit = 'zbbm.module.lease.rent.agreement'
    _description = "Lease/Rental Agreement"
   
   
   # commented by ansu
    @api.model
    def set_lease_expired(self):
        lease_ids = self.env['zbbm.module.lease.rent.agreement'].search([('agreement_end_date','<',datetime.today()),('state', '=', 'active')])
        for lease in lease_ids:
            lease.set_to_expired()
    
    
    # @api.onchange('state')
    # def terminate(self):
    #     print('expiredddddddddddddddddd')
    #     # if self.state == 'expired':
    #     #     zb_building_management.set_to_terminate()
    #     #
    #     #

   
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(LeaseRentAgreement, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         default_type = self._context.get('default_type', False)
        if self.env.user.has_group('zb_bf_custom.group_property_advisor'):
            managed_report = self.env.ref('zb_bf_custom.report_rent_agreement_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == managed_report.id:
                    res['toolbar']['print'].remove(print_submenu)
                    
        if self.env.user.has_group('zb_bf_custom.group_property_advisor'):
            non_mngd_report = self.env.ref('zb_bf_custom.report_non_managed_lease_agreement')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == non_mngd_report.id:
                    res['toolbar']['print'].remove(print_submenu)
                    
        if self.env.user.has_group('zb_bf_custom.group_property_advisor'):
            sheet_report = self.env.ref('zb_bf_custom.report_lease_agreement_sheet')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == sheet_report.id:
                    res['toolbar']['print'].remove(print_submenu)
                    
        if self.env.user.has_group('zb_bf_custom.group_property_advisor'):
            renewal_report = self.env.ref('zb_bf_custom.report_renewal_agreement_qweb')
            for print_submenu in res.get('toolbar', {}).get('print', []):
                if print_submenu['id'] == renewal_report.id:
                    res['toolbar']['print'].remove(print_submenu)
            
        return res
    
    def set_to_expired(self):
        for rec in self:
            subproperty = rec.subproperty
            subproperty.make_available()
#             subproperty.state = 'available'
            subproperty.sudo().tenant_id = self.tenant_id.id
            rec.state='expired'
            # if rec.voucher_move_id:
            #     if rec.voucher_move_id.state == 'posted':
            #         rec.voucher_move_id.button_draft()
            #         rec.voucher_move_id.button_cancel()
            #     else:
            #         if rec.voucher_move_id.state =='draft':
            #             rec.voucher_move_id.unlink()
            
            
   
   
    def set_to_draft(self):
        for rec in self:
            rec.commission_generated = False
            rec.is_commission = False
            if rec.subproperty:
                subproperty = rec.subproperty
                rec.subproperty.make_available()
#             if subproperty.state == 'occupied':
#                 subproperty.state='available'

            if rec.rent_invoice_id and rec.rent_invoice_id.rent_transfer_id:
                rec.rent_invoice_id.rent_transfer_id.button_draft()
                rec.rent_invoice_id.rent_transfer_id.button_cancel()
                
            if rec.payment_advise_id:
                rec.payment_advise_id.cancel()
            
            if rec.rent_invoice_id and rec.rent_invoice_id.management_fees_move_id:
                rec.rent_invoice_id.management_fees_move_id.button_draft()
                rec.rent_invoice_id.management_fees_move_id.button_cancel()
                
            if rec.invoice_plan_ids:
                for line in rec.invoice_plan_ids:
                    line.unlink()
            
            
            if rec.rent_invoice_id:
                if rec.rent_invoice_id.state == 'posted' and rec.rent_invoice_id.amount_residual == rec.rent_invoice_id.amount_total:
                    rec.rent_invoice_id.button_draft()
                    rec.rent_invoice_id.button_cancel()
                    rec.state = 'draft'
                elif rec.rent_invoice_id.state=='posted' and rec.rent_invoice_id.amount_residual != rec.rent_invoice_id.amount_total:
                    raise Warning(_('Rent Invoice is Partially/Fully Paid'))
                else:
                    if rec.rent_invoice_id.state =='draft':
                        rec.rent_invoice_id.button_cancel()
                        rec.state = 'draft'
            else:
                rec.state='draft'
            
            
# DB            if rec.vendor_id:
#                 if rec.vendor_id.state == 'posted' and rec.vendor_id.amount_residual == rec.vendor_id.amount_total:
#                     rec.vendor_id.state = 'cancel'
#                     rec.state='draft'
#                 elif rec.vendor_id.state=='posted' and rec.vendor_id.amount_residual != rec.vendor_id.amount_total:
#                     raise Warning(_('Agent Vendor Bill is Partially/Fully Paid'))
#                 else:
#                     if rec.vendor_id.state =='draft':
#                         rec.vendor_id.button_cancel()
#                         rec.state='draft'
#             else:
#                 rec.state='draft'

            
            if rec.vendor_id:
                if rec.vendor_id.state == 'posted':
                    rec.vendor_id.state = 'cancel'
                    rec.state='draft'
                else:
                    if rec.vendor_id.state =='draft':
                        rec.vendor_id.button_cancel()
                        rec.state='draft'
            else:
                rec.state='draft'
                
                 
            if rec.vendor_refund_id:
                if rec.vendor_refund_id.state == 'posted' and rec.vendor_refund_id.amount_residual == rec.vendor_refund_id.amount_total:
                    rec.vendor_refund_id.state = 'cancel'
                    rec.state='draft'
                elif rec.vendor_refund_id.state=='posted' and rec.vendor_refund_id.amount_residual != rec.vendor_refund_id.amount_total:
                    raise Warning(_('Agent Commission is Partially/Fully Paid'))
                else:
                    if rec.vendor_refund_id.state =='draft':
                        rec.vendor_refund_id.button_cancel()
                        rec.state='draft'
            else:
                rec.state='draft'
             
             
            if rec.voucher_move_id:
                if rec.voucher_move_id.state == 'posted' and rec.voucher_move_id.amount_residual == rec.voucher_move_id.amount_total:
                    rec.voucher_move_id.button_draft()
                    rec.voucher_move_id.button_cancel()
                    rec.state = 'draft'
                elif rec.voucher_move_id.state=='posted' and rec.voucher_move_id.amount_residual != rec.voucher_move_id.amount_total:
                    raise Warning(_('Receipt is Partially/Fully Paid'))
                else:
                    if rec.voucher_move_id.state =='draft':
                        rec.voucher_move_id.button_cancel()
                        rec.state = 'draft'
            else:
                rec.state='draft'
                 
             
            if rec.commission_move_id:
                if rec.commission_move_id.state == 'posted' and rec.commission_move_id.amount_residual == rec.commission_move_id.amount_total:
                    rec.commission_move_id.button_draft()
                    rec.commission_move_id.button_cancel()
                    rec.state = 'draft'
                elif rec.commission_move_id.state=='posted' and rec.commission_move_id.amount_residual != rec.commission_move_id.amount_total:
                    raise Warning(_('Commission Entry is Partially/Fully Paid'))
                else:
                    if rec.commission_move_id.state =='draft':
                        rec.commission_move_id.button_cancel()
                        rec.state = 'draft'
            else:
                rec.state='draft'
                 
            
            
            if rec.management_move_id:
                if rec.management_move_id.state == 'posted' and rec.management_move_id.amount_residual == rec.management_move_id.amount_total:
                    rec.management_move_id.button_draft()
                    rec.management_move_id.button_cancel()
                    rec.state = 'draft'
                elif rec.management_move_id.state=='posted' and rec.management_move_id.amount_residual != rec.management_move_id.amount_total:
                    raise Warning(_('Commission Entry is Partially/Fully Paid'))
                else:
                    if rec.management_move_id.state =='draft':
                        rec.management_move_id.button_cancel()
                        rec.state = 'draft'
            else:
                rec.state='draft'
            
            
                
            
            
                

        
   
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.move'].search([('state','=','posted'),('lease_id','=',self.id),('type','=','out_invoice')])
            order.invoices_count = len(invoices) 
             
    
    def _compute_jv(self):
        
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids += self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        
        for order in self:
            invoices = self.env['account.move'].search([('state','=','posted'),('journal_id','not in',journal_ids),('lease_id','=',self.id),('type','=','entry')])
            order.jv_count = len(invoices) 
            
    
    def _compute_payment_advises(self):
        for order in self:
            payment_ids = self.env['account.payment'].search([('lease_id','=',self.id),('payment_type','=','outbound'),('payment_advise','=',True)])
            order.payment_advise_count = len(payment_ids)
            
    def _compute_receipts_count(self):
        for order in self:
            payment_ids = self.env['account.payment'].search([('lease_id','=',self.id),('payment_type','=','inbound')])
            order.receipts_count = len(payment_ids)
            
    def _compute_payments_count(self):
        for order in self:
            payment_ids = self.env['account.payment'].search([('lease_id','=',self.id),('payment_type','=','outbound'),('payment_advise','=',False)])
            order.payments_count = len(payment_ids) 
            
    def _compute_owner_inv_count(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        for order in self:
            move_ids = self.env['account.move'].search([('lease_id','=',self.id),('type','in',('out_invoice','out_refund')),('journal_id','in',journal_ids)])
            order.owner_inv_count = len(move_ids) 
            
    def _compute_rs_inv_count(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        for order in self:
            move_ids = self.env['account.move'].search([('lease_id','=',self.id),('type','in',('out_invoice','out_refund')),('journal_id','in',journal_ids)])
            order.rs_inv_count = len(move_ids) 
            
    def _compute_rs_exp_count(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        for order in self:
            move_ids = self.env['account.move'].search([('lease_id','=',self.id),('type','in',('in_invoice','in_refund')),('journal_id','in',journal_ids)])
            order.rs_exp_count = len(move_ids) 
            
    def _compute_owner_exp_count(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        for order in self:
            move_ids = self.env['account.move'].search([('lease_id','=',self.id),('type','in',('in_invoice','in_refund')),('journal_id','in',journal_ids)])
            order.owner_exp_count = len(move_ids) 
             
    
    def get_invoices(self):  
        for order in self:
            invoices = self.env['account.move'].search([('state','=','posted'),('lease_id','=',self.id),('type','in',['in_invoice','in_refund'])])
            order.expenses_count = len(invoices)
             
             
    def action_view_invoice(self):
        invoices = self.env['account.move'].search([('state','=','posted'),('lease_id','=',self.id),('type','=','out_invoice')])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
     
 
    def action_view_expense(self):
        invoices = self.env['account.move'].search([('state','=','posted'),('lease_id','=',self.id),('type','in',['in_invoice','in_refund'])])
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_view_receipts(self):
        receipts = self.env['account.payment'].search([('lease_id','=',self.id),('payment_type','in',['inbound'])])
        action = self.env.ref('account.action_account_payments').read()[0]
        if len(receipts) > 1:
            action['domain'] = [('id', 'in', receipts.ids)]
        elif len(receipts) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = receipts.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_view_payments(self):
        payments = self.env['account.payment'].search([('lease_id','=',self.id),('payment_type','in',['outbound'])])
        action = self.env.ref('account.action_account_payments_payable').read()[0]
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = payments.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action   
    
    
    def action_view_jv(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids += self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        
        invoices = self.env['account.move'].search([('state','=','posted'),('journal_id','not in',journal_ids),('lease_id','=',self.id)])
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action 
    
    def action_view_owner_inv(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        invoices = self.env['account.move'].search([('lease_id','=',self.id),('type','in',('out_invoice','out_refund','entry')),('journal_id','in',journal_ids)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_account_move_inherit_zb').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_view_owner_expense(self):
        params = self.env['ir.config_parameter'].sudo()
        owner_journal_ids = params.get_param('zb_bf_custom.owner_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(owner_journal_ids)
        invoices = self.env['account.move'].search([('lease_id','=',self.id),('type','in',('in_invoice','in_refund','entry')),('journal_id','in',journal_ids)])
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]        
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_account_move_inherit_zb').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def action_view_rs_inv(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        invoices = self.env['account.move'].search([('lease_id','=',self.id),('type','in',('out_invoice','out_refund','entry')),('journal_id','in',journal_ids)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_account_move_inherit_zb').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action  
    
    def action_view_rs_expense(self):
        params = self.env['ir.config_parameter'].sudo()
        rs_journal_ids = params.get_param('zb_bf_custom.rs_in_exp_type_ids')
        journal_ids = self.env['account.move'].get_acc_type_ids(rs_journal_ids)
        invoices = self.env['account.move'].search([('lease_id','=',self.id),('type','in',('in_invoice','in_refund','entry')),('journal_id','in',journal_ids)])
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]        
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('zb_building_management.view_account_move_inherit_zb').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action  
    
    
    def action_view_payment_advises(self):
        invoices = self.env['account.payment'].search([('lease_id','=',self.id),('payment_type','=','outbound'),('payment_advise','=',True)])
        action = self.env.ref('account.action_account_payments').read()[0]
        action['context'] = {'default_payment_advise': 'True',
                'default_partner_type': 'customer',
                'search_default_inbound_filter': 1,
                'res_partner_search_mode': 'customer',}
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action  
    

    @api.model
    def action_invoice_generate(self):
        
        ''' Scheduler Function for Invoice Generation'''
        context = self._context or {}
        vals = {}
        cron_obj = self.env['ir.cron']
        # ir_cron_ids = cron_obj.search([('model_id.model', '=', 'zbbm.module.lease.rent.agreement')])
        ir_cron_ids = self.env.ref('zb_building_management.agreement_make_invoices')
        last_date = ""
        params = self.env['ir.config_parameter'].sudo()   
        
        invoice_generation_days = params.get_param('zb_bf_custom.invoice_generation_days') or 0
        invoice_generation_date = params.get_param('zb_bf_custom.invoice_generation_date')
        invoice_starting_date = params.get_param('zb_bf_custom.invoice_start_date')
        if invoice_starting_date:
            invoice_startdate = datetime.strptime(invoice_starting_date, '%Y-%m-%d').date()
        
        if invoice_generation_date:
            invoice_date = datetime.strptime(invoice_generation_date, '%Y-%m-%d').date()
        
        if ir_cron_ids:
            last_date = ir_cron_ids.nextcall.date()
            updated_last_date = datetime.strptime(str(last_date), '%Y-%m-%d')
        agreement_ids = self.search([('state', '=', 'active')])
        
        today_date = date.today()
        
        post_date = today_date + timedelta(days=int(invoice_generation_days))  
        updated_last_date = datetime.strptime(str(post_date), '%Y-%m-%d')
        
            
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        
        rent_invoice_product_id = params.get_param('zb_bf_custom.rent_invoice_product_id') or False
        if not rent_invoice_product_id:
            raise Warning(_('Please Configure Rent Invoice Product'))
        
        product = self.env['product.product'].browse(int(rent_invoice_product_id))
        lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
        date_format = lang_id.date_format
        
#         if not rent_invoice_journal_id:
#             raise Warning(_('Please Configure Rent Invoice Journal'))
        
        for agreement in agreement_ids:
            for line in agreement.invoice_plan_ids:
#                 if line.inv_date == post_date and not line.move_id:
                if line.inv_date and invoice_startdate and post_date:
                    if line.inv_date >= invoice_startdate and line.inv_date <= post_date and not line.move_id:
                    # line.inv_date<=invoice_date 
                    #if line.inv_date <= invoice_date and not line.move_id:  
                        formatted_from_date = datetime.strptime(str(line.inv_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                        from_date = line.inv_date
                        to_date = from_date + relativedelta(days=-1,months=agreement.invoice_cycle_num)
                        formatted_to_date = datetime.strptime(str(to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                        updated_last_date = datetime.strptime(str(from_date), '%Y-%m-%d')
                        
                        if not building_income_account_id:
                            journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                            if journal :
                                acct_id = journal[0].default_credit_account_id.id
                        else:
                            acct_id = int(building_income_account_id)
                        description = 'Rent for the Period from %s to %s'%(formatted_from_date,formatted_to_date)
                        params = self.env['ir.config_parameter'].sudo()        
                        tax_ids = params.get_param('zb_building_management.default_rental_tax_ids') or False,
                        if tax_ids[0]:
                            temp = re.findall(r'\d+', tax_ids[0]) 
                            tax_list = list(map(int, temp))
                        vals = {
                              'partner_id': agreement.tenant_id.id,
                              'type': 'out_invoice',
                              'invoice_date': line.inv_date,
                              'from_date':line.inv_date,
                              'to_date':to_date,
                              'building_id': agreement.building_id.id,
                              'module_id': agreement.subproperty.id,
                              'lease_id': agreement.id,
                              'journal_id':int(rent_invoice_journal_id),
                              'invoice_line_ids': [(0, 0, {
                                                    'product_id':int(rent_invoice_product_id),
                                                    'name': description,
                                                    'price_unit': line.amount,
                                                    'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
                                                    'quantity': 1,
                                                    'account_analytic_id':agreement.building_id.analytic_account_id.id if agreement.building_id.analytic_account_id else '',
                                                    'account_id': product.property_account_income_id and product.property_account_income_id.id or acct_id,
                                                    })],
                            }
                        invoice_id = self.env.get('account.move').create(vals)
                        invoice_id.action_post()
                        line.move_id = invoice_id.id
                        _logger.info("Invoice %s: %s to %s : %s belongs to flat %s,building %s",invoice_id.id,invoice_id.name,invoice_id.partner_id.id,invoice_id.partner_id.email,invoice_id.module_id.name,invoice_id.building_id.name)
                        self._cr.commit()
                    
            
                    
                    
#                     if agreement.subproperty.managed:
#                         management_fee_journal_id = params.get_param('zb_bf_custom.management_fee_journal_id') or False
#                         if not management_fee_journal_id:
#                             raise Warning(_('Please Configure Management Fee Journal'))
#                         
#                         management_product_id = params.get_param('zb_bf_custom.management_product_id') or False
#                         if not management_product_id:
#                             raise Warning(_('Please Configure Management Product'))
#                         
#                         management_inv_vals = {
#                                 'partner_id': agreement.tenant_id.id,
#                                 'type': 'entry',
#                                 'invoice_date':last_date,
#                                 'module_id': agreement.subproperty.id,
#                                 'building_id':agreement.subproperty.building_id and agreement.subproperty.building_id.id,
#                                 'lease_id':agreement.id,
#                                 'journal_id':int(management_fee_journal_id),
#                                 'invoice_line_ids': [(0, 0, {
#                                                             'product_id':int(management_product_id),
#                                                             'name': 'Management Fees:{}  to {}, Tenant:{}'.format(agreement.building_id.name,agreement.subproperty.name,agreement.tenant_id.name),
#                                                             'price_unit': agreement.management_fees,
#                                                             'quantity': 1,
#             #                                                 'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
#                                                             'analytic_account_id':agreement.building_id.analytic_account_id.id if agreement.building_id.analytic_account_id else '',
#                                                             'account_id': acct_id,
#                                                              })],
#                                 }
#                         management_inv_id = self.env['account.move'].create(management_inv_vals)
#                         agreement.management_move_id = management_inv_id.id
#                         management_inv_id.action_post()
#                         
#                         
#                         managemnet_line = agreement.invoice_plan_ids.filtered(lambda r: r.inv_date == management_inv_id.invoice_date and r.management_boolean)
#                         if managemnet_line:
#                             managemnet_line.move_id = management_inv_id.id
#                         else:
#                             management_inv_list = []
#                             management_invoice_plan_dict = {
#                                                 'inv_date':self.start_date,
#                                                 'amount': agreement.management_fees,
#                                                 'move_id':management_inv_id.id,
#                                                 'management_boolean':True,
#                                                }
#                             management_inv_list.append((0,0,management_invoice_plan_dict))
#                             agreement.write({'invoice_plan_ids': management_inv_list})
#      
        return True  

    
    def _attachment_count(self):
        '''Function to get count of attachments from Agreement.
        '''
        attachment_ids = self.env.get('ir.attachment').search([('agreement_id','=',self.id)])
        for agreement in self:
            if attachment_ids:
                agreement.attachment_count = len(attachment_ids)
            else:
                agreement.attachment_count = 0
      
      
    def view_attach_from_agreement(self):
        model, action_id = self.env.get('ir.model.data').get_object_reference('base', 'action_attachment')
        action = self.env.ref('base.action_attachment')
        agreement = []
        agreement_ids = self.env.get('ir.attachment').search([('agreement_id','=',self.id)])
        for idss in agreement_ids:
            agreement.append(idss.id)
        result = {
            'name': action.name,
            'type': action.type,
            'view_mode': action.view_mode,
            'target': 'current',
            'res_model': action.res_model,
            'domain':[('id', 'in',agreement)],
            'context' : {'default_agreement_id' : self.id},
            'help': "Click here to create new documents."
        }
        
#         agreement_ids = sum([agreement_ids.ids], [])
#         result['res_id'] = agreement_ids
#         result['domain'] = str([('id','in',agreement_ids)])
#         if len(agreement_ids) == 1:
#             result['res_id'] = agreement_ids[0]
#         else:
#             result['domain'] = str([('id','in',agreement_ids)])
        return result


    @api.onchange('subproperty','agreement_start_date')
    def property_change(self):
        print('===============property_change=============')
        params = self.env['ir.config_parameter'].sudo()    
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
        for order in self:
            if order.agreement_start_date:
                if order.subproperty.offer_start_date and order.subproperty.offer_end_date:
                    if order.agreement_start_date >= order.subproperty.offer_start_date and order.agreement_start_date <= order.subproperty.offer_end_date:
                        order.owner_id = int(config_owner_id)
                    else:
                        order.owner_id = order.subproperty.owner_id.id
                else:
                    order.owner_id = order.subproperty.owner_id.id
            # order.owner_id = order.subproperty.owner_id.id
            order.security_deposit = order.subproperty.deposit
            order.managed = order.subproperty.managed
            self.with_context(new_lease = True).set_service()
#             order.potential_rent = order.subproperty.potential_rent
#             

    def set_service(self):
        lease_service = []
#         for order in self:
        # if self.subproperty:
        service_ids = ''
        module = self.subproperty.id
        building = self.building_id.id
        if self._context.get('renew')=='make_renew':
            if self.lease_services_ids:
                
                service_ids = self.lease_services_ids
                
        else:
            module = self.subproperty.id
            building = self.building_id.id
            service_ids = self.subproperty.service_ids
        if service_ids:
            for serv in service_ids:
                value = {
                    'product_id':int(serv.product_id),
                    'package_name':serv.package_name,
                    'account_no':serv.account_no,
                    'bill':serv.bill,
                    'managed_by_rs':serv.managed_by_rs,
                    'owner_share':serv.owner_share,
                    'tenant_share':serv.tenant_share,
                    'from_date':serv.from_date,
                    'to_date':serv.to_date,
                    'initial_connection_date':serv.initial_connection_date,
                    'module_id':module,
                    'building_id':building,
                    'lease_id':self.id
                    }
                    
                lease_service.append((0,0,value))
        
        self.lease_services_ids = [(6, 0, [])]
        self.write({'lease_services_ids':lease_service}) 
    
    @api.model
    def create(self,vals):
        res = super(LeaseRentAgreement,self).create(vals)
        if self.subproperty:
            self.set_service()
        if vals.get('crm_lead_id'):
            lead = self.env.get('crm.lead').browse(vals.get('crm_lead_id'))
            module_ids = self.env.get('zbbm.module').search([('id','=',lead.module_id.id),('building_id','=',lead.building_id.id)])
            if module_ids:  
                module_ids.sudo().write({
                              'state':'book',
                              'lead_id':lead.id,
                              'reservation_time':0,
                              'user_id':lead.user_id.id
                                 })
            
            if  lead._context.get('booked') == 'make_open':
                module_ids.sudo().message_post(body=_(' {} booked  on {}').format(lead.partner_id.name,datetime.today()))
            stage = self.env['crm.stage'].search([('probability','=',70),('name','=','Booked')])
            if stage:
                lead.stage_id = stage.id
                lead.probability = stage.probability
                lead.store_prob = stage.probability
        return res
    
    
    # def write(self,vals):
    #     self.set_service(vals)
    #     return super(LeaseRentAgreement,self).write(vals)
    
    
    @api.depends('management_fees_percent','monthly_rent')
    def compute_management_fee(self):
        amt = 0.00
        for order in self:
            if order.management_fees_percent:
                perc = order.management_fees_percent/100
                amt = perc * order.monthly_rent
            order.management_fees = amt
            
    @api.depends('monthly_rent','moving_date')
    def _compute_pro_rate_amount(self):
        pro_amt = 0.00
        pro_rent_days = 0
        for order in self:
            if order.moving_date:
                pro_rent_days = (datetime.strptime(str(order.agreement_start_date), '%Y-%m-%d')-datetime.strptime(str(order.moving_date), '%Y-%m-%d')).days
            if order.monthly_rent:
                pro_amt = (order.monthly_rent/30)*pro_rent_days
            order.pro_rated_amt = pro_amt
            
    @api.depends('monthly_rent')
    def _compute_pro_rent(self):
        pro_rent = 0.00
        for order in self:
            if order.monthly_rent:
                pro_rent = (order.monthly_rent/30)
            order.pro_rent = pro_rent
    
    
    @api.onchange('total_commission_percent','monthly_rent','agreement_start_date','agreement_end_date','building_id','subproperty','commission_percent')
    def calculate_commission(self):
        ownr_commission = 0.000
        commission = 0.000
        for agreement in self:
            if agreement.agreement_start_date and agreement.agreement_end_date:
                total_days = (datetime.strptime(str(agreement.agreement_end_date), '%Y-%m-%d')-datetime.strptime(str(agreement.agreement_start_date), '%Y-%m-%d')).days+1
                print('==========total_days=================',total_days)
                print('==========total_days1=================',round(total_days/30))
                actual_total_days = (math.floor(total_days/30)*30)
                print('==========actual_total_days===============',actual_total_days)
                total_days_year = 30*12
                if not agreement.total_commission_percent and agreement.commission_percent:
                    if actual_total_days >= total_days_year:
                        commission = agreement.monthly_rent *(agreement.commission_percent/100)
                    else:
                        commission = (agreement.monthly_rent *(agreement.commission_percent/100))/total_days_year * actual_total_days     
                else:
                    if agreement.total_commission_percent and agreement.commission_percent:
                        rs_commission = agreement.commission_percent *(agreement.total_commission_percent/100)
                        if actual_total_days >= total_days_year:
                            commission = agreement.monthly_rent *(rs_commission/100)
                        else:
                            commission = (agreement.monthly_rent *(rs_commission/100))/total_days_year * actual_total_days  
                            
                if agreement.total_commission_percent:
                    if actual_total_days >= total_days_year:
                        ownr_commission = agreement.monthly_rent *(agreement.total_commission_percent/100)
                    else:
                        ownr_commission = (agreement.monthly_rent *(agreement.total_commission_percent/100))/total_days_year * actual_total_days  
            agreement.commission_percent_amount = ownr_commission
            agreement.agent_commission_amount = commission
    
    
    def check_services(self,service):
        params = self.env['ir.config_parameter'].sudo()           
        ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id') or False
        internet_product_id = params.get_param('zb_bf_custom.internet_product_id') or False
        osn_product_id = params.get_param('zb_bf_custom.osn_product_id') or False
        tabreed_product_id = params.get_param('zb_bf_custom.tabreed_product_id') or False
        if service == 'EWA':
            service_id = self.lease_services_ids.filtered(lambda r: r.product_id.id == int(ewa_product_id))
        elif service == 'Internet':
            service_id = self.lease_services_ids.filtered(lambda r: r.product_id.id == int(internet_product_id))
        elif service == 'OSN':
            service_id = self.lease_services_ids.filtered(lambda r: r.product_id.id == int(osn_product_id))
        elif service == 'Housekeeping':
            service_id = self.lease_services_ids.filtered(lambda r: r.product_id.id == int(tabreed_product_id))
        if service_id:
            return True
        else:
            return False
    
    def set_to_approved(self):
        if not self.user_has_groups('sales_team.group_sale_manager'):
            if not self.user_has_groups('base.group_user'):
                raise Warning(_('Only Sales manager or Admin  is allowed to Approve'))
        self.state = 'approved'
        if self.crm_lead_id:
            stage = self.env['crm.stage'].search([('probability','=',90)])
            self.crm_lead_id.stage_id = stage.id
    
    
    def action_set_renew(self):
        today = datetime.today()
        end = self.agreement_end_date
        end_day_obj = datetime.strptime(str(end), "%Y-%m-%d")
        new_date = end_day_obj + relativedelta(days=1)
        end_date = self.agreement_end_date
        new_end_day_obj = datetime.strptime(str(end_date), "%Y-%m-%d")
        new_end_date = new_date + relativedelta(years=1,days=-1)   
        vals={

            'tenant_id' : self.tenant_id.id,
            'building_id': self.building_id.id,
            'subproperty' : self.subproperty.id,
            'monthly_rent': self.monthly_rent,
            'ewa_limit' :self.ewa_limit,
            'agent' : self.agent.id,
            'invoice_date' : self.invoice_date,
            'agreement_start_date' : new_date,
            'agreement_end_date' : new_end_date,
            'contract_status' : 'no_contract',
            'renewed_lease_agreement_id':self.id,
            }

        view_id = self.env.ref('zb_building_management.view_lease_rent_agreement_form').id 
        context = self._context
        res = self.copy(vals)
        if self.state == 'expired':
            self.set_to_terminate()
        # super(LeaseRentAgreement,res).write(vals)
        # res.set_service(vals)
        return {'name':'view_lease_rent_agreement_form', 
                'view_type':'form', 
                'view_mode':'tree', 
                'views' : [(view_id,'form')], 
                'res_model':'zbbm.module.lease.rent.agreement', 
                'view_id':view_id, 
                'type':'ir.actions.act_window', 
                'res_id':res.id, 
                'target':'current', 
                'context' :context
                }

    
            
#     def _is_area_manager(self):
#         for rec in self:
#             if rec.env.user == rec.building_id.area_manager:
#                 rec.is_area_manager = True
#             else:
#                 rec.is_area_manager = False
                
    def send_for_approval(self):
        self.state = 'approval_waiting'
        
    @api.onchange('building_id')
    def assign_commision(self):
        for order in self:
            if order.building_id.commission_percent:
                order.commission_percent = order.building_id.commission_percent
            else:
                order.commission_percent = 0
            
            if order.building_id.area_manager:
                order.area_manager = order.building_id.area_manager.id
            else:
                order.area_manager = False
        

    invoice_cycle_num=fields.Integer(string='Invoice Cycle No.',required=True,default='1') 
    invoice_cycle=fields.Selection([
        ('months','Monthly'),
        ],default='months')
    adviser_id=fields.Many2one('res.users',string="Property Advisor",default=lambda self: self.env.uid)
    owner_id=fields.Many2one('res.partner','Owner')
    subproperty = fields.Many2one('zbbm.module', 'Unit')
    attachment_count  = fields.Integer(compute ='_attachment_count',string='Attachments') 
    invoice_plan_ids = fields.One2many('invoice.plan','lease_agreement_id',string="Invoice Plan")
    services_ids = fields.One2many('zbbm.services','lease_agreement_id',string="Services",track_visibility='onchange')
    raw_service_ids = fields.One2many('raw.services','lease_agreement_id',string="Services")
    management_fees_percent = fields.Float(string="Management Fees(%)",related="building_id.management_fees_percent")
    management_fees = fields.Float(string="Management Fee",digits = (12,3),compute="compute_management_fee")
    voucher_move_id = fields.Many2one('account.move',string="Receipt Id",copy=False)
    service_move_id = fields.Many2one('account.move',string="Owner/Tenant/Invoice",copy=False)
    commission_move_id = fields.Many2one('account.move',string="Commission Entry",copy=False)
    rent_invoice_id = fields.Many2one('account.move',string="Rent Tenant Invoice",copy=False)
    remarks = fields.Char(string="Remarks",copy=False)
    total_commission_percent = fields.Float(string="Total Commission Percent")
    # related="building_id.total_commission_percent"
    notes = fields.Text(string="Notes",copy=False)
    management_move_id = fields.Many2one('account.move',string="Management Fees Entry",copy=False)
    commission_percent_amount = fields.Float(string="Total Commission Amount",digits = (12,3),track_visibility='always')
    agent_commission_amount = fields.Float(string="Agent Commission Amount",digits = (12,3),copy=False)
    ref_person_id = fields.Many2one('res.partner','Reference Person Name',copy=False)
    prep_priority=fields.Selection([
        ('3 hours','3 Hours'),
        ('1 day','1 Day'),
        ('2 days','2 Days')
        ],string="Preparation Priority",copy=False)
#     agent_commission = fields.Float(string="Agent Commission")
    jv_count = fields.Integer(compute='_compute_jv',string='Journal Entry Counts') 
    payment_advise_count = fields.Integer(compute='_compute_payment_advises',string='Payment Advises') 
    payments_ids = fields.One2many('account.payment', 'lease_id', 'Payments')
    receipt_ids = fields.One2many('account.payment', 'lease_id', 'Receipts')
    owner_inv_count = fields.Integer(compute='_compute_owner_inv_count',string='Owner Invoices') 
    rs_inv_count = fields.Integer(compute='_compute_rs_inv_count',string='Real search Invoices')
    owner_exp_count = fields.Integer(compute='_compute_owner_exp_count',string='Owner Expenses') 
    rs_exp_count = fields.Integer(compute='_compute_rs_exp_count',string='Real search Expenses') 
    receipts_count = fields.Integer(compute='_compute_receipts_count',string='Receipts') 
    payments_count = fields.Integer(compute='_compute_payments_count',string='Payments') 
    moving_date = fields.Date('Move In Date')
    payment_advise_id = fields.Many2one('account.payment',string="Payment Advise")
    payment_id = fields.Many2one('account.payment',string="Payment")
    lead_id= fields.Many2one('activity.details',string="Lead")
    commission_generated = fields.Boolean(string="Commission Generated")
    managed = fields.Boolean(string="Managed")
    state = fields.Selection(selection_add=[('approval_waiting', 'Waiting For Approval'),
                                            ('approved', 'Approved'),('active',)])
#     is_area_manager = fields.Boolean('Is Area Manager',compute='_is_area_manager')
    potential_rent = fields.Float(string='Potential Rent',digits='Product Price',related="subproperty.potential_rent")
    
    renewed_lease_agreement_id= fields.Many2one('zbbm.module.lease.rent.agreement',string="Renewed lease Agreement")
    # commented by ansu
    security_deposit = fields.Float(string='Security Deposit ',digits = (12,3),copy=False)
    advance = fields.Char(string='Advance')
    
    security_deposit_arabic = fields.Char('Security Deposit Arabic')
    monthly_rent_arabic = fields.Char('Monthly Rent Arabic')
 
    leasedpremise_rent_arabic = fields.Char('Leased Premise Rent Arabic')
    pro_rated_amt = fields.Float(string='Pro Rated Amount',digits='Product Price',copy=False,compute='_compute_pro_rate_amount')
    advance_pay_mnth = fields.Integer(string='Advance payment month',copy=False)
    pro_rated_amt_arabic = fields.Char('Pro Rated Amount Arabic')
    crm_lead_id= fields.Many2one('crm.lead',string="CRM Lead")
    start_date_arabic = fields.Char('Start date in Arabic')
    end_date_arabic = fields.Char('End date in Arabic')
    lease_services_ids = fields.One2many('zbbm.services.agreement','lease_id',string="Services",track_visibility='onchange',copy=True)
    handover_date_arabic = fields.Char('Handover date in Arabic')
    pro_rent = fields.Float(string='Prorated Rent',digits='Product Price',copy=False,compute='_compute_pro_rent')
    pro_rent_arabic = fields.Char('Prorated Rent Arabic')
    prorata_payment_date = fields.Date('Pro Rata Payment Date',copy=False)
    duration_arabic = fields.Char('Duration Arabic',copy=False)
    is_commission = fields.Boolean('Is Commission',default=False,copy=False)
    municipality_tax = fields.Boolean('Municipality Tax',default=False)
    tax_municipality = fields.Selection([
        ('lessor','By Lessor'),
        ('lessee','By Lessee'),
        ],string="Municipality Tax")
    area_manager = fields.Many2one('res.users',string="Area Manager")
    campaign_id = fields.Many2one('utm.campaign',string="Campaign")
    source_id = fields.Many2one('utm.source',string="Source")
    
class zbbm_unit(models.Model):
    _inherit = 'zbbm.unit'
    
    
#     def make_booked(self):
#         params = self.env['ir.config_parameter'].sudo()    
# 
#         resale_commission_journal_id = params.get_param('zb_bf_custom.resale_commission_journal_id') or False
#         resale_commission_product_id = params.get_param('zb_bf_custom.resale_commission_product_id') or False
#         
#         if not resale_commission_journal_id:
#             raise Warning(_('Please Configure Resale Commisiion Journal'))
#         
#         if not resale_commission_product_id:
#             raise Warning(_('Please Configure Resale Commisiion Product'))
#         
#         product = self.env['product.product'].browse(int(resale_commission_product_id))
#         
#         config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
#         if not config_owner_id:
#             raise Warning(_('Please Configure Owner'))
#         
#         for items in self:
#             items.state = 'book'
#             
#             description = 'Resale Commission for the Owner '+ str(items.owner_id.name) if items.owner_id else ''
# 
#             
#             vals = {
#                   'partner_id': items.owner_id.id if items.owner_id else int(config_owner_id),
#                   'type': 'out_invoice',
#                   'invoice_date': datetime.today(),
#                   'from_date':datetime.today(),
#                   'to_date':datetime.today(),
#                   'building_id': items.building_id.id,
#                   'unit_id':items.id,
# #                   'module_id': line.move_id.module_id.id,
# #                   'lease_id':line.move_id.lease_id.id,
#                   'comment': description,
#                   'journal_id':int(resale_commission_journal_id),
#                   'invoice_line_ids': [(0, 0, {
#                                         'product_id':int(resale_commission_product_id),
#                                         'name': description,
#                                         'price_unit': items.resale_commission_amount,
#                                         'tax_ids' : product.taxes_id.ids,
#                                         'quantity': 1,
#                                         'account_analytic_id':items.building_id.analytic_account_id.id if items.building_id.analytic_account_id else '',
#                                         'account_id':product.property_account_income_id.id,
#                                         })],
#                 }
#             if items.resale_commission_amount > 0:
#                 resale_commission_inv_id = self.env['account.move'].create(vals)
#                 resale_commission_inv_id.action_post()
#                 items.resale_move_id = resale_commission_inv_id.id
    
    @api.model  
    def default_booking_time(self):
        '''
            Default getting of reservation time from configuration 
        '''
        params = self.env['ir.config_parameter'].sudo()
        default_booking_time = params.get_param('zb_building_management.reservation_time') or 0.0
        return default_booking_time
    
    @api.onchange('building_id','price','building_id.resale_buyer_commission_percent','building_id.resale_owner_commission_percent','building_id.resale_agent_commission_percent')
    def resale_commission(self):
        for order in self:
#             if order.building_id and order.building_id.resale_commission_percent:
#                 resale_commission_percent = order.building_id.resale_commission_percent
#                 resale_amount = order.price * (resale_commission_percent/100)
#             else:
#                 resale_amount = 0.00
            
            if order.building_id and order.building_id.resale_owner_commission_percent:
                resale_owner_commission_percent = order.building_id.resale_owner_commission_percent
                resale_owner_amount = order.price * (resale_owner_commission_percent/100)
            else:
                resale_owner_amount = 0.00
                
            if order.building_id and order.building_id.resale_buyer_commission_percent:
                resale_buyer_commission_percent = order.building_id.resale_buyer_commission_percent
                resale_buyer_amount = order.price * (resale_buyer_commission_percent/100)
            else:
                resale_buyer_amount = 0.00
                
            if order.building_id and order.building_id.resale_agent_commission_percent:
                resale_agent_commission_percent = order.building_id.resale_agent_commission_percent
                resale_agent_amount = order.price * (resale_agent_commission_percent/100)
            else:
                resale_agent_amount = 0.00
             
#             order.resale_commission_amount = resale_amount
            order.resale_owner_commission = resale_owner_amount
            order.resale_buyer_commission = resale_buyer_amount
            order.resale_agent_commission = resale_agent_amount
            
            
    def _compute_jv(self):
        for order in self:
            invoices = self.env['account.move'].search([('state','=','posted'),('unit_id','=',self.id),('type','=','entry')])
            order.jv_count = len(invoices) 
            
    
    def action_view_jv(self):
        params = self.env['ir.config_parameter'].sudo()
        
        invoices = self.env['account.move'].search([('state','=','posted'),('unit_id','=',self.id),('type','=','entry')])
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action 
    
    
    @api.depends('invoice_ids1','invoice_ids1.state','invoice_total','balance_invoice','balance_total')
    def get_state(self):
        for flat in self:
            lead = self.env['crm.lead'].search([('unit_id','=',flat.id)])
            stage = self.env['crm.stage'].search([('probability','=',90)])
            deal =  self.env['crm.stage'].search([('probability','=',100)])
            journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
            if flat.booking_fee_payment == 'installment':
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
    
    
    def state_change(self):
        
        for flat in self:
            lead = self.env['crm.lead'].search([('unit_id','=',flat.id)])
            stage = self.env['crm.stage'].search([('probability','=',90)])
            deal =  self.env['crm.stage'].search([('probability','=',100)])
            if flat.booking_fee_payment == 'installment':
                if flat.downpayment > 0:    
                    if flat.invoice_total >= flat.downpayment:
                       if flat.lead_id and stage:
                           unwanted_lead = self.env['crm.lead'].search([('unit_id','=',flat.id),('id','!=',flat.lead_id.id),('process','in',['sale','resale'])])
                           if flat.state !='sold':
    # #                                 flat.state ='contract'
                               flat.write({'state':'contract'})
                           if flat.lead_id.stage_id != deal: 
                               flat.lead_id.stage_id = stage.id
                               # flat.lead_id.write({'stage_id':stage.id})
                           if unwanted_lead:
                               for all in unwanted_lead:
                                   x = self.env['crm.lead'].browse(all.id)
                                   x.action_set_lost()
            elif flat.booking_fee_payment == 'advance':
                if flat.payment_total >= flat.price:
                    if flat.lead_id and stage:
                        unwanted_lead = self.env['crm.lead'].search([('unit_id','=',flat.id),('id','!=',flat.lead_id.id),('process','in',['sale','resale'])])
                        if flat.state !='sold':
                            flat.write({'state':'contract'})
                        if flat.lead_id.stage_id != deal: 
                            flat.lead_id.stage_id = stage.id
                            # flat.lead_id.write({'stage_id':stage.id})
                        if unwanted_lead:
                            for all in unwanted_lead:
                                x = self.env['crm.lead'].browse(all.id)
                                x.action_set_lost()
                    
    
    def advance_payment_fee(self):
        # active_model = self.env.context.get('active_model', False)
        # active_id = self.env.context.get('active_id', False)
        stage_reserved = self.env['crm.stage'].search([('probability','=',50)])
        msg = ''
        for items in self:
            # if items.state in ['new','reserved']:
            #     raise UserError(_('Unit should be booked to Client to generate invoice !'))
                     
            if items.invoice_total >= items.price and items.price > 0.0:
                raise Warning(_('Already Paid/Invoiced Full Amount'))
                
            if not items.building_id.account_id:
                journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                if journal :
                    acct_id = journal[0].default_credit_account_id.id
            else:
                acct_id = items.building_id.account_id.id
                 
            if items.account_analytic_id:
                analytic = items.account_analytic_id.id
            else:
                analytic = False 
                 
            params = self.env['ir.config_parameter'].sudo()        
            tax_ids = params.get_param('zb_building_management.default_sellable_tax_ids') or False,
            advance_journal_id = params.get_param('zb_bf_custom.advance_payment_journal_id') or False
            advance_product_id = params.get_param('zb_bf_custom.advance_product_id') or False
            
            if not advance_journal_id:
                raise Warning(_('Please Configure Advance Journal'))
            if not advance_product_id:
                raise Warning(_('Please Configure Advance Product'))
            
            if tax_ids[0]:
                temp = re.findall(r'\d+', tax_ids[0]) 
                tax_list = list(map(int, temp))
                 
            vals = {
                    'partner_id': items.buyer_id and items.buyer_id.id,
                    'type': 'out_invoice',
                    'invoice_date': items.invoice_date if items.invoice_date else '',
                    'unit_id': items.id,
                    'building_id':items.building_id and items.building_id.id,
                    'lead_id':items.lead_id and items.lead_id.id,
                    'journal_id':int(advance_journal_id),
                    'invoice_line_ids': [(0, 0, {
                                                'product_id':int(advance_product_id),
                                                'name': 'Advance payment for Unit {} in {}, {}th floor , {}  , Area - {} Sqm, Sale price BD {}/- '.format(self.name,self.building_id.name,self.floor,self.bedroom.name,self.total_area,round(self.price)),
                                                'price_unit': items.price,
                                                'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
                                                'quantity': 1,
#                                                 'from_date': items.contract_date,
                                                'account_analytic_id':analytic,
                                                'account_id': acct_id,
                                                 })],
                        }
            if items.state=='reserved' and not self.lead_id.stage_id == stage_reserved:
                stage = self.env['crm.stage'].search([('probability','=',49)])
                # items.sudo().write({'buyer_id':items.lead_id.partner_id.id,
                #                })
                if stage:
                    if items.buyer_id:
                        msg ='Reserved by: %s on %s'%(items.buyer_id.name,items.reservation_date)
                    else:
                        msg ='Reserved by: %s on %s'%(items.buyer_id.name,items.reservation_date)
            
            else:
                stage = self.env['crm.stage'].search([('probability','=',70)])
                if items.price:
                    invoice_id = self.env['account.move'].create(vals)
                    invoice_id.action_post()
                    items.update({'invoice_ids1': [(4,invoice_id.id)]})
                    items._calculate_invoice_total()
                    items.sudo().write({'buyer_id':items.lead_id.partner_id.id,
                                      'state':'book',
                                       'contract_date':datetime.today() })
                    items.sudo().write({
                                      'reservation_time':0
                                      })
                    items.message_post(body=_(' {} booked  on {}').format(items.lead_id.partner_id.name,datetime.today()))
                    items.lead_id.create_resale_invoices_()
                    if invoice_id.invoice_date:
                        items.las_date = invoice_id.invoice_date
            if items.lead_id.stage_id.id != stage.id:
                if stage:
                    items.lead_id.stage_id = stage.id
                    items.lead_id.msg = msg
                    items.lead_id.probability = stage.probability
                    items.lead_id.store_prob = stage.probability
            # items.state_change()
            
     
    owner_id = fields.Many2one('res.partner',string="Owner")
    resale_commission_amount = fields.Float(string="Resale Commission Amount")
    resale = fields.Boolean(string="Resale")
    resale_move_id = fields.Many2one('account.move',string="Resale Move",copy=False)
    lead_id = fields.Many2one('crm.lead',string="Lead details",readonly=True,copy=False)
    buyer_id = fields.Many2one('res.partner','Client',readonly =True,copy=False)
    state = fields.Selection([
        ('new', 'New'),
        ('reserved','Reserved'),
        ('book', 'Booked'),
        ('contract', 'Contract Signed'),
        ('sold', 'Sold'),
        ('cancel','Cancelled')
        ], 'Status',default='new')
    
    jv_count = fields.Integer(compute='_compute_jv',string='Journal Entry Counts') 
    owner_history_ids = fields.One2many('owner.history','unit_id',string="Owner History")
    contract_date = fields.Date('Contract Date',copy=False)
    adviser_id = fields.Many2one('res.users',string="Property Advisor",default=lambda self: self.env.uid)
    service_charge = fields.Float('Service Charge', digits = (12,3))
    unit_agent_id = fields.Many2one('res.partner',string="Agent")
    resale_owner_commission = fields.Float(string="Resale Owner Commission",digits = (12,3))
    resale_buyer_commission = fields.Float(string="Resale Buyer Commission",digits = (12,3))
    resale_agent_commission = fields.Float(string="Resale Agent Commission",digits = (12,3))
    feature = fields.Selection([('bare', 'Unfurnished'),
        ('semi furnish', 'Semi Furnish'),
        ('fully furnish', 'Fully Furnish'),
        ], 'Feature', copy=False, help="Features", index=True)
    remarks = fields.Text(string='Remarks')
    unit_view_id = fields.Many2one('unit.view','View')
    managed_by_rs = fields.Boolean(string="Managed By RS")
    entry_date = fields.Date('Entry Date')
    contract_time = fields.Integer('Contract Time', default=default_booking_time)
    booking_fee_payment = fields.Selection([('advance', 'Advance Payment'),
        ('installment', 'Installment Payment'),
        ], 'Booking Fee Payment',copy=False)
    invoice_date = fields.Date('Invoice Date',copy=False)

    
    @api.model
    def action_set_new_reserved(self):
          
        reserved_unit = self.env['zbbm.unit'].search([('state','=','reserved')])
        booked_unit = self.env['zbbm.unit'].search([('state','=','book')])
        new = all2 = self.env['crm.stage'].search([('probability','=',10)],limit=1)   
        end_date = ''
        book_date = ''
        for session in reserved_unit:
            if session.state =="reserved":
                if session.reservation_date and session.reservation_time:
                    end_date = datetime.strptime(str(session.reservation_date), '%Y-%m-%d') +timedelta(days=(session.reservation_time))
                if end_date:
                    if datetime.today() > end_date:
                        if session.state =="reserved":
                            res_lead = self.env['crm.lead'].search([('probability','=',50),('unit_id','=',session.id),('process','in',['sale','resale'])])
                            if res_lead:
                                res_lead.write({'stage_id' : new and new.id})
                                res_lead.stage_id= new.id
                                res_lead.probability = new.probability
                                res_lead.reserve_expired = True
                                session.state='new'

#Multiple invoices generated should be handled manaually
        for unit in booked_unit:
            if unit.contract_date and unit.contract_time:
                book_date = datetime.strptime(str(unit.contract_date), '%Y-%m-%d') +timedelta(days=(unit.contract_time))
            if book_date:
                if datetime.today() > book_date:
                    if unit.state =="book":
                        book_lead = self.env['crm.lead'].search([('probability','=',70),('unit_id','=',unit.id),('process','in',['sale','resale'])])
                        if book_lead:
                            if not book_lead.unit_id.instlm_total == book_lead.unit_id.price:
                                book_lead.write({'stage_id' : new and new.id})
                                book_lead.stage_id= new.id
                                book_lead.probability = new.probability
                                book_lead.book_expired = True
                                book_lead.unit_id.state = 'new'
                                


class InvoicePlan(models.Model):
    _name = "invoice.plan"
    _description = "Invoice Plan"
    
    inv_date = fields.Date(string="Date")
    amount = fields.Float(string="Amount",digits = (12,3))
    move_id = fields.Many2one('account.move',string="Invoice")
    lease_agreement_id = fields.Many2one('zbbm.module.lease.rent.agreement',string="Lease Agreement")
    management_boolean = fields.Boolean(string="Management Fees",default=False)
    
    def get_formatted_date(self, date):
        datetime.strptime(res['data']['date_from'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)    

    
    def get_to_date(self):
        for line in self:
            from_date = line.inv_date
            to_date = from_date + relativedelta(days=-1,months=self.lease_agreement_id.invoice_cycle_num)
        return to_date
    
    def invoice_create(self):
        
        params = self.env['ir.config_parameter'].sudo()   
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        rent_invoice_journal_id = params.get_param('zb_bf_custom.rent_invoice_journal_id') or False
        rent_invoice_product_id = params.get_param('zb_bf_custom.rent_invoice_product_id') or False
        if not rent_invoice_product_id:
            raise Warning(_('Please Configure Rent Invoice Product'))
        
        product = self.env['product.product'].browse(int(rent_invoice_product_id))
        lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
        date_format = lang_id.date_format
        
        for line in self:
            # updated_last_date = datetime.strptime(str(from_date), '%Y-%m-%d')
            # sql = """SELECT id
            #                 FROM account_move 
            #                 WHERE invoice_date = %s 
            #                 AND lease_id = %s
            #                 AND partner_id = %s
            #                 AND state = 'posted'
            #                 AND type = 'out_invoice'
            #                 AND journal_id = '%s'
            #                 """%(line.inv_date,)
            last_created_rent_inv = self.env['account.move'].search([('invoice_plan_id','=',line.id)])
            if not building_income_account_id:
                journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                if journal :
                    acct_id = journal[0].default_credit_account_id.id
            else:
                acct_id = int(building_income_account_id)
            
            inv_date_format = ''
            to_date_format = ''
            if line.inv_date:
                # inv_date_format = datetime.strptime(str(line.inv_date), '%Y-%m-%d').strftime('%d/%m/%Y')
                inv_date_format = datetime.strptime(str(line.inv_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            if self.get_to_date():
                to_date_format = datetime.strptime(str(self.get_to_date()),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
                # to_date_format = datetime.strptime(str(self.get_to_date()), '%Y-%m-%d').strftime('%d/%m/%Y')
            description = 'Rent for the Period from %s to %s'%(inv_date_format,to_date_format)
            
            tax_ids = params.get_param('zb_building_management.default_rental_tax_ids') or False,
            if tax_ids[0]:
                temp = re.findall(r'\d+', tax_ids[0]) 
                tax_list = list(map(int, temp))
            vals = {
                  'partner_id': line.lease_agreement_id.tenant_id.id,
                  'type': 'out_invoice',
                  'invoice_date': line.inv_date,
                  'from_date':line.inv_date,
                  'to_date':self.get_to_date(),
                  'building_id': line.lease_agreement_id.building_id.id,
                  'module_id': line.lease_agreement_id.subproperty.id,
                  'lease_id': line.lease_agreement_id.id,
                  'journal_id':int(rent_invoice_journal_id),
                  'invoice_plan_id':line.id,
                  'invoice_line_ids': [(0, 0, {
                                        'product_id':int(rent_invoice_product_id),
                                        'name': description,
                                        'price_unit': line.amount,
                                        'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
                                        'quantity': 1,
                                        'account_analytic_id':line.lease_agreement_id.building_id.analytic_account_id.id if line.lease_agreement_id.building_id.analytic_account_id else '',
                                        'account_id': product.property_account_income_id and product.property_account_income_id.id or acct_id,
                                        })],
                }
            if not last_created_rent_inv:
                invoice_id = self.env.get('account.move').create(vals)
                invoice_id.action_post()
                line.move_id = invoice_id.id
            
    

class Unit_view(models.Model):
    _name = "unit.view"
    _description = "Unit View"    
    
    name = fields.Char('View')

class ServicesLeaseAgreement(models.Model):
    _name = "zbbm.services.agreement"
    _description = "Lease Services"
    
    
#     _sql_constraints = [
#         ('account_unique', 'unique (product_id,account_no,module_id)', 'Account No Already Exists')
#     ]    
    
#     @api.onchange('account_no')
#     def _onchange_account(self):
#         service_ids = self.env['zbbm.lease.services'].search([('account_no','!=',False)])
#         for service in service_ids:
#             
#             if service.account_no == self.account_no:
#                 raise ValidationError(_('A Product with same Account No Already Exists.'))
#     
#     
#     def _get_computed_name(self):
#         self.ensure_one()
# 
#         if not self.product_id:
#             return ''
#         values = []
#         if self.product_id.partner_ref:
#             values.append(self.product_id.partner_ref)
#         return '\n'.join(values)
#     
#     
#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         for line in self:
#             line.package_name = line._get_computed_name()
            
    
#     lease_agreement_id = fields.Many2one('zbbm.module.lease.rent.agreement',string='Lease Agreement')
    lease_id = fields.Many2one('zbbm.module.lease.rent.agreement',string='Lease Agreement')
    module_id = fields.Many2one("zbbm.module",string="Flat")
    building_id = fields.Many2one('zbbm.building',string="Building")
    name=fields.Char('Description')
    # servic_id=fields.Many2one('project.task',string='Service')
    product_id = fields.Many2one('product.product','Service')
    bill = fields.Selection([
                    ('fixed', 'Fixed'),
                    ('owner', 'Extra By Owner'),
                    ('tenant','Extra By Tenant'),
                    ('by_rs','By RS'),
                    ], 'Bill',default='fixed')
    owner_share = fields.Float('Owner Share',digits = (12,3))
    owner_share_arabic = fields.Char('Owner Share in Arabic')
    tenant_share = fields.Float('Tenant Share',digits = (12,3))
    managed_by_rs = fields.Boolean(string="Managed By RS")
    package_name = fields.Char(string="Package Name")
    account_no = fields.Char(string="Account No")
    ewa = fields.Boolean(string="EWA",related="product_id.product_tmpl_id.ewa")
    owner_id = fields.Many2one('res.partner',string="Owner")
    from_date = fields.Date(string="Disconnected Date")
    to_date = fields.Date(string="Reconnected Date")
    initial_connection_date = fields.Date(string="Initial Connection Date")
    tenant_upgrade_date = fields.Date(string="Tenant Upgrade Request date")
    osn_extra_charge = fields.Float(string="OSN Package/Extra Charge",digits = (12,3))
    area = fields.Text(string='Area')
    trf_status = fields.Boolean('Trf Status', default=False)

#Created Onetomany for services-Jeena
class Service_Building(models.Model):
    _name = "zbbm.services"
    _description = "Building Services"
    
    
    _sql_constraints = [
        ('account_unique', 'unique (product_id,account_no,module_id)', 'Account No Already Exists')
    ]    
    
    @api.onchange('account_no')
    def _onchange_account(self):
        service_ids = self.env['zbbm.services'].search([('account_no','!=',False)])
        for service in service_ids:
            
            if service.account_no == self.account_no:
                raise ValidationError(_('A Product with same Account No Already Exists.'))
    
    
    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''
        values = []
        if self.product_id.partner_ref:
            values.append(self.product_id.partner_ref)
        return '\n'.join(values)
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            line.package_name = line._get_computed_name()
            
            
    
    lease_agreement_id = fields.Many2one('zbbm.module.lease.rent.agreement',string='Lease Agreement')
    module_id = fields.Many2one("zbbm.module",string="Flat")
    building_id = fields.Many2one('zbbm.building',string="Building")
    name=fields.Char('Description')
#     servic_id=fields.Many2one('project.task',string='Service')
    product_id = fields.Many2one('product.product','Service')
    bill = fields.Selection([
                    ('fixed', 'Fixed'),
                    ('owner', 'Extra By Owner'),
                    ('tenant','Extra By Tenant'),
                    ('by_rs','By RS'),
                    ], 'Bill',default='fixed')
    owner_share = fields.Float('Owner Share',digits = (12,3))
    owner_share_arabic = fields.Char('Owner Share in Arabic')
    tenant_share = fields.Float('Tenant Share',digits = (12,3))
    managed_by_rs = fields.Boolean(string="Managed By RS")
    package_name = fields.Char(string="Package Name")
    account_no = fields.Char(string="Account No")
    ewa = fields.Boolean(string="EWA",related="product_id.product_tmpl_id.ewa")
    owner_id = fields.Many2one('res.partner',string="Owner")
    from_date = fields.Date(string="Disconnected Date")
    to_date = fields.Date(string="Reconnected Date")
    initial_connection_date = fields.Date(string="Initial Connection Date")
    tenant_upgrade_date = fields.Date(string="Tenant Upgrade Request date")
    osn_extra_charge = fields.Float(string="OSN Package/Extra Charge",digits = (12,3))
    area = fields.Text(string='Area')
    trf_status = fields.Boolean('Trf Status', default=False)
    
#DB     @api.model
#     def create(self,vals):
#         res = super(Service_Building,self).create(vals)
#         if vals.get('module_id'):
#             lease_agreement_id = self.env['zbbm.module.lease.rent.agreement'].search([('subproperty','=',vals.get('module_id'))])
#             _logger.info("2222222222222222222222222222222222222222222222222222222 %s",lease_agreement_id)
#             if lease_agreement_id:
#                 res.lease_agreement_id = lease_agreement_id.id
#         return res
    


class RawServices(models.Model):
    _name = "raw.services"
    _description = "RawServices"
    _order = "id desc"
    
    
    
#     _sql_constraints = [
#         ('account_uniq', 'unique (account_no)', 'Account No Already Exists')
#     ]    
#     
    
    def action_view_invoice(self):
        invoices = self.env['account.move'].search([('state','=','posted'),('raw_service_id','=',self.id),('type','in',['out_invoice','out_refund'])])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
     
 
    def action_view_expense(self):
        invoices = self.env['account.move'].search([('state','=','posted'),('raw_service_id','=',self.id),('type','in',['in_invoice','in_refund'])])
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action        
    
    
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.move'].search([('state','=','posted'),('raw_service_id.id','=',self.id),('type','in',['out_invoice','out_refund'])])
            order.invoices_count = len(invoices) 
    
    def _compute_expenses(self):
        for order in self:
            invoices = self.env['account.move'].search([('state','=','posted'),('raw_service_id','=',self.id),('type','in',['in_invoice','in_refund'])])
            order.expenses_count = len(invoices)

    
    
    @api.depends('account_no','amount')
    def calculate_share(self):
        for order in self:
            
            if order.lease_agreement_id:
                service_ids = self.env['zbbm.services.agreement'].search([('account_no','=',order.account_no),('lease_id','=',order.lease_agreement_id.id)])
            else:
                service_ids = self.env['zbbm.services'].search([('account_no','=',order.account_no)])
            if service_ids:
                for service_id in service_ids:
                    
                    if not service_id.bill == 'by_rs':
                        if service_id.bill == 'fixed':
                            order.owner_share = service_id.owner_share
                            order.tenant_share = service_id.tenant_share
                        elif service_id.bill == 'tenant':
                            if order.amount <= service_id.owner_share:
                                order.owner_share = order.amount
#                                 bal = order.amount - service_id.owner_share
                                order.tenant_share = 0.000
                            else:
                                order.owner_share = service_id.owner_share
                                bal = order.amount - service_id.owner_share
                                order.tenant_share = bal
                        else:
                            if order.amount <= service_id.tenant_share:
                                order.tenant_share = order.amount
                                order.owner_share = 0.000
                            else:
                                order.tenant_share = service_id.tenant_share
                                bal = order.amount - service_id.tenant_share
                                order.owner_share = bal
                    else:
                        order.owner_share = 0.000
                        order.tenant_share = 0.000
            else:
                order.owner_share = 0.000
                order.tenant_share = 0.000
    
    
#     @api.onchange('module_id')
#     def set_lease_agreement(self):
#         for order in self:
#             if order.module_id:
#                 lease_id = self.env['zbbm.module.lease.rent.agreement'].search([('subproperty','=',order.module_id.id),('state','=','active')])
#                 if lease_id:
#                     order.lease_agreement_id = lease_id.id
#                 else:
#                     order.lease_agreement_id = ''
                    
    @api.onchange('account_no')
    def fetch_vals(self):
        for order in self:
            if order.account_no:
                service_id = self.env['zbbm.services'].search([('account_no','=',order.account_no)])
                lease_service_id = self.env['zbbm.services.agreement'].search([('account_no','=',order.account_no),('lease_id.state','=','active')],order='id desc',limit=1)
                if lease_service_id:
                    order.lease_agreement_id = lease_service_id.lease_id.id
                    order.product_id = lease_service_id.product_id.id
                    order.module_id = lease_service_id.lease_id.subproperty.id
                else:
                    order.lease_agreement_id = False
                    if service_id and not service_id.building_id:
                        order.module_id = service_id.module_id.id
                        order.product_id = service_id.product_id.id
                                
                    else:
                        order.lease_agreement_id = False
                        order.module_id = False
                        order.product_id = service_id.product_id.id
                        order.building_id = service_id.building_id.id
                        order.area = service_id.area

    
    name = fields.Char(string="Name",readonly=True,copy=False) 
    lease_agreement_id = fields.Many2one('zbbm.module.lease.rent.agreement',string='Lease Agreement')
    module_id = fields.Many2one("zbbm.module",string="Flat")
    product_id = fields.Many2one('product.product','Service')
    bill = fields.Selection([
                    ('fixed', 'Fixed'),
                    ('owner', 'Extra By Owner'),
                    ('tenant','Extra By Tenant'),
                    ('by_rs','By RS'),
                    ], 'Bill',default='fixed')
    owner_share = fields.Float('Owner Share',compute = 'calculate_share',digits = (12,3),store=True)
    tenant_share = fields.Float('Tenant Share',compute = 'calculate_share',digits = (12,3),store=True)
    service_date = fields.Date('Date',required=True)
    owner_id = fields.Many2one('res.partner','Owner',related='module_id.owner_id')
    tenant_id = fields.Many2one('res.partner','Tenant',related='module_id.tenant_id')
    billing_status = fields.Selection([
                    ('to_be_invoiced', 'To Be Invoiced'),
                    ('invoiced', 'Invoiced'),
                    ], 'Billing Status',default='to_be_invoiced')
    
#     module_id = fields.Many2one('zbbm.module', 'Unit',related='lease_agreement_id.subproperty')
    building_id = fields.Many2one('zbbm.building','Building')
    account_no = fields.Char(string="Account No")
    bill_no = fields.Char(string="Bill No")
    amount = fields.Float(string="Amount",digits = (12,3))
    bill_date = fields.Date(string="Bill Date")
    due_date = fields.Date(string="Due Date")
    rent_invoice_id = fields.Many2one('account.move',string="Rent Invoice")
    payment_advice_id = fields.Many2one('account.payment',string ="Payment Advice")
    payment_link_id = fields.Many2one('account.payment',string ="Payment Link")
    move_id = fields.Many2one('account.move',string="Owner/Tenant/Invoice")
    type_of_service = fields.Selection([
                    ('ewa', 'EWA'),
                    ('internet', 'Internet'),
                    ], 'Type Of Service',default='ewa')
    
    invoices_count = fields.Integer(compute='_compute_invoice',string='Invoices') 
    expenses_count = fields.Integer(compute='_compute_expenses',string='Vendor Bills') 
    area = fields.Char(string="Area")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    
    
    @api.model
    def create(self,vals):
        if vals.get('name', 'None') == 'None':
            vals['name'] = self.env['ir.sequence'].get('raw.services') or '/'
        vals.update({'billing_status':'invoiced'})
        res = super(RawServices, self).create(vals)
        res.fetch_vals()
        params = self.env['ir.config_parameter'].sudo()        
        
        if not res.product_id.service_product_partner_id:
            raise UserError(_('Please Configure Service Provider in Products'))
        
        if not res.product_id.service_product_journal_id:
            raise UserError(_('Please Configure Service Journal in Products'))
        
        if not res.product_id.service_product_vendor_journal_id:
            raise UserError(_('Please Configure Service Purchase Journal in Products'))
        
        
        building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
        if not building_income_account_id:
            raise Warning(_('Please Configure Building Income Account'))
        
        
        building_expense_account_id = params.get_param('zb_bf_custom.building_expense_acccount_id') or False
        if not building_expense_account_id:
            raise Warning(_('Please Configure Building Expense Account'))
        
        tabreed_journal_id = params.get_param('zb_bf_custom.tabreed_journal_id') or False
        if not tabreed_journal_id:
            raise Warning(_('Please Configure Tabreed journal'))
        
        config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        if not config_owner_id:
            raise Warning(_('Please Configure Owner'))
        
        lang_id = self.env['res.lang']._lang_get(self.env.user.lang)
        date_format = lang_id.date_format
        formatted_service_date = ''
        from_date_format = ''
        to_date_format = ''
        if res.service_date:
            formatted_service_date = datetime.strptime(str(res.service_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        if res.from_date:
            from_date_format = datetime.strptime(str(res.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        if res.to_date:
            to_date_format = datetime.strptime(str(res.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        
        if res.building_id and not res.module_id:
            ref = 'service bill for the period from {} to {}'.format(from_date_format,to_date_format)
        else:
            ref = 'service bill for the period from {} to {}'.format(from_date_format,to_date_format)
        
        currnet_user = self.env['res.users'].browse(self._uid)
        company_id = currnet_user.company_id
#         company_id = self.env['res.company']._company_default_get()   
        
        if res.lease_agreement_id:
            service_id = self.env['zbbm.services.agreement'].search([('account_no','=',res.account_no),('lease_id','=',res.lease_agreement_id.id)])
        elif res.module_id or res.building_id:
            service_id = self.env['zbbm.services'].search([('account_no','=',res.account_no)])
        
        
        if res.building_id and not res.module_id:
            ref = 'service bill for the period from {} to {}'.format(from_date_format,to_date_format)
#PV             building_invoice_vals = {
#                 'partner_id': res.product_id.service_product_partner_id.id,
#                 'type': 'out_invoice',
#                 'invoice_date':res.service_date,
#                 'from_date':res.service_date,
#                 'to_date':res.service_date,
#                 'module_id': res.module_id.id if res.module_id else '',
#                 'building_id':res.module_id.building_id.id if res.module_id else res.building_id.id,
#                 'agreement_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
#                 'journal_id':res.product_id.service_product_journal_id.id,
#                 'deposit_jv_desc':ref,
#                 'raw_service_id':res.id,
#                 'invoice_line_ids':[(0, 0, {
#                                             'account_id':res.module_id.building_id.account_id.id,
#                                             'partner_id':company_id.partner_id.id,
#                                             'product_id':res.product_id.id,
#                                             'name':res.name,
#                                             'price_unit':res.amount,
#                                             'quantity': 1,
# #                                             'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
#                                             'analytic_account_id':res.module_id.building_id.analytic_account_id.id,
#                                              })]
#                 }
#             
            
            building_bill_vals = {
                'partner_id': res.product_id.service_product_partner_id.id,
                'type': 'in_invoice',
                'invoice_date':res.service_date,
                'from_date':res.from_date,
                'to_date':res.to_date,
                'module_id': res.module_id.id if res.module_id else False,
                'building_id':res.building_id.id,
                'agreement_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
                'lease_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
                'journal_id':res.product_id.service_product_vendor_journal_id.id,
                'deposit_jv_desc':ref,
                'raw_service_id':res.id,
                'invoice_origin':vals['name'],
                'ref':res.bill_no,
                'invoice_line_ids':[(0, 0, {
                                            'account_id':res.product_id.property_account_expense_id.id if res.product_id.property_account_expense_id else int(building_expense_account_id),
                                            'partner_id':res.product_id.service_product_partner_id.id,
                                            'product_id':res.product_id.id,
                                            'name':'%s - %s %s'%(res.building_id.code,res.product_id.name,ref),
                                            'price_unit':res.amount,
                                            'quantity': 1,
                                            'tax_ids' : res.product_id.supplier_taxes_id.ids,
                                            'analytic_account_id':res.building_id.analytic_account_id.id,
                                             })]
                }
#PV             inv_move_id = self.env['account.move'].create(building_invoice_vals)
#PV             inv_move = inv_move_id.action_post()
            if res.product_id.service_product_journal_id.id != int(tabreed_journal_id):
                if res.product_id.service_product_partner_id:
                    bill_move_id = self.env['account.move'].create(building_bill_vals)
                    bill_move = bill_move_id.action_post()
        
        
        else:
            ref = 'service bill for the period from {} to {}'.format(from_date_format,to_date_format)
            # if res.module_id.flat_on_offer == True:
            #     owner_id = config_owner_id
            # else:
            #     owner_id = res.module_id.owner_id
            owner_id = self.env['res.partner'].get_owner_id(res.module_id,res.lease_agreement_id)
            
            invoice_debit_owner_vals = {
                    'partner_id':owner_id.id,
                    'raw_service_id':res.id,
                    'type': 'out_invoice',
                    'invoice_date':res.service_date,
                    'from_date':res.from_date,
                    'to_date':res.to_date,
                    'module_id': res.module_id.id if res.module_id else False,
                    'building_id':res.module_id.building_id.id if res.module_id else res.building_id.id,
                    'agreement_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
                    'lease_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
                    'journal_id':res.product_id.service_product_journal_id.id,
                    'deposit_jv_desc':ref,
                    'invoice_origin':vals['name'],
                    'ref':res.bill_no,
                    'invoice_line_ids': [(0, 0, {
#                                             'partner_id':res.module_id.owner_id.id,
                                            'product_id':res.product_id.id,
                                            'name':'%s- %s - %s %s'%(res.module_id.building_id.code,res.module_id.name,res.product_id.name,ref),
                                            'price_unit':res.owner_share,
                                            'quantity': 1,
                                            'tax_ids' : res.product_id.taxes_id.ids,
                                            'analytic_account_id':res.module_id.building_id.analytic_account_id.id,
                                            'account_id':res.product_id.property_account_income_id.id if res.product_id.property_account_income_id else int(building_income_account_id),
                                             })],
                    }
            
            
            invoice_debit_tenant_vals = {
                    'partner_id': res.lease_agreement_id.tenant_id.id if res.lease_agreement_id else owner_id.id,
                    'type': 'out_invoice',
                    'invoice_date':res.service_date,
                    'from_date':res.from_date,
                    'to_date':res.to_date,
                    'module_id': res.module_id.id if res.module_id else False,
                    'building_id':res.module_id.building_id.id if res.module_id else res.building_id.id,
                    'agreement_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
                    'lease_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
                    'journal_id':res.product_id.service_product_journal_id.id,
                    'deposit_jv_desc':ref,
                    'raw_service_id':res.id,
                    'invoice_origin':vals['name'],
                    'ref':res.bill_no,
                    'invoice_line_ids': [(0, 0, {
                                            'account_id':res.product_id.property_account_income_id.id if res.product_id.property_account_income_id else int(building_income_account_id),
#                                             'partner_id':res.tenant_id.id,
                                            'product_id':res.product_id.id,
                                            'name':'%s- %s - %s %s'%(res.module_id.building_id.code,res.module_id.name,res.product_id.name,ref),
                                            'price_unit':res.tenant_share,
                                            'tax_ids' : res.product_id.taxes_id.ids,
                                            'quantity': 1,
                                            'analytic_account_id':res.module_id.building_id.analytic_account_id.id,
                                             })],
                    }
    
            payable_account = res.product_id.property_account_expense_id.id if res.product_id.property_account_expense_id else int(building_expense_account_id),
            payable_owner = res.product_id.service_product_partner_id if service_id.managed_by_rs else owner_id
            invoice_payable_vals = {
                    'partner_id': payable_owner.id,
                    'type': 'in_invoice',
                    'invoice_date':res.service_date,
                    'from_date':res.from_date,
                    'to_date':res.to_date,
                    'module_id': res.module_id.id if res.module_id else False,
                    'building_id':res.module_id.building_id.id if res.module_id else res.building_id.id,
                    'agreement_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
                    'lease_id':res.lease_agreement_id.id if res.lease_agreement_id else '',
                    'journal_id':res.product_id.service_product_vendor_journal_id.id,
                    'deposit_jv_desc':ref,
                    'raw_service_id':res.id,
                    'invoice_origin':vals['name'],
                    'ref':res.bill_no,
                    'invoice_line_ids': [(0, 0, {
                                            'account_id':payable_account,
#                                             'partner_id':res.product_id.service_product_partner_id.id,
                                            'product_id':res.product_id.id,
                                            'name':'%s- %s - %s %s'%(res.module_id.building_id.code,res.module_id.name,res.product_id.name,ref),
                                            'price_unit':res.tenant_share + res.owner_share,
                                            'quantity': 1,
                                            'tax_ids' : res.product_id.supplier_taxes_id.ids,
                                            'analytic_account_id':res.module_id.building_id.analytic_account_id.id,
                                             })]
                    }
    
            if res.owner_share > 0:
                if owner_id:
                    owner_move_id = self.env['account.move'].create(invoice_debit_owner_vals)
                    owner_move = owner_move_id.action_post()
#                 for line in owner_move_id.line_ids:
#                     if line.credit > 0.000:
#                         line.partner_id = company_id.partner_id.id
                
            if res.tenant_share > 0:
                # if res.lease_agreement_id and res.lease_agreement_id.state == 'active':
                #     if res.tenant_id:
                tenant_move_id = self.env['account.move'].create(invoice_debit_tenant_vals)
                tenant_move = tenant_move_id.action_post()
            if vals.get('amount') > 0:
                if res.product_id.service_product_journal_id.id != int(tabreed_journal_id):
                    if payable_owner:
                        payable_move_id = self.env['account.move'].create(invoice_payable_vals)
                        payable_move_id.action_post()
            
#         move_id = self.env['account.move'].create(entry_vals)
#         move = move_id.action_post()
#         res.move_id = move_id.id
#         res.module_id.service_move_id = move_id.id
#         res.lease_agreement_id.service_move_id = move_id.id
#         
        return res      


    

class OwnerHistory(models.Model):
    _name = "owner.history"
    _description = "Owner History"
    
    
    owner_id = fields.Many2one("res.partner",string="Owner")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    unit_id = fields.Many2one('zbbm.unit',string="Sellable Unit")
    module_id = fields.Many2one('zbbm.module',string="Module")



    




