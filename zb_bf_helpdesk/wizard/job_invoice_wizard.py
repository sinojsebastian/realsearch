 # -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.tools.translate import _
from datetime import date,datetime,timedelta 
from odoo.exceptions import AccessError,UserError,Warning
from dateutil.relativedelta import relativedelta
import re


import logging
_logger = logging.getLogger(__name__)


class JobInvoiceWizard(models.TransientModel):
	_name = 'job.invoice.wizard'
	_description = "Job Invoice"



	def action_create_job_invoice(self):
		if self.env.context.get('active_model') == 'helpdesk.ticket':
			ticket = self.env['helpdesk.ticket'].browse(self.env.context.get('active_id'))
			if ticket.job_order_id:
				job_details = ticket.job_order_id
		else:	
			job_details = self.env['job.order'].browse(self.env.context.get('active_id'))
		params = self.env['ir.config_parameter'].sudo()     
		maintenance_journal_id = params.get_param('zb_bf_custom.maintenance_journal_id') or False
		lines  = []
		for x in self.job_invoice_line_ids:
			vals = {
				'product_id':x.product_id.id,
				'account_id':x.product_id.property_account_income_id.id,
				'name': x.description,
				'quantity':x.qty,
				'price_unit':x.unit_price,
				'tax_ids' : x.product_id.taxes_id.ids,
				'analytic_account_id':job_details.building_id.analytic_account_id.id if job_details.building_id.analytic_account_id else '',
			}
			lines.append((0, 0, vals))
		vals = {
			'job_id':job_details.id,
			'building_id':job_details.building_id.id,
			'lease_id':job_details.lease_id.id,
			'module_id':job_details.module_id.id,
			'partner_id':self.customer_id.id,
			'invoice_date':fields.Datetime.now(),
			'invoice_line_ids':lines,
			'journal_id':int(maintenance_journal_id),
			'invoice_origin':job_details.name,
			'type': 'out_invoice'}
		inv_id = self.env['account.move'].create(vals)
		inv_id.action_post()
		time_material_obj= self.env['time.material']
		for line in self.job_invoice_line_ids:
			if line.qty < line.time_material_id.qty:
				new_qty = line.time_material_id.qty - line.qty
				line.time_material_id.write({'qty':line.qty,'invoice_id':inv_id.id})
				time_material_obj.create({'product_id':line.product_id.id,'qty': new_qty,'unit_price':line.unit_price,'amount':line.amount,'job_id':int(job_details)})
			else:
				line.time_material_id.write({'invoice_id':inv_id.id})
		return True



	@api.onchange('bill_to')
	def _onchange_bill_to(self):
		if not self.bill_to  or self.bill_to == 'others':
			self.customer_id = False
		if self.bill_to:
			if self.env.context.get('active_model') == 'helpdesk.ticket':
				ticket = self.env['helpdesk.ticket'].browse(self.env.context.get('active_id'))
				if ticket.job_order_id:
					job_order = ticket.job_order_id
			else:	
				job_order = self.env['job.order'].browse(self.env.context.get('active_id'))
			params = self.env['ir.config_parameter'].sudo()
			owner_id = params.get_param('zb_bf_custom.owner_id') or False
			if self.bill_to == 'owner':
				self.customer_id = job_order.module_id.owner_id.id if job_order.module_id.owner_id else int(owner_id)
			if self.bill_to == 'tenant':
				self.customer_id = job_order.lease_id.tenant_id.id if job_order.lease_id else job_order.module_id.tenant_id.id
				

	bill_to = fields.Selection([
		('owner', 'Owner'),
		('tenant', 'Tenant'),
		('others', 'Others'),
		], 'Bill To', required=True)
	customer_id = fields.Many2one('res.partner',string='Customer',required=True)
	job_invoice_line_ids = fields.One2many('job.invoice.line','job_invoice_id',string="Lines")


class JobInvoiceWizardLine(models.TransientModel):
	_name="job.invoice.line"


	@api.depends('qty','unit_price')
	def _calculate_costs(self):
		for rec in self:
			rec.amount = rec.qty * rec.unit_price

	job_invoice_id = fields.Many2one('job.invoice.wizard',string='Job Order')
	time_material_id = fields.Many2one('time.material',string="Time Material")
	product_id = fields.Many2one('product.product',string="Product")
	description = fields.Char(string='Description')
	qty = fields.Float(string = 'Quantity')
	unit_price = fields.Float(string='Unit Price',digits=(6, 3))
	amount = fields.Float(string='Amount',compute='_calculate_costs',store=True,digits=(6, 3))


class AccountMove(models.Model):
    
    _inherit = 'account.move'

    job_id = fields.Many2one('job.order',string='Job Order')
	
	
   