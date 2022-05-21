# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2020 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api, fields, _
from odoo.exceptions import UserError

class vat_report_wizard(models.TransientModel):
    """Wizard for Purchase And Sales VAT report"""
    _name = "wizard.vat.report"
    
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    type = fields.Selection([('purchase','Purchase'),
                                        ('sales','Sales')], string="Report")

    
    def print_report(self):
        self.ensure_one()
        return self.env.ref('zb_purchaseandsales_vat_report.report_vat_xlsx').report_action(self)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: