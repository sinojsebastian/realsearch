from odoo import models, fields, api
from datetime import date,datetime


class ResaleReportWizard(models.TransientModel):
    _name = 'resale.report.wizard'
    _description = "Resale Report"
    
    
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    
    
    def print_resale_report(self):
        report_id = self.env.ref('zb_bf_custom.report_resale_report')
        return report_id.report_action(self, data = None)
