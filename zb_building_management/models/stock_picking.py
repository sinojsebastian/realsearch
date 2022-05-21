from odoo import models, fields, api, _
from odoo.exceptions import UserError

import odoo.addons.decimal_precision as dp



class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    @api.onchange('partner_id','building_id')
    def hide_units_modules(self):
        for all in self:
            if all.building_id:
                if all.building_id.building_type =='rent':
                    all.hide_field =True
                    all.hide_field2 =False
                else:
                    all.hide_field2 =True
                    all.hide_field =False
            else:
                all.hide_field2 =True
                all.hide_field =False
            if all.picking_type_id.code =='outgoing':
                all.hide_field0 = True
            else:
                all.hide_field0 = False
                all.hide_field = False
                all.hide_field2 = False
                
    hide_field0 = fields.Boolean('Hide',default =False,compute = 'hide_units_modules' )
    hide_field = fields.Boolean('Hide',default =False,compute = 'hide_units_modules' )
    hide_field2 = fields.Boolean('Hide',default =False,compute = 'hide_units_modules' )
    
    module_id = fields.Many2one('zbbm.module', 'Flat/Office')
    building_id = fields.Many2one('zbbm.building', 'Building')
    unit_id = fields.Many2one('zbbm.unit', 'Unit')
    
