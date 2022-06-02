##############################################
#
# Inforise IT & ZestyBeanz Technologies Pvt. Ltd
# By Sinoj Sebastian (sinoj@zbeanztech.com, sinoj@inforiseit.com)
# First Version 2020-08-13
# Website1 : http://www.zbeanztech.com
# Website2 : http://www.inforiseit.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
# from lxml import etree
from odoo import models, fields, api,exceptions,tools,_
from odoo.tools.translate import _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
# import re
from dateutil import relativedelta
from odoo.tools.float_utils import float_round 
import odoo.addons.decimal_precision as dp
from datetime import datetime, date, timedelta

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

import logging

_logger = logging.getLogger(__name__)


class zbbm_month(models.Model):
    _name = "zbbm.month"
    _description = "Month"
    
    name = fields.Char('Year Month')


class zbbm_building(models.Model):
    _name = 'zbbm.building'
    _description = "Buildings"
    
    @api.model
    def create(self,vals):
        try:
           res = super(zbbm_building, self).create(vals)
        except Exception as e:
            build_type = ""
            if  vals.get('building_type') == 'sell':
                build_type = 'Sellable' 
            elif vals.get('building_type') == 'both':
                build_type = 'Sellable and Leasable' 
            raise Warning(_('You dont have permission to create {}  building').format(build_type))
        return res
    
    
    
    @api.model
    def invoice_due_remainder(self):
        
        units = self.env['zbbm.unit'].search(['|',('state','=','book'),('state','=','contract')])
        if units: 
            for invoic in units:
                for invoice in invoic.installment_ids:
                    if invoice.state=='Posted' or 'Unposted':
                        if invoice.due_date:
                            end_date = datetime.strptime(str(invoice.due_date), '%Y-%m-%d') +timedelta(days=self.inv_gener_gap)
                            if datetime.today() > end_date:
                                invoice.invoice_create()
                                
                    

    def _calculate_total(self):
        '''Function to calculate total From all the invoices'''
        total = {}
        for building in self:
            total[building.id] = 0.00
            if building.module_ids:
                total_amount = 0.00
                for module in building.module_ids:
                    if module.state not in ['draft', 'cancel']:
#                         res = self.env['zbbm.module']._calculate_supplier_invoice_total()
                        if module.supplier_invoice_total:
#                             supplier_invoice_total = res[module.id]
                            total_amount = total_amount + module.invoice_total - module.supplier_invoice_total
                        else:
                            total_amount = total_amount + module.invoice_total
                                    
                total[building.id] = total_amount
                building.rent_total = total_amount
            else:
                total[building.id] = 0
                building.rent_total = 0
#         return total

    
    def _calculate_invoice_total(self):
        '''Function to calculate total From all the valid invoices'''
        total = {}
        for building in self:
#             total[building.id] = 0.00
            if building.module_ids:
                total_amount = 0.00
                for module in building.module_ids:
                    if module.state not in ['draft', 'cancel']:
                        res = self.env['zbbm.module']._calculate_invoice_total()

                        total_amount = total_amount + module.invoice_total
#                 total[building.id] = total_amount
                building.invoice_total = total_amount
            else:
                building.invoice_total = 0
            if building.unit_ids:
                total_amount = 0.00
                for unit in building.unit_ids:
                    if unit.state not in ['new', 'cancel']:
                        res = unit._calculate_invoice_total()

                        total_amount = total_amount + unit.invoice_total
#                 total[building.id] = total_amount
                building.invoice_total = total_amount
            else:
                building.invoice_total = 0
#         return total

    
    def _calculate_payment_total(self):
        '''Function to calculate total from all the valid payments'''
        total = {}
        for building in self:
            if building.module_ids:
                total_amount = 0.00
                for module in building.module_ids:
                    if module.state not in ['draft', 'cancel']:
                        res = self.env.get('zbbm.module')._calculate_payment_totals()
                        total_amount = total_amount + module.payment_total
                building.payment_total = total_amount
            else:
                building.payment_total = 0
#         return total

    
    def _calculate_balance_total(self):
        '''Function to calculate total  Balance From all the payments'''
        total = {}
        for building in self:
            if building.module_ids:
                total_amount = 0.00
                for module in building.module_ids:
                    if module.state not in ['draft', 'cancel']:
                        res = self.env['zbbm.module']._calculate_balance_total()
                        total_amount = total_amount + module.balance_total
                building.balance_total = total_amount
            else:
                building.balance_total = 0
#         return total

    
    def _calculate_balance_total_percentage(self):
        '''Function to calculate total  Balance percentage from customer invoice  payments'''
        total = {}
        precision = self.env['decimal.precision'].precision_get('Account')
        for building in self:
            totalbuilding = 0.0
            if building.invoice_total:
                totalbuilding = (building.balance_total/building.invoice_total)*100
            building.balance_total_percentage =  totalbuilding     
#         return total

    
    def _calculate_expense_total(self):
        '''Function to calculate expense total From all the valid invoices'''
        total = {}
        for building in self:
            if building.module_ids:
                total_amount = 0.00
                for module in building.module_ids:
                    if module.state not in ['draft', 'cancel']:
                        res = self.env['zbbm.module']._calculate_supplier_invoice_total()
                        total_amount = total_amount + module.supplier_invoice_total
                building.expense_total = total_amount
            else:
                building.expense_total = 0
#         return total

    
    def _calculate_expense_balance_total(self):
        '''Function to calculate total expense balance from supplier invoice payments'''
        total = {}
        for building in self:
            if building.module_ids:
                total_amount = 0.00
                for module in building.module_ids:
                    if module.state not in ['draft', 'cancel']:
                        res = self.env.get('zbbm.module')._calculate_supplier_balance_total()
                        total_amount = total_amount + module.supplier_balance_total
                building.expense_balance_total = total_amount
            else:
                building.expense_balance_total = 0
#         return total

    
    def _calculate_expense_balance_total_percentage(self):
        '''Function to calculate total  Balance percentage from supplier invoice  payments'''
        total = {}
        precision = self.env['decimal.precision'].precision_get('Account')
        for building in self:
            total[building.id] = 0.0
            if building.expense_total:
                total[building.id] = (building.expense_balance_total/building.expense_total)*100
            building.expense_balance_total_percentage = total[building.id]
#         return total
    
    
    def _get_total(self):
        '''Function retun the keys of Account Invoice'''
        result = {}
        for line in self.env.get('zbbm.module'):
            result[line.building_id.id] = True
        return result.keys()
    
    
    def _get_order_invoice(self):
        '''Function retun the keys of Account Invoice'''
        result = {}
        for invoice in self.env.get('account.move'):
            if invoice.module_id and invoice.module_id.building_id:
                result[invoice.module_id.building_id.id] = True
        return result.keys()
    
    
    def _get_order_invoice_line(self):
        '''Function retun the keys of Account Invoice'''
        result = {}
        for invoice_line in self.env.get('account.move.line'):
            if invoice_line.move_id and invoice_line.move_id.module_id and \
                invoice_line.move_id.module_id.building_id:
                result[invoice_line.move_id.module_id.building_id.id] = True
        return result.keys()

    
    def _get_payment(self):
        '''Function retun the keys of Account Voucher'''
        result = {}
        for voucher in self.env.get('account.payment'):
            if voucher.module_id and voucher.module_id.building_id:
                result[voucher.module_id.building_id.id] = True
        return result.keys()
    

    def _calculate_current_total(self):
        '''Function to calculate current total From all the valid invoices'''
        total = {}
        now = datetime.now()
        for building in self:
            total_customer_invoice = 0.00
            total_customer_balance = 0.00
            total_supplier_invoice = 0.00
            total_supplier_balance = 0.00
            if building.module_ids:
                total_amount = 0.00
                for module in building.module_ids:
                    if module.state not in ['draft', 'cancel'] and module.invoice_ids:
                        for invoice in module.invoice_ids:
                            if invoice.invoice_date:
                                date_invoice = datetime.strptime(str(invoice.invoice_date), DF)
                                if date_invoice.month == now.month and date_invoice.year == now.year:
                                    if invoice.state not in ['draft', 'cancel'] and invoice.type == 'out_invoice':
                                        total_customer_invoice = total_customer_invoice + invoice.amount_total
                                        total_customer_balance = total_customer_balance + invoice.amount_residual
                                        
                                    if invoice.state not in ['draft', 'cancel'] and invoice.type == 'out_refund':
                                        total_customer_invoice = total_customer_invoice - invoice.amount_total
                                        total_customer_balance = total_customer_balance - invoice.amount_residual
                                    if invoice.state not in ['draft', 'cancel'] and invoice.type == 'in_invoice':
                                        total_supplier_invoice = total_supplier_invoice + invoice.amount_total
                                        total_supplier_balance = total_supplier_balance + invoice.amount_residual
                                    if invoice.state not in ['draft', 'cancel'] and invoice.type =='in_refund':
                                        total_supplier_invoice = total_supplier_invoice - invoice.amount_total
                                        total_supplier_balance = total_supplier_balance - invoice.amount_residual
        
            building.current_invoice_total = total_customer_invoice
            building.current_balance_total = total_customer_balance
            building.current_expense_total =  total_supplier_invoice
            building.current_expense_balance_total = total_supplier_balance 
                                   
            total[building.id] =  {
                                   'current_invoice_total': total_customer_invoice,
                                   'current_balance_total': total_customer_balance,
                                   'current_expense_total': total_supplier_invoice,
                                   'current_expense_balance_total': total_supplier_balance 
                                   }
            
                    
            
        
        
#         return total

    
    def _calculate_current_balance_total_percentage(self,name, args):
        '''Function to calculate total  Balance percentage from customer invoice  payments'''
        total = {}
        precision = self.env['decimal.precision'].precision_get('Account')
        for building in self:
            total[building.id] = 0.0
            if building.current_invoice_total:
                total[building.id] = (building.current_balance_total/building.current_invoice_total)*100
            else:
                total[building.id] = 0.0
        return total

    
    def _calculate_current_expense_balance_total_percentage(self,name, args):
        '''Function to calculate total  Balance percentage from supplier invoice  payments'''
        total = {}
        precision = self.env['decimal.precision'].precision_get('Account')
        for building in self:
            total[building.id] = 0.0
            if building.current_expense_total:
                total[building.id] = (building.current_expense_balance_total/building.current_expense_total)*100
            else:
                total[building.id] = 0.0
        return total
   
    
    def make_available(self):
        return self.write({'state': 'available'})
    
    
    def action_delist(self):
        return self.write({'state': 'delisted'})
    
    
    def action_unavailable(self):
        return self.write({'state': 'blocked'})
    
    
    def _calculate_available_room_percentage(self,name, args):
        '''Function to calculate total  Available percentage of room'''
        total = {}
        precision = self.env['decimal.precision'].precision_get('Account')
        for building in self:
            total[building.id] = 0.0
            if building.current_expense_total:
                total[building.id] = (building.current_expense_balance_total/building.current_expense_total)*100
            else:
                total[building.id] = 0.0
        return total

    
    def _attachment_count(self):
        '''Function to get count of attachments from Building.
        '''
        attachment_ids = self.env.get('ir.attachment').search([('building_id','=',self.id)])
        for building in self:
            if attachment_ids:
                building.attachment_count = len(attachment_ids)
            else:
                building.attachment_count = 0
   
    
    def view_attach_from_building(self):
        
        model, action_id = self.env.get('ir.model.data').get_object_reference('base', 'action_attachment')
        action = self.env.ref('base.action_attachment')
#         action = model.read(action_id)
        building = []
        build_ids = self.env['ir.attachment'].search(['|',('res_id','=',self.id),('building_id','=',self.id)])
        for idss in build_ids:
            building.append(idss.id)
        
        result = {
            'name': action.name,
            'type': action.type,
#             'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': 'current',
            'res_model': action.res_model,
            'domain':[('id', 'in',building)],
            'context' : {'default_building_id' : self.id},
            'help': "Click here to create new documents."
        }
        
        return result
    

    def _calculate_count(self):
        '''Function return the count available,occupied,blocked,sold,booked etc of all building types'''
        for building in self:
            
            building.total_flats = 0
            building.available_type = 0
            building.occupied_type = 0
            building.occupied_flats = 0
            building.blocked_subproperty = 0
            building.legal_case = 0
            building.pending_type  = 0
            building.available_units = 0
            building.available_type = 0
            building.contract_case = 0
            building.sold_units = 0
            building.available_flats = 0
            building.booked_unit = 0
            user_id = self.env.user
                
            if building.module_ids:
                tot_lease = self.env['zbbm.module'].search([('building_id','=',building.id)])
                avl_lease = self.env['zbbm.module'].search([('building_id','=',building.id),('state','=','available')])
                occ = self.env['zbbm.module'].search([('building_id','=',building.id),('state','=','occupied')])
                blk = self.env['zbbm.module'].search([('building_id','=',building.id),('state','in',['new','blocked','delisted'])])
#PV                 cmpl = self.env['project.task'].search([('state','=','new'),('building_id','=',building.id)])
                legl = self.env.get('legal.cases').search([('state','=','legal'),('building_id','=',building.id)])
                
                building.total_flats += len(tot_lease)
                building.available_type = len(avl_lease)
                building.occupied_type = len(occ)
                building.occupied_flats = len(occ)
                building.blocked_subproperty = len(blk)
                building.legal_case = len(legl)
                building.pending_type  = 0

            if building.unit_ids and user_id.has_group('zb_building_management.group_administrator'):
                tot_sell = self.env['zbbm.unit'].search([('building_id','=',building.id)])
                avl_sell = self.env['zbbm.unit'].search([('building_id','=',building.id),('state','=','new')])
                book = self.env['zbbm.unit'].search([('building_id','=',building.id),('state','=','book')])
                contract = self.env['zbbm.unit'].search([('building_id','=',building.id),('state','=','contract')])
                sold = self.env['zbbm.unit'].search([('building_id','=',building.id),('state','=','sold')])
                
                building.total_flats += len(tot_sell)
                building.available_units = len(avl_sell)
                building.booked_unit = len(book)
                building.contract_case = len(contract)
                building.sold_units = len(sold)
            
            if building.total_flats > 0:
                module = float(building.available_type)
                unit = float(building.available_units)
                tot_flat = float(building.total_flats)
                building.available_flats = int(((module + unit)/tot_flat)*100)



    def action_available_subunit(self):
        '''Function retun the no of Sellable units'''
        l = [] 
        module_ids = self.env.get('zbbm.unit').search([('state','=','new'),('building_id','in',self.ids)])
        for idss in module_ids:
            l.append(idss.id)
            
        domain  = [('id', 'in',l)]
        return {
#             'view_id':False,
            'name' : "New",
            'view_mode': 'tree,form',
            'res_model': 'zbbm.unit',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
#             'readonly':False,
            'flags': {'tree': {'action_buttons': True,}},
            }
        
    
    def action_blocked_subproperty(self):
        '''Function return the no of blocked leasable units'''
        l = [] 
        module_ids = self.env.get('zbbm.module').search([('state','in',['new','blocked','delisted']),('building_id','in',self.ids)])
        for idss in module_ids:
            l.append(idss.id)
        domain  = [('id', 'in',l)]
#         view_id = self.env.ref('view_module_tree').id
        return {
#             'view_id':False,
            'name' : "New",
            'view_mode': 'tree,form',
            'res_model': 'zbbm.module',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
#             'readonly':False,
            'flags': {'tree': {'action_buttons': True,}},
            }
        
        
    def action_total_flats(self):
        '''Function retun the no of Total'''
        l = [] 
        module_ids = self.env.get('zbbm.module').search([('building_id','in',self.ids)])
        for idss in module_ids:
            l.append(idss.id)
            
        domain  = [('id', 'in',l)]
#         view_id = self.env.ref('view_module_tree').id
        return {
#             'view_id':False,
            'name' : "Total",
            'view_mode': 'tree,form',
            'res_model': 'zbbm.module',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
#             'readonly':False,
            'flags': {'tree': {'action_buttons': True,}},
            }
        

    def action_occupied_subbuid(self):
        '''Function retun the no of Available type'''
        l = [] 
        module_ids = self.env.get('zbbm.module').search([('state','=','occupied'),('building_id','in',self.ids)])
        for idss in module_ids:
            l.append(idss.id)
            
        domain  = [('id', 'in',l)]
#         view_id = self.env.ref('view_module_tree').id
        return {
            'view_id':False,
            'name' : "Occupied",
            'view_mode': 'tree,form',
            'res_model': 'zbbm.module',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
            }
        

    def action_lease_legal(self):
        '''Function retun the no of Available type'''
        l = [] 
        module_ids = self.env.get('legal.cases').search([('state','=','legal'),('building_id','in',self.ids)])
        for idss in module_ids:
            l.append(idss.id)
            
        domain  = [('id', 'in',l)]
#         view_id = self.env.ref('view_module_tree').id
        return {
            'view_id':False,
            'name' : "Legal",
            'view_mode': 'tree,form',
            'res_model': 'legal.cases',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
            }   
        

    def action_occupied_sell(self):
        '''Function retun the no of soldtype'''
        l = [] 
        module_ids = self.env.get('zbbm.unit').search([('state','=','sold'),('building_id','in',self.ids)])
        for idss in module_ids:
            l.append(idss.id)
            
        domain  = [('id', 'in',l)]
#         view_id = self.env.ref('view_module_tree').id
        return {
            'view_id':False,
            'name' : "Sold",
            'view_mode': 'tree,form',
            'res_model': 'zbbm.unit',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
            }   
        

    def action_book_sell(self):
        '''Function retun the no of Available type'''
        l = [] 
        module_ids = self.env.get('zbbm.unit').search([('state','=','book'),('building_id','in',self.ids)])
        for idss in module_ids:
            l.append(idss.id)
            
        domain  = [('id', 'in',l)]
#         view_id = self.env.ref('view_module_tree').id
        return {
            'view_id':False,
            'name' : "Booked",
            'view_mode': 'tree,form',
            'res_model': 'zbbm.unit',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
            }
        

    def action_available_subprpty(self):
        '''Function retun the no of Available Subproperty'''
        l = [] 
        module_ids = self.env.get('zbbm.module').search([('state','=','available'),('building_id','in',self.ids)])
        
        for idss in module_ids:
            l.append(idss.id)
            
        domain  = [('id', 'in',l)]
#         view_id = self.env.ref('view_module_tree').id
        return {
            'view_id':False,
            'name' : "Available",
            'view_mode': 'tree,form',
            'res_model': 'zbbm.module',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
                  }
        
        

    def action_contract_sell(self):
        '''Function retun the no of Available type'''
        l = [] 
        module_ids = self.env.get('zbbm.unit').search([('state','=','contract'),('building_id','in',self.ids)])
        for idss in module_ids:
            l.append(idss.id)
            
        domain  = [('id', 'in',l)]
#         view_id = self.env.ref('view_module_tree').id
        return {
            'view_id':False,
            'name' : "Contract Signed",
            'view_mode': 'tree,form',
            'res_model': 'zbbm.unit',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
            'flags': {'tree': {'action_buttons': True}},
                  }    
                
        
        
    def total_income(self):
        units = self.env['zbbm.unit'].search([('building_id','=',self.id)])
        module = self.env['zbbm.module'].search([('building_id','=',self.id)])
        i =0
        if units:
            for unit in units:
                i+= unit.invoice_total
        if module: 
            for modul in module:
                i+= modul.invoice_total
        self.total_income = i   
        
        
    def total_expense(self):
        module = self.env['zbbm.module'].search([('building_id','=',self.id)])
        i =0
        if module: 
            for modul in module:
                i+= modul.supplier_invoice_total
        self.total_expense = i 


    @api.depends('building_type')
    def _set_color(self):
        for rec in self:
            if rec.building_type == 'rent':
                rec.color = 1
            elif rec.building_type == 'sell':
                rec.color = 5
            else:
                rec.color = 4

        
    def _calculate_pending_type(self):
        '''Function retun the no of pending Compliants'''
        total = {}
        mod_ids = []
        i =0
#         complaints = self.env['project.task'].search([('state','=','pending'),('building_id','=',self.id)])
        for items in self:
            complaints = self.env['project.task'].search([('state','=','new'),('building_id','=',items.id)])
            items.pending_type  = len(complaints) 

    
    def actihhon_pending_compliants(self):
        '''Function retun the no pending compliants'''
        h = [] 
        complaints = self.env['project.task'].search([('state','=','new'),('building_id','=',self.ids)])
        for idss in complaints:
            h.append(idss.id)
            
        domain  = [('id', 'in',h)]
#         view_id = self.env.ref('view_module_tree').id
        return {
#             'view_id':False,
            'name' : "Pending Complaints",
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'target': 'current',
#             'readonly':False,
            'flags': {'tree': {'action_buttons': True,}}}
        
               
    bank_id = fields.Many2one('res.partner.bank',string="Bank")           
    account_id = fields.Many2one('account.account','Income Account')
    expense_account_id = fields.Many2one('account.account','Expense Account')
    
    pending_type = fields.Integer(compute='_calculate_pending_type',string='Pending Complaints') 
         
    total_income = fields.Float('Total Income',compute = 'total_income',digits='Product Price')
    total_expense = fields.Float('Total Income',compute = 'total_expense',digits='Product Price')
    color = fields.Integer('Kanban Color Index',compute='_set_color')
#     
    building_type = fields.Selection([
                    ('rent', 'Leasable'),
                    ('sell', 'Sellable'),
                    ('both','Sellable or leasable')
                    ], 'Property Type',default='rent')
    attachment_count  = fields.Integer(compute ='_attachment_count',string='Attachments') 
    current_invoice_total = fields.Float(compute ='_calculate_current_total', 
                        string='Current Invoice Total',digits='Product Price')
                 
    current_balance_total = fields.Float(compute='_calculate_current_total', 
                        string='Current Balance Total',digits='Product Price'
                        )
                 
    current_balance_total_percentage = fields.Integer(compute='_calculate_current_balance_total_percentage',
                        string='Current Balance Total Percentage')
                 
    current_expense_total = fields.Float(compute ='_calculate_current_total', 
                        string='Current Expense Total',digits='Product Price'
                        )
                 
    current_expense_balance_total = fields.Float(compute='_calculate_current_total', 
                        string='Current Expense Balance Total',digits='Product Price'
                       )
                 
    current_expense_balance_total_percentage = fields.Integer(compute='_calculate_current_expense_balance_total_percentage',
                        string='Current Expense Balance Total Percentage')
                 
    available_flats = fields.Integer(compute='_calculate_count',
                                 string='Total Available Flat %')
    total_flats = fields.Integer(compute='_calculate_count',
                                 string='Total Flat ')
    occupied_flats = fields.Integer(compute ='_calculate_count',
                                 string='Total Occupied Flat')
    available_type = fields.Integer(compute='_calculate_count',
                                 string='Total Available type',
                                 )
    booked_unit = fields.Integer(compute='_calculate_count',
                                 string='Total Booked units',
                                 )
    blocked_subproperty = fields.Integer(compute='_calculate_count',
                                 string='Total Blocked/Delisted type',
                                 )
    sold_units = fields.Integer(compute='_calculate_count',
                                 string='Total Sold Unit',
                                 )
    occupied_type = fields.Integer(compute='_calculate_count',
                                 string='Total Occupied type')
    legal_case = fields.Integer(compute='_calculate_count',
                                 string='Total Legal Case')
     
    contract_case = fields.Integer(compute='_calculate_count',
                                 string='Total Contract Signed')
    available_units = fields.Integer(compute='_calculate_count',
                                 string='Total Available Unit',
                                 )           
                
    name = fields.Char('Building Name', required=True)
    image =  fields.Binary("Image") 
    active = fields.Boolean('Active',default=True)
    building_address = fields.Many2one('res.partner', 'Building Address')
    street = fields.Char(related='building_address.street')
    street2 = fields.Char(related='building_address.street2')
    zip = fields.Char(change_default=True,related='building_address.zip')
    city = fields.Char(related='building_address.city')
    module_ids =  fields.One2many('zbbm.module', 'building_id', string='Flat/Office', readonly=True)
    unit_ids =  fields.One2many('zbbm.unit', 'building_id', string='Modules / Flats', readonly=True)
    state = fields.Selection([
                    ('new', 'New Building'),
                    ('available', 'Available'),
                    ('blocked', 'Blocked / Unavailable'),
                    ('delisted', 'Delisted'),
                    ], 'Status', readonly=True, copy=False, help="", index=True,default='new')
    build_id= fields.Many2one('zbbm.module', 'Building')
    invoice_total=fields.Float(compute='_calculate_invoice_total', string='Invoice Total', digits='Product Price')
    payment_total = fields.Float(compute='_calculate_payment_total', string='Payment Total',digits='Product Price'
                        )
    balance_total = fields.Float(compute='_calculate_balance_total', string='Balance Total',digits='Product Price')
                 
    balance_total_percentage=fields.Integer(compute='_calculate_balance_total_percentage', string='Balance Total'
                        )
                 
    rent_total = fields.Float(compute='_calculate_total',
                        string='Net Amount',digits='Product Price')
                 
    expense_total = fields.Float(compute='_calculate_expense_total',
                                 string='Expense Total',digits='Product Price')
                 
    expense_balance_total = fields.Float(compute ='_calculate_expense_balance_total', string='Expense Balance Total',digits='Product Price'
                        )
    expense_balance_total_percentage = fields.Integer(compute='_calculate_expense_balance_total_percentage', string='Balance Expe')
    cr=fields.Char('CR')
    elec=fields.Char('ELEC')
    code=fields.Char('Code',size=6,required=True) 
    downpayment_perc = fields.Float('Downpayment Percentage (%)')
    non_refund  = fields.Float('Booking fee (%)',default =0.00)
    inv_gener_gap = fields.Integer('Invoice generation gap')
    cont_preparation_fee = fields.Float('Contract Preparation Fees',digits='Product Price',required =True,default =0)
    res_com = fields.Selection([
                    ('res', 'Residential'),
                    ('com', 'Commercial'),
                    ('both','Residential or Commercial')
                    ], 'Building Type',default='res')
    
    commission_percent = fields.Float(string="Commission Percentage")
    
class zbbm_Unit(models.Model):

    _name = "zbbm.unit"
    _inherit = 'mail.thread'
    _description = "Sellable Units"
    
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False,lazy=True):
        if 'floor' in fields:
            fields.remove('floor')
        return super(zbbm_Unit, self).read_group(domain, fields, groupby, offset, limit=limit,orderby=orderby,lazy=lazy)
    
    
    @api.model
    def invoice_duemail_remainder(self):
#         self.ensure_one()
        units = self.env['zbbm.unit'].search(['|',('state','=','book'),('state','=','contract')])
        if units:
            for invoic in units:
                for invoice in invoic.invoice_ids1:
                    if invoice.date_due:
                        end_date = datetime.strptime(str(invoice.date_due), '%Y-%m-%d')
                        if datetime.today() > end_date and end_date+timedelta(days=16) > datetime.today():
                            if invoic.payment_total < invoic.invoice_total:
                                mail_pool = self.env['mail.mail']
                                email_template_obj = self.env['mail.template']
                                mailmess_pool = self.env['mail.message']
                                mail_date = datetime.now()
                                mail_pool = self.env['mail.mail']
                                email_template_obj = self.env['mail.template']
                                mailmess_pool = self.env['mail.message']
                                mail_date = datetime.now()
                                ir_model_data = invoic.env['ir.model.data']
                                try:
                                    template_id = ir_model_data.get_object_reference('zb_building_management', 'email_template_session_mail3')[1]
                                except ValueError:
                                    template_id = False
                                if template_id:
                                    mail_template_obj = self.env['mail.template'].browse(template_id)
                                    mail_id = mail_template_obj.send_mail(invoic.id, force_send=True)
                                else:
                                    raise Warning(_('Please provide Assigned user/Email'))
                            if datetime.today() > end_date+timedelta(days=16):
                                if invoic.payment_total < invoic.invoice_total:
                                    mail_pool = self.env['mail.mail']
                                    email_template_obj = self.env['mail.template']
                                    mailmess_pool = self.env['mail.message']
                                    mail_date = datetime.now()
                                    sessions = self.search([])
                                    for session in sessions:
                                        session_date = datetime.strptime(str(session.from_date), '%Y-%m-%d') - timedelta(days=1)
                                        if mail_date.strftime("%Y-%m-%d") == session_date.strftime("%Y-%m-%d"):
                                            if session.days_id:
                                                session.day = session.days_id.name 
                                            if session.volunteer_id.email1:
                                                 ir_model_data = session.env['ir.model.data']
                                                 try:
                                                    template_id = ir_model_data.get_object_reference('zb_building_management', 'email_template_session_mail4')[1]
                                                 except ValueError:
                                                     template_id = False
                                                 if template_id:
                                                    mail_template_obj = self.env['mail.template'].browse(template_id)
                                                    mail_id = mail_template_obj.send_mail(session.id, force_send=True)
                                            else:
                                                 raise Warning(_('Please provide Assigned user/Email'))            
            return True
    
    
    @api.constrains('reservation_time')
    def _check_maximum(self):
        params = self.env['ir.config_parameter'].sudo()
        max_reservation_time = params.get_param('zb_building_management.max_reservation_time') or 0.0
        if self.reservation_time > int(max_reservation_time):
            raise Warning(_('Maximum reservation time is %s days'%(max_reservation_time)))


    
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
                                template_id = ir_model_data.get_object_reference('zb_building_management', 'email_template_session_mail2')[1]
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
    def action_set_invoice_notice(self):
        invoices_dat = self.env['zbbm.unit'].search([('las_date','>=',date.today())])
        if invoices_dat:
            for items in invoices_dat:
                no =0
                if items.time_period=='month':
                    no= 30 * items.intr
                else:
                    no =1*items.intr
                plus = datetime.strptime((str(items.las_date)), '%Y-%m-%d') +timedelta(days=no)
                qe =datetime.strftime(date.today(), '%Y-%m-%d %H:%M:%S')
                if plus==datetime.strptime(str(qe), '%Y-%m-%d %H:%M:%S'):
                    rt = datetime.now()+timedelta(hours=5.5)
                    self.env.get('calendar.event').create({'name':'Invoice reminder for %s  of "tijaria tower'%(items.name),
                                                       'partner_ids':[(4, items.agent_id.partner_id.id)],
                                                       'allday':False,
                                                       'duration':1,
#                                                        'start_datetime':rt,
                                                        'start':date.today(),
                                                        'stop':date.today()+timedelta(hours=5.5)
                                                       })
        
        return True
    
    
    
    def unlink(self):
        for items in self:
            if items.state in ['book','sold']:
                raise UserError(_('Cannot delete Booked Units..!'))
            if items.installment_ids:
                for f in items.installment_ids:
                    if f.invoice_id:
                        raise UserError(_('some installment is already paid..!'))
                
            # Explicitly unlink bank statement lines so it will check that the related journal entries have been deleted first
        return super(zbbm_Unit, self).unlink()
    
    
    
    
    
    @api.onchange('unit_area','balcony_area')
    def total_area_calc(self):
        if self.unit_area or self.balcony_area:
            self.total_area = self.unit_area + self.balcony_area
        else:
            self.total_area = 0
    
    

    def make_cancel(self):
        for items in self:
            items.state = 'cancel'
            
    
    def make_booked(self):
        for items in self:
            items.state = 'book'
    

    def make_buy(self):
        for items in self:
            items.state ='sold'
            
            
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.move'].search([('unit_id','=',order.id),('type','in',['out_invoice','out_refund'])])
            order.invoice_ids1 = invoices
            order.invoice_count = len(invoices)       
    

    def get_expense(self):  
        for order in self:
#             invoices = self.env['account.invoice'].search([('partner_id','=',self.agent.id),('unit_id','=',self.id),('type','in',['in_invoice','in_refund'])])
            invoices = self.env['account.move'].search([('unit_id','=',self.id),('type','in',['in_invoice','in_refund'])])
            order.expenses_count = len(invoices) 
     
 
    def action_view_invoice(self):
#         invoices = self.mapped('invoice_ids')
        invoices = self.env['account.move'].search([('unit_id','=',self.id),('type','in',['out_invoice','out_refund'])])
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
        lead = self.env['crm.lead'].search([('unit_id','=',self.id),('unit_id','=',self.id)])
        invoices = self.env['account.move'].search([('unit_id','=',self.id),('type','in',['in_invoice','in_refund'])])
 
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    
    def _calculate_payment_totals(self):
        '''Function to calculate total from all the valid payments'''
        for module in self:
            if module.payments_ids:
                total_payments = 0.00
                for payments in module.payments_ids:
                    if payments.state not in ['draft', 'cancel'] :
                        if payments.payment_type == 'outbound':
                            total_payments = total_payments - payments.amount
                        if payments.payment_type == 'inbound':
                            total_payments = total_payments + payments.amount
                module.payment_total = total_payments
            else:
                module.payment_total = 0

    
    def state_change(self):
        for flat in self:
            lead = self.env['crm.lead'].search([('unit_id','=',flat.id)])
            stage = self.env['crm.stage'].search([('probability','=',90)])
            deal =  self.env['crm.stage'].search([('probability','=',100)])
            if flat.downpayment > 0:    
                if flat.invoice_total >= flat.downpayment:
                   if flat.lead_id and stage:
                       unwanted_lead = self.env['crm.lead'].search([('unit_id','=',flat.id),('id','!=',flat.lead_id.id)])
                       if flat.state !='sold':
# #                                 flat.state ='contract'
                           flat.write({'state':'contract'})
                       if flat.lead_id.stage_id != deal: 
                           flat.lead_id.stage_id = stage.id
                           flat.lead_id.write({'stage_id':stage.id})
                       if unwanted_lead:
                           for all in unwanted_lead:
                               x = self.env['crm.lead'].browse(all.id)
                               x.action_set_lost()
         
    
    
    def _calculate_invoice_total(self):
        '''Function to calculate total From all the valid invoices'''
        
        for flat in self:
            if flat.invoice_ids1:
                total_invoice = 0.00
                total_supplier_invoice = 0.00
                params = self.env['ir.config_parameter'].sudo() 
                resale_journl_id = params.get_param('zb_bf_custom.resale_commission_journal_id') or False
                resale_journl = self.env['account.journal'].browse(int(resale_journl_id))
                for invoice in flat.invoice_ids1:
                    if invoice.journal_id != resale_journl:
                        if invoice.state not in ['draft', 'cancel'] and invoice.type == 'out_invoice':
                            total_invoice = total_invoice + invoice.amount_total
                        if invoice.state not in ['draft', 'cancel'] and invoice.type =='out_refund':
                            total_invoice = total_invoice - invoice.amount_total
                    else:
                        if invoice.partner_id.id == flat.buyer_id.id:
                            if invoice.state not in ['draft', 'cancel'] and invoice.type == 'out_invoice':
                                total_invoice = total_invoice + invoice.amount_total
                            if invoice.state not in ['draft', 'cancel'] and invoice.type =='out_refund':
                                total_invoice = total_invoice - invoice.amount_total
                        
                flat.invoice_total = total_invoice
                flat.balance_invoice = flat.price-flat.invoice_total
            else:
                flat.invoice_total = 0
                flat.balance_invoice = 0
   
  
  
    
    
    def _calculate_balance_total(self):
        '''Function to calculate total From the balance invoices'''
        for flat in self:
            if flat.invoice_ids1:
                total_invoice = 0.00
                params = self.env['ir.config_parameter'].sudo() 
                resale_journl_id = params.get_param('zb_bf_custom.resale_commission_journal_id') or False
                resale_journl = self.env['account.journal'].browse(int(resale_journl_id))
                for invoice in flat.invoice_ids1:
                    if invoice.journal_id != resale_journl:
                        if invoice.state not in ['draft', 'cancel']:
                            total_invoice = total_invoice + invoice.amount_residual
                flat.balance_total = total_invoice
            else:
                flat.balance_total = 0
    
    
    
    @api.onchange('downpayment','number_ins')
    def get_installment(self):
        for items in self:
            if items.downpayment and items.number_ins:
                items.amount_per = (items.price-items.downpayment)/items.number_ins
            else:
                items.amount_per = 0
        
        
    def get_down(self):
        for items in self:
            bu = self.env['zbbm.building'].browse(items.building_id.id)
            if bu :
                if bu.building_type == 'sell' or  bu.building_type == 'both':
                    items.downpayment = (items.downpayment_perc*items.price)/100
                else:
                    items.downpayment = 0
            else:
                items.downpayment = 0

    
    def installment_total(self):
        
        if self.number_ins:
            if self.installment_ids:
                for i in self.installment_ids:
                    if i.state:
                        if  i.state not in  ['Unposted','draft']:
                            raise Warning(_('Cannot create new installment lines.Some entries are already posted, please do it manually'))
                        else: 
                            i.unlink()
                    else:   
                        i.unlink()
            for inst in range(self.number_ins):
#                 Removed self.invoice_total from amount calculation (by Lekshmi Priya)
                if inst == 0:
                    self.env['installment.details'].create({'fee_for':'book',
                                                            'unit_id':self.id,
                                                            'percentage':self.booking_per,
                                                            'amount':self.price*(self.booking_per)*.01,
                                                            'name':str(self.name)+ '/'+str(inst)})
                    
                    self.env['installment.details'].create({'fee_for':'down',
                                                            'unit_id':self.id,
                                                            'percentage':self.downpayment_perc-self.booking_per,
                                                            'amount':self.price*(self.downpayment_perc-self.booking_per)*.01,
                                                            'name':str(self.name)+ '/'+str(inst+1)})
                else:
                    self.env['installment.details'].create({'fee_for':'installment','unit_id':self.id,'amount':0,'name':str(self.name)+ '/'+str(inst+1)})
#                 self.no_button = True

    
    @api.depends('installment_ids')
    def find_total_instllment(self):
        for items in self:
            t =0
            for ite in items.installment_ids:
                t += ite.amount
            items.instlm_total = t  
            items.remaining_total = items.price- t 
    
    
    @api.onchange('parking')
    def get_parking(self):
        x = self.env['zbbm.unit'].search([])
        m =[]
        for all in x:
            if all.parking_ids:
                for every in all.parking_ids:
                    m.append(every.id)
        if self.parking: 
            park =self.env['zbbm.car.park'].search([('building_id','=',self.building_id.id),('id','not in',m)])
            lis = {}
            z= []
            if park:
                for line in park:
                    z.append(line.id)
            lis['domain'] = {'parking_ids':[('id','in',z)]}       
            
            return lis                           

                
    @api.constrains('parking_ids')
    def _check_maximu(self):
        
        if len(self.parking_ids) > self.parking:
            raise Warning(_('maximum car park is %s'%(self.parking)))            
    

    def _get_followers1(self):
        users =self.env['res.users'].search([])
        li =''
        for all in users:
            if all.has_group('acccount.group_account_invoice'):
                if all.partner_id.email:
                    li += all.partner_id.email + ','
                else:
                    li = ''
            if all.has_group('zb_building_management.group_tijaria_admin')  :
                if all.partner_id.email:
                    li+=  all.partner_id.email +","
                else:
                    li = ''
#             if  li[-1]:
#                 if li[-1] == ',':
#                     li= li[:-1]  
            self.cc_email = li
        
     
    def _get_followers2(self):
        users =self.env['res.users'].search([])
        li =''
        for all in users:
            if all.partner_id.email:
                if all.has_group('acccount.group_account_invoice'):
                    li += all.partner_id.email + ','
                else:
                    li += ''
                if all.has_group('zb_building_management.group_tijaria_admin'):
                    li+=  all.partner_id.email +","
                else:
                    li+=''
                if all.has_group('zb_building_management.group_user_management'):
                    li+=  all.partner_id.email +","  
                else:
                    li+=''  
            else:
                li = ''
            
#             if  li[-1]:
#                 if li[-1] == ',':
#                     li= li[:-1]  
            self.cc_email2 = li    
#             self.cc_email2 = li
        
    

    @api.onchange('building_id','price')
    def onchanget_booking_fee(self):
#         '''This function return module id for voucher'''
# #         book_fee = self.env.get('zbbm.building').search([('id','=',self.building_id.id)])
        for unit in self:
            unit.method2 = False
            if unit.building_id.non_refund and not unit.method2:
                unit.booking_per = unit.building_id.non_refund
            else:
                unit.booking_per = 0
            if unit.building_id.downpayment_perc:
                unit.downpayment_perc =unit.building_id.downpayment_perc
            else:
                unit.downpayment_perc = 0
    
    
    @api.onchange('number_ins') 
    def onchange_con_fee(self):
        for unit in self:
            if unit.building_id.cont_preparation_fee:
                unit.cont_prepa_fee = unit.building_id.cont_preparation_fee     
            else:
                unit.cont_prepa_fee = 0      
                
    
    @api.onchange('booking_amount','method2')
    def method_2change(self):
        for unit in self:
            if unit.method2:
                if unit.price:
                    unit.booking_percent = (unit.booking_amount/unit.price)*100 
                else:
                    unit.booking_percent = 0
            else:
                unit.booking_percent = 0
                           
    
    def write(self, vals):
        '''Modified for Message Post'''
        if vals.get('booking_percent'):
            self.booking_per = vals['booking_percent']
        # msg = ''
        # if self.ids:
        #     if vals.get('price'):
        #         if vals['price'] != self.price:
        #             user = self.env['res.users'].browse(self._uid)
        #             msg = 'Price Changed to %s  by %s ' %(vals['price'],user.name)
        #             self.message_post(body=msg)
        res = super(zbbm_Unit, self).write(vals)
        return res
    
    
    @api.model
    def create(self, vals):
        if vals.get('booking_percent'):
            self.booking_per = vals['booking_percent']
        res = super(zbbm_Unit, self).create(vals)
        return res
    
    
    @api.onchange('bedroom')
    def get_park(self):
        if self.bedroom:
            self.parking = self.bedroom.no_car
        else:
            self.parking = 0.00
    
    
    def if_price(self):
        user_id = self.env['res.users'].browse(self.env.uid)
        for butt in self:
            if not user_id.has_group('zb_building_management.group_tijaria_admin'):
                butt.no_button = True
            else:
                butt.no_button = False
                

    def get_las_reser(self):
        for items in self:
            if items.reservation_date and items.reservation_time:
                items.las_reser = datetime.strptime(str(items.reservation_date), '%Y-%m-%d') + timedelta(days=items.reservation_time)
            else:
                items.las_reser = ''
                
    
    
    def name_get(self):
        res = []
        for rec in self:
            
            name = u'{} ({})'.format(rec.name, rec.state)
            res.append((rec.id, name))
        return res

    @api.model  
    def default_reservation_time(self):
        '''
            Default getting of reservation time from configuration 
        '''
        params = self.env['ir.config_parameter'].sudo()
        default_reservation_time = params.get_param('zb_building_management.reservation_time') or 0.0
        return default_reservation_time
   
    
    @api.model
    def generate_sellable_invoice(self):
        """
        Generates Automatic Invoice for sellable Units.
        """
        context = self._context or {}
        vals = {}
        cron_obj = self.env.get('ir.cron')
        updated_date = False
        #Schedular Selection
        ir_cron_ids = cron_obj.search([('model_id.model', '=', 'zb_building_management.model_zbbm_Unit'),('active','=',False)])
        if ir_cron_ids:
            last_date = ir_cron_ids.nextcall
            updated_last_date = datetime.strptime(str(last_date), '%Y-%m-%d %H:%M:%S')
        
        unit_ids = self.env.get('zbbm.unit').search([('state','in',['contract','book'])])   
        units = [unit.id for unit in unit_ids]
        installment_ids = self.env.get('installment.details').search([('unit_id','in',units),('invoice_date','=',str(date.today()))])
        for installmnts in  installment_ids:
            if not installmnts.invoice_id:
                installmnts.invoice_create()  
        return True    





    
    contract_number = fields.Integer('Number of Contracts',default = 1)
    cont_prepa_fee =fields.Float('Contract Preparation Fees')
    method2 = fields.Boolean('Use Booking(Amount)',default = False)
    booking_amount= fields.Float('Booking Amount')
    account_analytic_id = fields.Many2one('account.analytic.account',
        string='Cost Centre')
    no_button = fields.Boolean('no',default=False,compute="if_price")
    downpayment_perc = fields.Float(string='Downpayment Percentage (%)',readonly= False)
    booking_per = fields.Float('Booking fee (%)',readonly= False,default=1)
    cc_email = fields.Char('followers',compute='_get_followers1')
    cc_email2 = fields.Char('followers2',compute='_get_followers2')
    contract_paid = fields.Boolean('Contract Paid',default = False) 
    intr = fields.Integer('Invoice Time period')
    time_period = fields.Selection([('day', 'Days'),
        ('month','Months')],default='month')
    agent_id = fields.Many2one('res.users','Salesperson')
    instlm_total =  fields.Float(compute="find_total_instllment", string='Installment total', default=0,store = True)  
    invoice_count = fields.Integer(compute="_compute_invoice", string='# of Invoices', default=0)
#     invoice_ids = fields.Many2many('account.move','unit_invoice_rel','unit_id','move_id', string='Invoices')
    invoice_ids1 = fields.Many2many('account.move','invoice_unit_rel',string='Invoices')
    attachment_ids3 = fields.Many2many('ir.attachment', 'caddress_ir_attach_rel', 'address_id', 'attachadd_id', 'Unit Address Card')
    attachment_ids2 = fields.Many2many('ir.attachment', 'csignature_ir_attach_rel', 'sign_id', 'attachs_id', 'Commercial Registration Certificate')   
    attachment_ids1 = fields.Many2many('ir.attachment', 'class_ir_attach_rel', 'educat_id', 'attach_id', 'Signatory Authorization Letter')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'unit_attach_rel',
        'unitz_id', 'attachmentz_id', 'Attachments',required =True)
    attachment_ids4 = fields.Many2many('ir.attachment', 'class_ir_attach_book_rel', 'educat_id_book', 'attachbk_id', 'Booking Form')
    attachment_ids5 = fields.Many2many('ir.attachment', 'class_ir_attach_sale_rel', 'educat_id_sales', 'attachsa_id', 'Sales Agreement')
    name = fields.Char('Units', required=True, size=32)
    types = fields.Many2one('zbbm.type.unit',string ='Unit type')
    image = fields.Binary("Image") 
    unit = fields.Char('Unit Number', size=32)
    floor = fields.Integer('Floor Number')
    building_id = fields.Many2one('zbbm.building', 'Building', 
                    required=True, domain=[('building_type', 'in', ['sell','both']),('state','=','available')])
    
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    state = fields.Selection([
        ('new', 'New'),
        ('reserved','Reserved'),
        ('book', 'Booked'),
        ('contract', 'Contract Signed'),
        ('sold', 'Sold'),
        ('cancel','Cancelled')
        ], 'Status',default='new')
    
    unit_area = fields.Float('Unit Area')
    balcony_area = fields.Float('Balcony Area')
    total_area = fields.Float('Total Area')
    parking = fields.Integer('Number of Car Parks',compute="get_park")
    price =fields.Float('Selling Price',currency_field='currency_id',digits='Product Price',required=True,readonly = True,track_visibility='always', states={'new': [('readonly', False)]})
    buyer_id = fields.Many2one('res.partner','Client',readonly =True)
    contract_date = fields.Date('Contract Date')
    reservation_date= fields.Date('Reservation Date')
    payments_ids = fields.One2many('account.payment', 'unit_id', 'Payments')
    balance_invoice = fields.Float(compute='_calculate_invoice_total',
                     string='Outstanding Balance',digits='Product Price')
     
    invoice_total = fields.Monetary(string='Invoice Total',
        index=True, readonly=True, compute='_calculate_invoice_total',)
    balance_total = fields.Monetary(compute='_calculate_balance_total',readonly=True,
                     string='Balance Total',index =True)
    payment_total = fields.Monetary(compute='_calculate_payment_totals',
                    string='Payment Total',index =True,readonly =True
                    )
    downpayment = fields.Float('Total Down payment Fee',digits='Product Price',compute="get_down")
    number_ins = fields.Integer('Number of Installments')
    amount_per = fields.Float('Amount per installment',digits='Product Price')
    next_instalmnt = fields.Date('Next installment date')
    las_date = fields.Date('Last Invoice date')
    floor_plan = fields.Many2many('ir.attachment', 'unit_aflorrel',
        'uflr_id', 'attachmentf_id', 'Floor Plan')
    reservation_time = fields.Integer('Reservation time', default=default_reservation_time)
    installment_ids = fields.One2many('installment.details', 'unit_id', 'Installments'
                        )
    lead_id = fields.Many2one('crm.lead',string="Lead details",readonly=True)
    parking_ids = fields.Many2many('zbbm.car.park', 'unit_parking_rel',
        'unitd_id', 'parking_id', 'Car park')
    bedroom = fields.Many2one('zbbm.bedroom.unit', string ='Number of Bedrooms')
    las_reser = fields.Date('Reservation Ends', compute = 'get_las_reser')
    remaining_total = fields.Float('Remaining Total',compute ='find_total_instllment',store =True)
     
    expenses_count = fields.Integer(compute='get_expense',string='Expense')
    vendor_ids = fields.Many2many('account.move','vendor_unit_rel',string='Vendor Ids')
    commission_percent = fields.Float(string="Commission Percentage")
    booking_percent = fields.Float(string="Booking Percent")
    

class zbbm_type(models.Model):

    _name = "zbbm.type.unit"
    _description = "Building Types"

    name = fields.Char('Name')


class zbbm_bed_room(models.Model):
    _name = "zbbm.bedroom.unit"
    _description = "Bedroom"

    name = fields.Char('Name')
    no_car = fields.Integer('Number of Car Park')


class Installment(models.Model):

    _name = 'installment.details'

    def invoice_create(self):
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        for items in self:
            if not items.invoice_id:
                if items.unit_id.state in ['new','reserved']:
                    raise UserError(_('Unit should be booked to Client to generate invoice !'))
                     
                if items.unit_id.invoice_total >= items.unit_id.price:
                    raise Warning(_('Already Paid/Invoiced Full Amount'))
                if items.amount >= items.unit_id.price:
                    raise Warning(_('You need to pay only %s'%(items.unit_id.price)))    
    #             if items.unit_id.building_id.account_id:
    #                 acct_line_id = items.unit_id.building_id.account_id.id
    #             else:
    #                 acct_line_id = items.user_id.property_account_payable_id.id   
                if not items.unit_id.building_id.account_id:
                    journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                    if journal :
                        acct_id = journal[0].default_credit_account_id.id
                else:
                    acct_id = items.unit_id.building_id.account_id.id
                 
    #             journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
    #             if journal:
    #                 acct_id = journal[0].default_credit_account_id.id
                if items.unit_id.account_analytic_id:
                    analytic = items.unit_id.account_analytic_id.id
                else:
                    analytic = False 
                if self.fee_for:      
                    fee = dict(self.fields_get(allfields=['fee_for'])['fee_for']['selection'])[self.fee_for] 
                if not self.fee_for:
                    fee = False
                check = ['th',"st","nd","rd",]+["th"]*96
                try:
                    if self.name.split('/')[1] == '0':
                        order = ''
                    else:
                        order = check[int(self.name.split('/')[1])%100]
                         
                except:
                    order ='th' 
                if self.name.split('/')[1] == '0':
                    name = ''
                else:
                    name =  self.name.split('/')[1]  
                 
#                 config_obj = self.env.get('res.config.settings').search([('type','=', 'sale')], limit=1)
                params = self.env['ir.config_parameter'].sudo()        
                tax_ids = params.get_param('zb_building_management.default_sellable_tax_ids') or False,
                if tax_ids[0]:
                    temp = re.findall(r'\d+', tax_ids[0]) 
                    tax_list = list(map(int, temp))
                 
                vals = {
                        'name':str(items.name),
                        'partner_id': items.unit_id.buyer_id and items.unit_id.buyer_id.id,
                        'type': 'out_invoice',
#                         'account_id': items.unit_id.buyer_id.property_account_receivable_id.id,
                        'invoice_date_due': items.due_date,
                        'invoice_date': items.invoice_date,
                        'unit_id': items.unit_id and items.unit_id.id,
                        'building_id':items.unit_id.building_id and items.unit_id.building_id.id,
                        'lead_id':items.unit_id.lead_id and items.unit_id.lead_id.id,
                        'invoice_line_ids': [(0, 0, {
                                                    'name': '{} {} {} for Unit {} in {}, {}th floor , {}  , Area - {} Sqm, Sale price BD {}/- '.format(name,order,fee,self.unit_id.name,self.unit_id.building_id.name,self.unit_id.floor,self.unit_id.bedroom.name,self.unit_id.total_area,round(self.unit_id.price)),
                                                    'price_unit': items.amount,
                                                    'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
                                                    'quantity': 1,
    #                                                 'from_date': items.contract_date,
                                                    'account_analytic_id':analytic,
                                                    'account_id': acct_id,
                                                     })],
                            }
                invoice_id = self.env['account.move'].create(vals)
                items.unit_id.update({'invoice_ids1': [(4,invoice_id.id)]})
                if invoice_id.invoice_date:
                    items.unit_id.las_date = invoice_id.invoice_date
                if invoice_id.state =='open':
                    status= 'Posted'
                else:
                    status =  invoice_id.state  
                items.write({'state':status,
                             'invoice_id':invoice_id.id
                             })
             
            else:
                pass
 
     
    def get_status(self):
        for inv in self:
            if inv.invoice_id:
                if inv.invoice_id.state=='draft':
                    inv.state = 'Unposted'
                if inv.invoice_id.state=='posted':
                    inv.state = 'Posted'
                if inv.invoice_id.state=='paid':
                    inv.state= 'Paid'   
                if inv.invoice_id.state=='cancel' and not  inv.invoice_id.merged:
                    inv.state= 'Cancelled'
                if inv.invoice_id.state=='cancel' and inv.invoice_id.merged:  
                    inv.state= 'Merged to %s'%(inv.invoice_id.merged.name)
            else:
                inv.state = 'Unposted'
                     
   
    @api.onchange('percentage')
    def onchange_percentage(self):
        for items in self:
            if items.percentage:
                items.amount = items.percentage*.01*(items.unit_id.price)
            else:
                items.amount = 0
                

    name = fields.Char('Sl.No')
    amount = fields.Float('Amount', digits='Product Price')
    due_date = fields.Date('Due date')
    invoice_date = fields.Date('Invoice Date')
    invoice_id = fields.Many2one('account.move',readonly=True)
    state = fields.Char('Status',compute ="get_status",default ='Unposted',readonly=True)
    unit_id = fields.Many2one('zbbm.unit')    
    percentage = fields.Float('Percentage(%)')
    fee_for = fields.Selection([
        ('book', 'Booking Fee'),
        ('down', 'Down Payment Fee'),
        ('installment', 'Installment Fee'),
        ('final','Final Payment')
        ], 'Fee Type')


import base64
import binascii


class zbbm_module(models.Model):
    _name = "zbbm.module"
    _inherit = ['mail.thread','portal.mixin']
    _description = "Module / Flat"
    

    @api.model
    def create(self, vals):
        res = super(zbbm_module, self).create(vals)
        if vals.get('building_id'):
            building = self.env['zbbm.building'].browse(vals.get('building_id'))
            if building.state in ['available'] and not self.env.user.has_group('base.group_system'):
                raise Warning(_('You cannot create the unit!!'))
        return res

    #portal url
    def _compute_access_url(self):
        super(zbbm_module, self)._compute_access_url()
        for unit in self:
            unit.access_url = '/my/units/%s' % (unit.id)

    def action_flatdetails_send(self):
        '''
        This function opens a window to compose an email, with the edi flat template message loaded by default
        '''
        ids = self._ids
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.env.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference('zb_building_management', 'email_template_edi_zb_flat_management')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        ctx.update({
            'default_model': 'zbbm.module',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    
    def _calculate_invoice_total(self):
        '''Function to calculate total From all the valid invoices'''
        total = {}
        total_invoice =0.00
        for flat in self:
            total[flat.id] = 0.00
            if flat.invoice_ids:
                total_invoice = 0.00
                total_supplier_invoice = 0.00
                for invoice in flat.invoice_ids:
                    if invoice.state not in ['draft', 'cancel'] and invoice.type == 'out_invoice':
                        total_invoice = total_invoice + invoice.amount_total
                    if invoice.state not in ['draft', 'cancel'] and invoice.type =='out_refund':
                        total_invoice = total_invoice - invoice.amount_total
                total[flat.id] =  total_invoice
                flat.invoice_total = total_invoice
            else:
                flat.invoice_total = 0
        return total_invoice
    

    
    def _calculate_supplier_invoice_total(self):
        '''Function to calculate total From all the valid invoices'''
        total = {}
        total_supplier_invoice = 0.00
        for flat in self:
            total[flat.id] = 0.00
            if flat.invoice_ids:
                total_supplier_invoice = 0.00
                for invoice in flat.invoice_ids:
                    if invoice.state not in ['draft', 'cancel'] and invoice.type == 'in_invoice':
                        total_supplier_invoice = total_supplier_invoice + invoice.amount_total 
                    if invoice.state not in ['draft', 'cancel'] and invoice.type == 'in_refund':
                        total_supplier_invoice = total_supplier_invoice - invoice.amount_total
                total[flat.id] = total_supplier_invoice 
                flat.supplier_invoice_total = total_supplier_invoice
            else:
                flat.supplier_invoice_total = 0
        return total_supplier_invoice
    

    def _calculate_balance_total(self):
        '''Function to calculate total From the balance invoices'''
        total = {}
        total_invoice = 0.00
        for flat in self:
            total[flat.id] = 0.00
            if flat.invoice_ids:
                total_invoice = 0.00
                for invoice in flat.invoice_ids:
                    if invoice.state not in ['draft', 'cancel'] and invoice.type == 'out_invoice':
                        total_invoice = total_invoice
                total[flat.id] = total_invoice
                flat.balance_total = total_invoice
            else:
                flat.balance_total = total_invoice
        return total_invoice
    

    def _calculate_supplier_balance_total(self):
        '''Function to calculate total From the balance invoices'''
        total = {}
        total_invoice= 0.00
        for flat in self:
            total[flat.id] = 0.00
            if flat.invoice_ids:
                total_invoice = 0.00
                for invoice in flat.invoice_ids:
                    if invoice.state not in ['draft', 'cancel'] and invoice.type == 'in_invoice':
                        total_invoice = total_invoice 
                total[flat.id] = total_invoice
                flat.supplier_balance_total = total_invoice
            else:
                flat.supplier_balance_total = total_invoice
        return total_invoice
    

    def _get_order_invoice(self):
        '''Function retun the keys of Account Invoice'''
        result = {}
        for invoice in self.env.get('account.move'):
            result[invoice.module_id.id] = True
        return result.keys()
    

    def _calculate_payment_totals(self):
        '''Function to calculate total from all the valid payments'''
        total = {}
        total_payments_inbound = 0
        total_payments_outbound = 0

        for module in self:
            total[module.id] = 0.00
            if module.payments_ids:
                total_payments_inbound = 0.00
                total_payments_outbound = 0.00

                for payments in module.payments_ids:
                    if payments.state not in ['draft', 'cancel'] and payments.partner_type=='customer' and payments.payment_type  == 'inbound':
                         total_payments_inbound = total_payments_inbound + payments.amount
                    if payments.state not in ['draft', 'cancel'] and payments.partner_type=='customer' and payments.payment_type  == 'outbound':
                         total_payments_outbound = total_payments_outbound + payments.amount


                    module.payment_total = total_payments_inbound - total_payments_outbound
            else:
                module.payment_total = 0
    

    def _calculate_supplier_payment_total(self):
        '''Function to calculate total from all the valid payments'''
        total = {}
        total_payments_inbound = 0
        total_payments_outbound = 0
        for module in self:
            total[module.id] = 0.00
            if module.payments_ids:
                total_payments_inbound = 0.00
                total_payments_outbound = 0.00

                for payments in module.payments_ids:
                    if payments.state not in ['draft', 'cancel'] and payments.partner_type=='supplier' and payments.payment_type  == 'inbound':
                         total_payments_inbound = total_payments_inbound + payments.amount
                    if payments.state not in ['draft', 'cancel'] and payments.partner_type=='supplier' and payments.payment_type  == 'outbound':
                         total_payments_outbound = total_payments_outbound + payments.amount
                    module.supplier_payment_total = total_payments_outbound - total_payments_inbound 
            else:
                module.supplier_payment_total = 0
                

    def _get_payment(self):
        '''Function retun the keys of Account Voucher'''
        result = {}
        for voucher in self.env.get('account.payment'):
            result[voucher.module_id.id] = True
        return result.keys()

    
    def _get_order_invoice_line(self):
        '''Function retun the keys of Account Invoice'''
        result = {}
        for invoice_line in self.env.get('account.move.line'):
            if invoice_line.invoice_id and invoice_line.invoice_id.module_id:
                result[invoice_line.invoice_id.module_id.id] = True
        return result.keys()

    
    def _attachment_count(self):
        '''Function to get count of attachments from Building.
        '''
        for rec in self:
            attachment_ids = self.env.get('ir.attachment').search([('module_id','=',rec.id)])
            for module in self:
                if attachment_ids:
                    module.attachment_count = len(attachment_ids)
                else:
                    module.attachment_count =  0
#         return total

    
    def view_attach_from_flat(self):
        '''This function returns an action that display attachments from Flat.
        '''
#         action = self.env.ref('base.action_attachment')
         
        model, action_id = self.env.get('ir.model.data').get_object_reference('base', 'action_attachment')
        action = self.env.ref('base.action_attachment')
#         action = model.read(action_id)
        
        module = []
        mod_ids = self.env.get('ir.attachment').search([('module_id','=',self.id)])
        for idss in mod_ids:
            module.append(idss.id)
        
        result = {
            'name': action.name,
            'type': action.type,
            'view_mode': action.view_mode,
            'target': 'current',
            'res_model': action.res_model,
            'domain':[('id', 'in',module)],
            'context' : {'default_opportunity_id' : self.id},
            'help': "Click here to create new documents."
        }
        
#         module_ids = sum([mod_ids.ids], [])
#         kanban = self.env.ref('view_document_file_kanban', False)
#         kanban_id = kanban.id if kanban else False
#         result['views'] = [(kanban_id, 'kanban')]
#         result['res_id'] = module_ids
#         result['domain'] = str([('id','in',module_ids)])
#         if len(module_ids) == 1:
#             result['res_id'] = module_ids[0]
#         else:
#             result['domain'] = str([('id','in',module_ids)])
        return result
    
    

    @api.depends('attachment_ids3','attachment_ids2','attachment_ids1')
    def onget_partnerattach(self):
#         if self.attachment_ids3:
        for alls in self:
            for all in alls.attachment_ids3:
                x =self.env['ir.attachment'].create({'name':'%s'%(all.name),'res_model':'res.partner','res_id':alls.tenant_id.id,'mimetype':'text/csv','datas': all.datas})
            for all in  alls.attachment_ids2:
                y =self.env['ir.attachment'].create({'name':'%s'%(all.name),'res_model':'res.partner','res_id':alls.tenant_id.id,'mimetype':'text/csv','datas': all.datas})
            for all in  alls.attachment_ids1:
                z =self.env['ir.attachment'].create({'name':'%s'%(all.name),'res_model':'res.partner','res_id':alls.tenant_id.id,'mimetype':'text/csv','datas': all.datas})
            alls.dummy = not alls.dummy
    

    contract_number = fields.Integer('Number of Contracts',default = 1)  
    dummy = fields.Boolean('dummy',compute='onget_partnerattach',store =True)
    attachment_ids3 = fields.Many2many('ir.attachment', 'caddress_ir_att_rel', 'addre_id', 'attacadd_id', 'Lease Agreement')
    attachment_ids2 = fields.Many2many('ir.attachment', 'csignatur_attch_rel', 'signs_id', 'attinv_id', 'Inventory List')   
    attachment_ids1 = fields.Many2many('ir.attachment', 'class_ir_aggttach_rel', 'educaxt_id', 'attacxh_id', 'Handover Form')
    floor_plan = fields.Many2many('ir.attachment', 'uncidt_aflorrel',
        'ufsldr_id', 'attachmednjtf_id', 'Floor Plan')    
    
    account_analytic_id = fields.Many2one('account.analytic.account',
        string='Cost Centre')
    name = fields.Char('Module / Flat Number', required=True, size=32)
    attachment_count = fields.Integer(compute='_attachment_count',string='Attachments') 
    user_id =  fields.Many2one('res.users', 'Salesperson')
   
    image = fields.Binary("Image") 
    active =  fields.Boolean('Active',default=True)
    level = fields.Char('Level', size=32)
    
    building_id = fields.Many2one('zbbm.building', 'Building', 
                    required=True, domain=[('state', '=', 'available'),('building_type', 'in', ['rent','both'])])
    tenant_id = fields.Many2one('res.partner', 'Tenant', compute='get_tenant_id', store=True)
    tenant_dummy = fields.Many2one('res.partner', 'Tenant Dummy', related='tenant_id')
    state = fields.Selection([
        ('new', 'New'),
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('blocked', 'Blocked / Unavailable'),
        ('delisted', 'Delisted'),
        ], 'Status', readonly=True, copy=False, index=True,default='new')
    contract_date = fields.Date('Contract Date')
    rental_start_date = fields.Date('Lease Start Date')
    floor_area = fields.Float('Floor Area')
    bed_room = fields.Char('Bedroom')
    bath_room = fields.Integer('Bathroom')
    feature = fields.Selection([('bare', 'Unfurnished'),
        ('semi furnish', 'Semi Furnish'),
        ('fully furnish', 'Fully Furnish'),
        ], 'Feature', copy=False, help="Features", index=True)
    feature_description = fields.Text('Feature Description')
#     floor_plan = fields.Binary('Floor Plan')
    monthly_rate = fields.Float('Monthly Rent',digits='Product Price')
    advance = fields.Float('Advance',digits='Product Price')
    advance_paid = fields.Float('Paid Advance',digits='Product Price')
    
    
    invoice_ids = fields.One2many('account.move', 'module_id', 'Invoice')
    
    expense_new = fields.Float('Expense Test')#,compute= 'get_analytic'
    
    customer_invoice_ids = fields.One2many('account.move', 'module_id', 'Customer Invoices',
                        domain=[('type','=','out_invoice')])
     
    customer_refund_ids =  fields.One2many('account.move', 'module_id', 'Customer Refunds',
                        domain=[('type','=','out_refund')])
     
    supplier_invoice_ids = fields.One2many('account.move', 'module_id', 'Supplier Invoice',
                        domain=[('type','=','in_invoice')])
     
    supplier_refund_ids = fields.One2many('account.move', 'module_id', 'Supplier Refybds',
                        domain=[('type','=','in_refund')])
     
    payments_ids = fields.One2many('account.payment', 'module_id', 'Payments')
    
    last_invoice_date = fields.Date('Last Invoice Date')
    last_payment_date = fields.Date('Last Payment Date')
    rental_end_date = fields.Date('Lease End Date')
    type = fields.Many2one('zbbm.type', 'Type')
 
    
    invoice_total = fields.Float(compute='_calculate_invoice_total',
                     string='Invoice Total',digits='Product Price')
     
    payment_total = fields.Float(compute='_calculate_payment_totals',
                    string='Payment Total',digits='Product Price'
                    )
     
    supplier_payment_total= fields.Float(compute='_calculate_supplier_payment_total',
                    string='Supplier Payment Total',digits='Product Price')
     
    supplier_invoice_total=fields.Float(compute='_calculate_supplier_invoice_total',
                     string='Supplier Invoice Total',digits='Product Price')
     
    balance_total = fields.Float(compute='_calculate_balance_total',
                     string='Balance Total',digits='Product Price')
     
    supplier_balance_total =fields.Float(compute='_calculate_supplier_balance_total',
                     string='Balance Total',digits='Product Price')
    
    status = fields.Selection([('asigned','Amendment Lease Signed'),('new', 'New lease Signed'),
        ('legal', 'Legal'),('vacant','Vacant'),('process','In Process'),('pending','Amendment Lease Pending'),('notice','On notice period')],string = 'Contract Status',default ='vacant')
    
    res_com = fields.Selection([
                    ('res', 'Residential'),
                    ('com', 'Commercial'),
                    ('both','Residential or Commercial')
                    ],related='building_id.res_com',string='Building Design')
    
    potential_rent = fields.Float(string='Potential Rent',digits='Product Price'
                    )
    agreement_ids = fields.One2many('zbbm.module.lease.rent.agreement', 'subproperty', 'Agreements')
    owner_id = fields.Many2one('res.partner','Owner')
    managed = fields.Boolean('Managed',default=False)
    
    

    def get_tenant_id(self): 
        for val in self:
            if val.agreement_ids:
                count = 0
                for rec in val.agreement_ids:
                    if rec.state=='active':
                        count+=1
#                         print(rec.tenant_id.id)
                    val.update({'tenant_id': rec.tenant_id.id})
    
    
    def name_get(self):
        res = []
        for rec in self:
            name1 = u'{} - {}'.format( rec.building_id.name,rec.name)
            res.append((rec.id, name1))
        return res
  
    
    
    def write(self, vals):
        '''Modified for Message Post'''
        msg = ''
        if self.ids:
            if vals.get('tenant_id', False):
                tenant = self.env.get('res.partner').browse(vals['tenant_id'])
                msg = 'Tenant Changed to %s \n' %tenant.name
            if vals.get('monthly_rate', False):
                msg = msg + '<b>Monthly Rate Changed </b> to %.3f </br>' %vals['monthly_rate']
            if vals.get('contract_date', False):
                msg = msg + '<b>Contract Date Changed to </b> %s </br>' %str(vals['contract_date'])
#             if vals.get('rental_start_date', False):
#                 msg = msg + '<b> Lease Start Date Changed to </b> %s' %str(vals['rental_start_date'])
#             if vals.get('rental_end_date', False):
#                 msg = msg + '<b> Lease End Date Changed to </b> %s' %str(vals['rental_end_date'])    
            if msg:
                self.message_post(body=msg)
                     
        res = super(zbbm_module, self).write(vals)
        return res
    
    
    def make_available(self):
        _logger.info("111111111111111111111111111111111111")
        '''State Change from New to Available'''
        msg = 'Flat %s Available. %s vacated'%(self.name,self.tenant_id.name)
        self.sudo().message_post(body=msg)
        self.sudo().write({'tenant_id':False,'rental_start_date':False,'rental_end_date':False,'status':'vacant','attachment_ids1':[(6, 0, [])],'attachment_ids2':[(6, 0, [])],'attachment_ids3':[(6, 0, [])],'state': 'available'})
        return True
    
    
    def action_occupied(self):
        '''State Change from Available to Occupied'''
        for flat in self:
            cc = self.env['zbbm.module'].search([('name', '=', self.name),('building_id','=',self.building_id.id),('state','=','occupied')])
            
            if cc:
                raise Warning(_('Flat is already in use'))
            else:   
                if not flat.tenant_id:
                    raise Warning(_('Please enter the Tenant'))
                if not flat.building_id.building_address:
                    raise Warning(_('Please enter the Building Address'))
                if flat.monthly_rate <= 0:
                    raise Warning(_('Please enter the Monthly Rate'))
#                 if not flat.rental_start_date:
#                     raise Warning(_('Please enter the Lease Start Date'))
                flat.write({'state': 'occupied'})
        return True
    
    
    def action_delist(self):
        '''State Change from Available to Delist'''
        self.write({'state': 'delisted'})
        return True
    
    
    def action_unavailable(self):
        '''State Change from Available to Unavailable'''
        self.write({'state': 'blocked'})
        return True
    
    
    def action_comment_generate(self,updated_last_date, flat):
        '''This function return comment for invoice'''
        first_day_of_previous_month = updated_last_date - timedelta(days=30)
        first_day_of_previous_month_date = str(first_day_of_previous_month).split(' ', 1)[0]
        first_day_of_previous_month_date_format = datetime.strptime(str(first_day_of_previous_month_date), '%Y-%m-%d').strftime('%B %Y') or ''
        building_street = flat.building_id.building_address.street
        building_road = flat.building_id.building_address.street2
        building_city = flat.building_id.building_address.city
        return 'Rent payment for the month of %s, Flat/ %s %s %s' %(first_day_of_previous_month_date_format or '', building_street or '', building_road or '', building_city or '')
    
    
    def get_month(self,date, cron_date):
         '''This function return Months'''
         months = 0.00
         days = 0.00
         invoice_start_date = datetime.strptime(str(date), '%Y-%m-%d')
         months_relatve = relativedelta.relativedelta(invoice_start_date, cron_date)
         months = abs(float(months_relatve.months)) + abs(round(float(months_relatve.days)/30, 3))
         return months
    
    
    
class LeaseRentAgreement(models.Model):

    _name = 'zbbm.module.lease.rent.agreement'
    _description = "Lease/Rental Agreement"
    _inherit = ['mail.thread','portal.mixin']
#     _rec_name = 'tenant_id'
    
    reference_no =  fields.Char('Reference Number',readonly=True,copy=False)
    tenant_id = fields.Many2one('res.partner', 'Tenant')
    building_id = fields.Many2one('zbbm.building',"Building")
    subproperty = fields.Many2one('zbbm.module', 'SubProperty')
    agreement_start_date = fields.Date('Agreement Start Date')
    agreement_end_date = fields.Date('Agreement End Date')
    invoice_date = fields.Integer('Invoice Day',help="Day of Month")
    agent = fields.Many2one('res.partner', 'Agent')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    monthly_rent = fields.Float(string='Monthly Rent',digits='Product Price')
    ewa_limit = fields.Float(string='EWA Limit',digits = (12,3) )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active','Active'),
        ('expired', 'Expired'),
        ('terminate', 'Terminate')
        ], default='draft', track_visibility='always')  
    invoices_count = fields.Integer(compute='_compute_invoice',string='Invoice Counts') 
    invoice_ids = fields.Many2many('account.move','move_invoice_rel',string='Invoices')
    expenses_count = fields.Integer(compute='get_invoices',string='Expense')
    vendor_ids = fields.Many2many('account.move','move_vendor_rel',string='Vendor Ids')
    attachment_ids3 = fields.Many2many('ir.attachment', 'caddress_ir_att_rel1', 'addre_id', 'attacadd_id', 'Lease Agreement')
    attachment_ids2 = fields.Many2many('ir.attachment', 'csignatur_attch_rel1', 'signs_id', 'attinv_id', 'Inventory List')   
    attachment_ids1 = fields.Many2many('ir.attachment', 'class_ir_aggttach_rel1', 'educaxt_id', 'attacxh_id', 'Handover Form')
    floor_plan = fields.Many2many('ir.attachment', 'uncidt_aflorrel1',
        'ufsldr_id', 'attachmednjtf_id', 'Floor Plan')
    commission_percent = fields.Float(string="Commission Percentage")
    vendor_id = fields.Many2one('account.move',string="Vendor Bill")
    vendor_refund_id = fields.Many2one('account.move',string="Vendor Refund Bill")
    termination_date = fields.Date('Termination Date')
    contract_status = fields.Selection([
        ('in_process', 'In Process'),
        ('signed','Signed'),
        ('notice_period', 'Notice Period'),
        ('no_contract', 'No Contract')
        ], default='no_contract')
    security_deposit = fields.Float(string='Advance/Security Deposit ',digits = (12,3))
    user_id =  fields.Many2one('res.users', 'User',default=lambda self: self.env.user)


    #portal url
    def _compute_access_url(self):
        super(LeaseRentAgreement, self)._compute_access_url()
        for agreement in self:
            agreement.access_url = '/my/agreements/%s' % (agreement.id)

    
    def name_get(self):
        res = []
        for rec in self:
            name_format = '[%s][%s - %s] %s'%(rec.reference_no,rec.building_id.name,rec.subproperty.name,rec.tenant_id.name)
            res.append((rec.id, name_format))
        return res
    
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if name:
            if operator in ('ilike', 'like', '=', '=like', '=ilike'):
                domain = ['|', '|','|',('reference_no', operator, name), ('tenant_id.name', operator, name),('building_id.name', operator, name),('subproperty.name', operator, name)]
                return self.search(domain, limit=limit).name_get()
        return super(LeaseRentAgreement, self).name_search(name, args, operator, limit)
    
    
    @api.onchange('building_id')
    def assign_commision(self):
        for order in self:
            if order.building_id.commission_percent:
                order.commission_percent = order.building_id.commission_percent
            else:
                order.commission_percent = 0
    
   
    @api.onchange('subproperty')
    def assign_monthly_rent(self):
        for order in self:
           
            if order.subproperty.monthly_rate:
                order.monthly_rent = order.subproperty.monthly_rate
            else:
                order.monthly_rent = 0
                
    
                
    @api.model
    def create(self,vals):
        if vals.get('reference_no', '/') == '/':
            vals['reference_no'] = self.env['ir.sequence'].get('lease.agreement') or '/'
        if vals.get('invoice_date',False):    
            if vals['invoice_date'] > 31:
                raise UserError(_("Invoice Day Cannot Be Greater Than 31"))
        
        res = super(LeaseRentAgreement, self).create(vals)
        return res   
    
    
    def write(self,vals):
        res = super(LeaseRentAgreement, self).write(vals)
        if self.invoice_date > 31:
            raise UserError(_("Invoice Day Cannot Be Greater Than 31"))
        return res   
               

    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.move'].search([('partner_id','=',self.tenant_id.id),('module_id','=',self.subproperty.id),('type','=','out_invoice')])
            order.invoices_count = len(invoices) 
            

    def get_invoices(self):  
        for order in self:
            invoices = self.env['account.move'].search([('partner_id','=',self.agent.id),('module_id','=',self.subproperty.id),('type','in',['in_invoice','in_refund'])])
            order.expenses_count = len(invoices) 
        

    def action_view_invoice(self):
        invoices = self.env['account.move'].search([('partner_id','=',self.tenant_id.id),('module_id','=',self.subproperty.id),('type','=','out_invoice')])

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
        invoices = self.env['account.move'].search([('partner_id','=',self.agent.id),('module_id','=',self.subproperty.id),('type','in',['in_invoice','in_refund'])])
        
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    

    @api.onchange('agreement_start_date')
    def onchange_agreement_start_date(self):
        if self.agreement_start_date:
            start = self.agreement_start_date
            start_day_obj = datetime.strptime(str(start), "%Y-%m-%d")
            end_date = start_day_obj + relativedelta.relativedelta(days=-1,years=1)
            self.agreement_end_date = end_date

            
    def set_to_active(self):
        
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        for items in self:
            if items.subproperty:
                subproperty = items.subproperty

                subproperty.monthly_rate = items.monthly_rent
                subproperty.tenant_id = items.tenant_id.id
                if subproperty.state == 'available':
                    subproperty.state='occupied'
                elif subproperty.state == 'occupied':
                    raise UserError('Already Occuped!!!!')
            else:
                raise UserError('Please Assign Subproperty !!!')
            items.state='active'
            
            if not items.tenant_id:
                raise Warning(_('Please Assign Tenant'))
        
#             if not items.agent:
#                 raise Warning(_('Please Assign Agent'))
            if not items.subproperty.building_id.account_id:
                journal = self.env.get('account.journal').search([('type','=', 'purchase')], limit=1)
                if journal :
                    acct_id = journal[0].default_debit_account_id.id
            else:
                acct_id = items.subproperty.building_id.expense_account_id.id
            
            if items.subproperty.account_analytic_id:
                analytic = items.subproperty.account_analytic_id.id
            else:
                analytic = '' 
                    
            if items.subproperty.building_id.building_address.street:
                street = items.subproperty.building_id.building_address.street
            else:
                street = '' 
                
            if items.subproperty.building_id.building_address.street2:
                street2 = items.subproperty.building_id.building_address.street2
            else:
                street2 = ''
            
            if items.subproperty.building_id.building_address.city:
                city = items.subproperty.building_id.building_address.city
            else:
                city = ''
                
            if items.subproperty.building_id.building_address.country_id:
                country = items.subproperty.building_id.building_address.country_id.name
            else:
                country = ''
                    
            end_date = datetime.strptime(str(items.agreement_end_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',       
            start_date = datetime.strptime(str(items.agreement_start_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',  
            params = self.env['ir.config_parameter'].sudo()        
            tax_ids = params.get_param('zb_building_management.default_expense_tax_ids') or False,
            _logger.info('--------------Tax Ids---------->>>>>>>>>>>>>>>>> (%s).', tax_ids[0])
            if tax_ids[0]:
                temp = re.findall(r'\d+', tax_ids[0]) 
                tax_list = list(map(int, temp))  
            
#             company_id = self.env['res.company']._company_default_get()  
            currnet_user = self.env['res.users'].browse(self._uid)
            company_id = currnet_user.company_id    
            vals = {
#                     'name':items.reference_no,
                    'invoice_payment_term_id':items.agent.property_supplier_payment_term_id.id if items.agent.property_supplier_payment_term_id else '',
                    'partner_id': items.agent.id,
                    'type': 'in_invoice',
#                     'account_id': items.agent.property_account_payable_id.id,
                    'comment': company_id.agent_commission_comment,
                    'module_id': items.subproperty.id,
                    'building_id':items.subproperty.building_id and items.subproperty.building_id.id,
                    'lease_id':items.id,
                    'invoice_line_ids': [(0, 0, {
                                                'name': '{},{},{},{},Area {},{}, Rent Period:{}  to {}, Tenant:{},  {}% of {}'.format(items.building_id.name,items.subproperty.name,street,street2,city,country,start_date[0],end_date[0],items.tenant_id.name,items.commission_percent,items.monthly_rent),
                                                'price_unit': items.monthly_rent *(items.commission_percent/100) if items.commission_percent else 0,
                                                'quantity': 1,
                                                'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
                                                'account_analytic_id':analytic,
                                                'account_id': acct_id,
                                                 })],
                        }
            
            tenant_vals = {
                'building_id':items.building_id,
                'module_id':items.subproperty,
                'monthly_rent':items.monthly_rent,
                'lease_start_date':items.agreement_start_date,
                'lease_end_date':items.agreement_end_date
                }
            if items.tenant_id:
                tenant_ids = self.env['res.partner'].search([('id','=',items.tenant_id.id)])
                tenant_ids.update(tenant_vals)
            if items.agent:
                invoice_id = self.env['account.move'].create(vals)
                items.vendor_id = invoice_id.id
        
    

    def set_to_draft(self):
        for rec in self:
            if rec.subproperty:
                subproperty = rec.subproperty
                rec.subproperty.make_available()
#             if subproperty.state == 'occupied':
#                 subproperty.state='available'
            if rec.vendor_id:
                if rec.vendor_id.state == 'open' and not rec.state == 'paid':
                    rec.vendor_id.state = 'cancel'
                    rec.state='draft'
                elif rec.state == 'paid':
                    raise Warning(_('Agent Commission is Paid/Refunded'))
                else:
                    if rec.vendor_id.state =='draft':
                        rec.vendor_id.unlink()
                        rec.state='draft'
            else:
                rec.state='draft'
                    
            if rec.vendor_refund_id:
                if rec.vendor_refund_id.state == 'open' and not rec.state == 'paid':
                    rec.vendor_refund_id.state = 'cancel'
                    rec.state='draft'
                elif rec.state == 'paid':
                    raise Warning(_('Agent Commission is Paid/Refunded'))
                else:
                    if rec.vendor_refund_id.state =='draft':
                        rec.vendor_refund_id.unlink()
                        rec.state='draft'
            else:
                rec.state='draft'
        

    def set_to_expired(self):
        for rec in self:
            subproperty = rec.subproperty
            subproperty.make_available()
#             subproperty.state = 'available'
            subproperty.tenant_id = self.tenant_id.id
            rec.state='expired'
    
    def set_to_terminate(self):
        for rec in self:
            subproperty = rec.subproperty
            subproperty.make_available()
#             subproperty.state = 'available'
            subproperty.tenant_id = self.tenant_id.id
#             subproperty.action_delist()
            rec.termination_date = datetime.today()
            rec.state='terminate'
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        for items in self:
            if not items.subproperty.building_id.account_id:
                journal = self.env.get('account.journal').search([('type','=', 'purchase')], limit=1)
                if journal :
                    acct_id = journal[0].default_credit_account_id.id
            else:
                acct_id = items.subproperty.building_id.account_id.id
            
            if items.subproperty.account_analytic_id:
                analytic = items.subproperty.account_analytic_id.id
            else:
                analytic = '' 
                    
            if items.subproperty.building_id.building_address.street:
                street = items.subproperty.building_id.building_address.street
            else:
                street = '' 
                
            if items.subproperty.building_id.building_address.street2:
                street2 = items.subproperty.building_id.building_address.street2
            else:
                street2 = ''
            
            if items.subproperty.building_id.building_address.city:
                city = items.subproperty.building_id.building_address.city
            else:
                city = ''
                
            if items.subproperty.building_id.building_address.country_id:
                country = items.subproperty.building_id.building_address.country_id.name
            else:
                country = ''
            
            
            end_date = datetime.strptime(str(items.agreement_end_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',       
            start_date = datetime.strptime(str(items.agreement_start_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',  
            
            no_of_dates = (datetime.strptime(str(items.agreement_end_date), '%Y-%m-%d')-datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')).days
            if items.vendor_id.state == 'draft':
                raise UserError('Please Validate The Vendor Bill')
            
#             if not items.agent:
#                 raise Warning(_('Please Assign Agent'))
                
            else:
                vals = {
                        'partner_id': items.agent.id,
                        'invoice_payment_term_id':items.agent.property_supplier_payment_term_id.id if items.agent.property_supplier_payment_term_id else '',
                        'ref':items.vendor_id.name,
                        'type': 'in_refund',
                        'lease_id':items.id,
#                         'account_id': items.agent.property_account_payable_id.id,
    #                     'date_due': items.agreement_end_date,
                        'module_id': items.subproperty.id,
                        'building_id':items.subproperty.building_id and items.subproperty.building_id.id,
                        'invoice_line_ids': [(0, 0, {
                                                    'name': '{},{},{},{},Area {},{}, Rent Period:{}  to {}, Tenant:{}'.format(items.building_id.name,items.subproperty.name,street,street2,city,country,start_date[0],end_date[0],items.tenant_id.name),
                                                    'price_unit': (no_of_dates * ((items.monthly_rent)/30)),
                                                    'quantity': 1,
    #                                                 'from_date': items.contract_date,
                                                    'account_analytic_id':analytic,
                                                    'account_id': acct_id,
                                                     })],
                            }
                if items.agent:
                    invoice_id = self.env['account.move'].create(vals)
                    items.vendor_refund_id = invoice_id.id
        
        
    def action_set_renew(self):
        today = datetime.today()
        end = self.agreement_end_date
        end_day_obj = datetime.strptime(str(end), "%Y-%m-%d")
        new_date = end_day_obj + relativedelta.relativedelta(days=1)
        
        end_date = self.agreement_end_date
        new_end_day_obj = datetime.strptime(str(end_date), "%Y-%m-%d")
        new_end_date = new_end_day_obj + relativedelta.relativedelta(days=-1,years=1)
            
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
            'contract_status' : 'no_contract'
            }

        view_id = self.env.ref('zb_building_management.view_lease_rent_agreement_form').id 
        context = self._context
        res = self.copy()
        super(LeaseRentAgreement, res).write(vals)
        
 
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

    
    @api.model
    def action_invoice_generate(self):
        ''' Scheduler Function for Invoice Generation'''

        context = self._context or {}
        vals = {}
        cron_obj = self.env['ir.cron']
        updated_date = False
        updated_last_date = False
        ir_cron_ids = cron_obj.search([('model_id.model', '=', 'zbbm.module.lease.rent.agreement'),('active','=',False)])
        if ir_cron_ids:
            last_date = ir_cron_ids.nextcall
            updated_last_date = datetime.strptime(str(last_date), '%Y-%m-%d %H:%M:%S')
        agreement_ids = self.search([('state', '=', 'active')])
        today = datetime.now().date()
        first_day = today.strftime('%Y-%m-01')
        first_day_obj = datetime.strptime(str(first_day), "%Y-%m-%d")
        next_month_first = first_day_obj + relativedelta.relativedelta(months=+1)
        month_last = next_month_first + relativedelta.relativedelta(days=-1)
        for agreement in agreement_ids:
            if agreement.invoice_date in [28,29,30,31]:
                day_to_invoice = month_last.day
            else:
                day_to_invoice = today.day
            if agreement.invoice_date == day_to_invoice and day_to_invoice==updated_last_date.day:
                company_id = self.env.get('res.users').company_id.id
                if not agreement.building_id.account_id:
                    journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                    if journal :
                        acct_id = journal[0].default_credit_account_id.id
                else:
                    acct_id = agreement.building_id.account_id.id
                description = 'Rental payment for the Period for the Month '+today.strftime("%B")+' '+today.strftime("%Y")
                params = self.env['ir.config_parameter'].sudo()        
                tax_ids = params.get_param('zb_building_management.default_rental_tax_ids') or False,
                if tax_ids[0]:
                    temp = re.findall(r'\d+', tax_ids[0]) 
                    tax_list = list(map(int, temp))
                vals = {
                      'partner_id': agreement.tenant_id.id,
                      'type': 'out_invoice',
#                       'account_id': agreement.tenant_id.property_account_receivable_id.id,
                      'invoice_date': last_date,
                      'building_id': agreement.building_id.id,
                      'module_id': agreement.subproperty.id,
                      'lease_id': agreement.id,
                      'comment': description,
                      'invoice_line_ids': [(0, 0, {
                                            'name': description,
                                            'price_unit': agreement.monthly_rent,
                                            'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
                                            'quantity': 1,
                                            'account_id': acct_id,
                                            })],
                    }
                invoice_id = self.env.get('account.move').create(vals)
                invoice_id.action_post()
        return True   
    



class res_partner(models.Model):

    _inherit = 'res.partner'
    _description = "Partners"
    
    
    @api.model
    def default_get(self,fields):
        res = super(res_partner, self).default_get(fields)
        if self._context.get('tenant'):
            res.update({
            'is_tenant': True ,
            'customer' : False
                    })
        elif self._context.get('module_tenant'):
            res.update({
            'is_tenant': True,
            'customer' : True
                    })
        return res

    
    
    @api.onchange('customer')
    def prospect_customer_change(self):
        if self.customer and self.is_a_prospect:
            self.is_a_prospect = False


    @api.onchange('is_a_prospect')
    def prospect_change(self):
        if self.is_a_prospect and self.customer:
            self.customer = False


    @api.constrains('customer', 'is_a_prospect')
    def partner_prospect_check(self):
        for partner in self:
            if partner.customer and partner.is_a_prospect:
                raise ValidationError(_(
                    "Partner '%s' cannot be both a prospect and a customer")
                    % self.name_get()[0][1])


    building_id = fields.Many2one('zbbm.building',"Building",readonly=True)
    nationality = fields.Many2one('res.country','Nationality')
    passport = fields.Char('Passport No')
    is_tenant = fields.Boolean('Tenant')
    customer = fields.Boolean('Customer', help="Check this box if this contact is a customer.")
    supplier = fields.Boolean('Vendor', help="Check this box if this contact is a Supplier.")           
    is_a_prospect = fields.Boolean('is a Prospect')
    module_id = fields.Many2one('zbbm.module',string="Flat/Office",readonly=True)
    lease_start_date = fields.Date(string="Lease Start Date",readonly=True)
    lease_end_date = fields.Date(string="Lease End Date",readonly=True)
    monthly_rent = fields.Float(string="Monthly Rent",digits='Product Price',store=True,readonly=True)
    amount_due = fields.Monetary(string="Amount Due",digits='Product Price',related="credit",readonly=True)
    is_an_agent = fields.Boolean('Agent')

    @api.constrains('cpr', 'passport')
    def _check_cpr_passport_constraint(self):
        for contact in self:
            partner = self.env['res.partner']
            domain1 = [('cpr', '=', contact.cpr), ('id', '!=', self.id)]
            domain2 = [('passport', '=', contact.passport), ('id', '!=', self.id)]
            if contact.cpr and partner.search(domain1):
                raise ValidationError(_('CPR %s already exists!') % self.cpr)
            elif contact.passport and partner.search(domain2):
                raise ValidationError(_('Passport %s already exists!') % self.passport)
            else:
                pass
                

class zbbm_type(models.Model):

    _name = "zbbm.type"
    _description = "Buildings Type"

    name=fields.Char('Type', required=True, size=32)
    

class zbbm_car_park(models.Model):
    
    _name = 'zbbm.car.park'
    _description = "Car Parking Slot"
    
    name=fields.Char('Parking Number', required=True, size=32)
    building_id = fields.Many2one('zbbm.building',string="Building")



# DBclass account_voucher(models.Model):
# 
#     _inherit = 'account.voucher'
#     _description = "Account Voucher model Fields Modification"
#    
#     @api.model
#     def default_module_id(self):
#         '''This function return module id for voucher'''
#         module_id = False
#         context = self._context
#         if context.get('active_model', '') and context['active_model'] == 'account.move':
#             if context.get('active_id', False):
#                 invoice = self.env.get('account.move').browse(context['active_id'])
#                 if invoice.module_id:
#                     module_id = invoice.module_id.id
#                 else:
#                      module_id = False
#         return module_id
#     
#     @api.model
#     def default_building_id(self):
#         '''This function return building id for voucher'''
#         building_id = False
#         context = self._context
#         if context.get('active_model', '') and context['active_model'] == 'account.move':
#             if context.get('active_id', False):
#                 invoice = self.env.get('account.move').browse(context['active_id'])
#                 if invoice.building_id:
#                     building_id = invoice.building_id.id
#                 else:
#                     building_id = False
#         return building_id
#     
#     @api.model
#     def default_comment(self):
#         '''This function return addtional log for voucher'''
#         module_id = False
#         context = self._context
#         log = ''
#         if context.get('active_model', '') and context['active_model'] == 'account.move':
#             if context.get('active_id', False):
#                 invoice = self.env.get('account.move').browse(context['active_id'])
#                 if invoice.comment:
#                     log = invoice.comment
#                 else:
#                     log = False
#         return log
#     
#     @api.model
#     def default_check_date(self):
#         '''This function return check date for customer payment voucher'''
#         check_date = False
#         context = self._context
#         if context.get('active_model', '') and context['active_model'] == 'account.voucher':
#             if context.get('active_id', False):
#                 voucher = self.env.get('account.voucher').browse(context['active_id'])
#                 if voucher.check_date:
#                     date = voucher.check_date
#                 else:
#                     date = datetime.now()
#         else:
#             date = datetime.now()
#         return date
#     
#     @api.onchange('building_id')
#     def hide_units_modules(self):
#         for all in self:
#             if all.building_id:
#                 if all.building_id.building_type =='rent':
#                     all.hide1 =False
#                     all.hide2 =True
#                 else:
#                     all.hide2 =False
#                     all.hide1 =True
#         
# 
#     building_id = fields.Many2one('zbbm.building', 'Building', domain=[('state', '=', 'available')],default=default_building_id)
#     module_id =fields.Many2one('zbbm.module', 'Flat/Office',default=default_module_id)
#     unit_id = fields.Many2one('zbbm.unit', 'Unit')
#     logo =fields.Text('comment',default=default_comment)
#     check_date =fields.Date('Check Date',default=default_check_date)
#     hide1 = fields.Boolean('Hide1',default =False,compute = 'hide_units_modules')
#     hide2 = fields.Boolean('Hide2',default =False,compute = 'hide_units_modules')








