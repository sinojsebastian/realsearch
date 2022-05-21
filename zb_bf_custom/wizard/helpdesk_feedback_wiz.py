from odoo import models, fields, api
import datetime 
from calendar import monthrange


class HelpdeskFeedbackReport(models.TransientModel):
    _name = 'wiz.helpdesk.feedback.report'
    _description = "Helpdesk Feedback Report"
    
    
#     managed_by = fields.Boolean("Managed By RS")
#     occupied_by = fields.Boolean("Occupied")
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')

    
    def print_helpdesk_feedback_report(self):
        datas = {
            'ids': self.ids,
            'form': self.read(),
        }
        return self.env.ref('zb_bf_custom.report_helpdesk_feedback').report_action(self,data=datas)