# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class IrAttachments(models.Model):
    _inherit = "ir.attachment"
    _description = "Attachment modification"
    
    
    @api.model
    def create(self, vals):
        """
        Function to create attachment from quotation/opportunity.
        """
        res = {}
        if self._context.get('active_model')=='zbbm.building':
            vals.update({'building_id':self._context.get('active_id')})
        elif self._context.get('active_model')=='zbbm.module':
            vals.update({'module_id':self._context.get('active_id')})
        else:
            if vals.get('res_model',False)=='zbbm.building':
                vals.update({'building_id':vals.get('res_id',False)})
            elif vals.get('res_model',False)=='zbbm.module':
                vals.update({'module_id':vals.get('res_id',False)})
            else:
                pass
             
        res = super(IrAttachments, self).create(vals)
        return res

    
    def _get_index_image(self):
        if self.mimetype == 'image/jpeg':
            if self.datas:
                self.index_image = self.datas
            else:
                self.index_image = ""
        else:
            self.index_image = ""
    building_id = fields.Many2one('zbbm.building',string='Buildings')
    module_id = fields.Many2one('zbbm.module',string='Flats')
    index_image = fields.Binary(compute='_get_index_image', string='Index Content', help='This field is used only for view purpose')
    
    
    
  

    

              