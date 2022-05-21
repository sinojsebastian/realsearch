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


class res_partner(models.Model):

    _inherit = "res.partner"
    _description = "Partner inheritance"

    cr = fields.Char('CR', size=32)
    cpr = fields.Char('CPR', size=32)
    vat_no = fields.Char('Vat No', size=32)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        result = []
        if name:
            domain = ['|', '|', '|', '|', ('name', operator, name),
                      ('phone', operator, name), ('mobile', operator, name),
                      ('cpr', operator, name), ('cr', operator, name)]
        super(res_partner, self).name_search(name, args=domain, operator='ilike', limit=100)
        partner = self.search(domain + args, limit=limit)
        for p in partner:
            if p.name:
                name = p.name
            result.append((p.id, name))
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
