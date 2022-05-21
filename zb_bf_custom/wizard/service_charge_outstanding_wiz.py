from odoo import models, fields, api
from datetime import date,datetime

class ServiceChargeOutstandingWiz(models.TransientModel):
    _name = 'wiz.service.charge.outstanding'
    _description = "Service Charge Outstanding Wizard"

    
    from_date = fields.Date("From Date",required=True)
    to_date = fields.Date("To Date",required=True)
    building_id = fields.Many2one('zbbm.building','Building',required=True)
    
    def print_building_move_analysis_report(self):
         
        return self.env.ref('zb_bf_custom.report_building_move_analysis_xlsx').report_action(self)
    
    

                   
       