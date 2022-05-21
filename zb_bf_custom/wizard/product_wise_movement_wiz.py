from odoo import models, fields, api
from datetime import date,datetime

class ProductWiseMovementWiz(models.TransientModel):
    _name = 'wiz.product.wise.movement'
    _description = "Product Wise Movement Wizard"

    
    from_date = fields.Date("From Date",required=True)
    to_date = fields.Date("To Date",required=True)
    product_id = fields.Many2one('product.product','Product',required=True)
    
    def print_product_move_analysis_report(self):
         
        return self.env.ref('zb_bf_custom.report_pdt_wise_movement_report').report_action(self)