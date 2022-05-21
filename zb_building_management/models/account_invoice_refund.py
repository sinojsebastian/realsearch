# -*- coding: utf-8 -*-
##############################################
#
# Inforise IT & ZestyBeanz Technologies Pvt. Ltd
# By Sinoj Sebastian (sinoj@zbeanztech.com, sinoj@inforiseit.com)
# First Version 2015-05-10
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

import time
from odoo import models, fields, api,exceptions,_
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.tools.translate import _

class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice modified for linking refund to bulding"""
    _inherit = "account.invoice.refund"
    
    def invoice_refund(self):
        ## Linking refund to building
        context = self._context or {}
        res = super(AccountInvoiceRefund, self).invoice_refund()
        inv_obj = self.env.get('account.invoice')
        if res.get('domain') and context.get('active_ids'):
            inv = inv_obj.browse(context['active_ids'][0])
            if inv.module_id:
                for domain in res['domain']:
                    if len(domain) > 2 and domain[0] == 'id':
                        refund_ids = domain[2] or []
                        for refund_id in refund_ids:
                            wr = inv_obj.browse(refund_id)
                            wr.write({'module_id': inv.module_id.id,
                                      'building_id': inv.building_id and inv.building_id.id})
        return res
         
         