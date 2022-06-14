# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2020 OpenERP S.A. (<http://openerp.com>).
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

from odoo import api, fields, models, _



class AccountMoveLine(models.Model):
    
    _inherit = 'account.move.line'
    

    rec_date =fields.Date('Reconciled Date',copy=False)
    reconcilation_id =fields.Many2one('bank.reconciliation','Reconciled Record',copy=False)
    date_vals = fields.Date('Date', compute="action_move_type", store=True)

    @api.depends('move_id')
    def action_move_type(self):
        for line in self:
            if line.move_id.type in ['in_invoice', 'out_invoice']:
                line.date_vals = line.move_id.invoice_date

