from odoo import models, fields, api
from datetime import date,datetime

class LeasingDetailsReport(models.TransientModel):
    _name = 'wiz.leasing.details.report'
    _description = "Leasing Details Report"

    
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    
    def print_leasing_details_report(self):
         
        return self.env.ref('zb_bf_custom.report_leasing_details_xlsx').report_action(self)
    
    

                   
       