from odoo import models, fields, api
import datetime 
from calendar import monthrange


class CallCenterReport(models.TransientModel):
    _name = 'wiz.call.center.report'
    _description = "Customer Call center Division Report"
    
    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    
    def print_call_center_report(self):
        return self.env.ref('zb_bf_custom.report_call_center_division_report').report_action(self)