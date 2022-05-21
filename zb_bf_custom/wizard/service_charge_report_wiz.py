from odoo import models, fields, api
from datetime import date,datetime

class ServiceChargeCollectionWiz(models.TransientModel):
    _name = 'wiz.service.charge.collection'
    _description = "Service Charge Collection Wizard"

    
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    building_id = fields.Many2one('zbbm.building','Building')
    product_id = fields.Many2one('product.product','Product(Income/Expense)')
    
    def print_service_charge_report(self):
          
        return self.env.ref('zb_bf_custom.report_service_charge_collection').report_action(self)