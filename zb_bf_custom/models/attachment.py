# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models


class IrAttachments(models.Model):
    _inherit = "ir.attachment"
    _description = "Attachment modification"
    
    
    @api.model
    def create(self, vals):
        res = {}
        if self._context.get('active_model')=='zbbm.module.lease.rent.agreement':
            vals.update({'agreement_id':self._context.get('active_id')})
        else:
            if vals.get('res_model',False)=='zbbm.module.lease.rent.agreement':
                vals.update({'agreement_id':vals.get('res_id',False)})
            else:
                pass
        res = super(IrAttachments, self).create(vals)
        return res
    

    agreement_id = fields.Many2one('zbbm.module.lease.rent.agreement',string='Agreements')
