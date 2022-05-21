from odoo import models, fields, api
from datetime import date,datetime

class Project_Wise_Income_Stmnt_Wiz(models.TransientModel):
    _name = 'proect.wise.income.stmnt.wiz'
    _description = "Project Wise Income Statement Wizard"

    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    
    def print_income_stmnt_report(self):
         
        return self.env.ref('zb_bf_custom.report_project_wise_income_statement').report_action(self)