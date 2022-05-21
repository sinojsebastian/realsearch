# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>)..
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

from odoo import api, fields, models


class res_company(models.Model):

    _inherit = "res.company"
    _description = "Company inheritance"

    vat_no = fields.Char('Vat NO', size=32)


    def _get_euro(self):
        '''Overriding the base function to set currency as BHD'''
        currency_obj = self.pool.get('res.currency')
        res = currency_obj.search([('name', '=', 'BHD')])
        return res and res[0] or False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
