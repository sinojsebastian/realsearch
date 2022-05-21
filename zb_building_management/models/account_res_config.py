# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import ast
from odoo import models, fields, api, _


class AccountConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    period_lock_date = fields.Date(string="Lock Date for Non-Advisers", related='company_id.period_lock_date', help="Only users with the 'Adviser' role can edit accounts prior to and inclusive of this date. Use it for period locking inside an open fiscal year, for example.")
    fiscalyear_lock_date = fields.Date(string="Lock Date", related='company_id.fiscalyear_lock_date', help="No users, including Advisers, can edit accounts prior to and inclusive of this date. Use it for fiscal year locking for example.")
    agent_commission_comment = fields.Text(String="Agent Commission Text", related='company_id.agent_commission_comment') 
    sellable_tax_ids_default = fields.Many2many('account.tax', 'config_sell_tax_rel', 'config_id', 'tax_id', string='Default Sellable Tax')
    rental_tax_ids_default = fields.Many2many('account.tax', 'config_rent_tax_rel', 'config_id', 'tax_id', string="Default Rental Tax")
    expense_tax_ids_default = fields.Many2many('account.tax', 'config_purchase_tax_rel', 'config_id', 'tax_id', string="Default Property Expense Tax")
    
    @api.model
    def get_values(self):
        res = super(AccountConfigSettings, self).get_values()
        sellable_tax_ids_default = self.env['ir.config_parameter'].sudo().get_param('zb_building_management.sellable_tax_ids_default')
        rental_tax_ids_default = self.env['ir.config_parameter'].sudo().get_param('zb_building_management.rental_tax_ids_default')
        expense_tax_ids_default = self.env['ir.config_parameter'].sudo().get_param('zb_building_management.expense_tax_ids_default')
        
        if sellable_tax_ids_default == False:
            res.update(sellable_tax_ids_default=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(sellable_tax_ids_default=[(6, 0, ast.literal_eval(sellable_tax_ids_default))],)
        
        if rental_tax_ids_default == False:
            res.update(rental_tax_ids_default=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(rental_tax_ids_default=[(6, 0, ast.literal_eval(rental_tax_ids_default))])
            
        if expense_tax_ids_default == False:
            res.update(expense_tax_ids_default=[(6, 0, ast.literal_eval('None'))],)
        else:
            res.update(expense_tax_ids_default=[(6, 0, ast.literal_eval(expense_tax_ids_default))])
        
        return res



    def set_values(self):
        super(AccountConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('zb_building_management.sellable_tax_ids_default', self.sellable_tax_ids_default.ids)
        set_param('zb_building_management.rental_tax_ids_default', self.rental_tax_ids_default.ids)
        set_param('zb_building_management.expense_tax_ids_default', self.expense_tax_ids_default.ids)
        


