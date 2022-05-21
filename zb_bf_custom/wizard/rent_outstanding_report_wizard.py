from odoo import models, fields, api
from datetime import date,datetime




class RentOutstandingReporttWizard(models.TransientModel):
    _name = 'rent.outstanding.wizard'
    _description = "Rent Outstanding Report"

    building_id = fields.Many2one('zbbm.building',string="Building")
    area_manager_id = fields.Many2one('res.users','Area Manager')
    adviser_id = fields.Many2one('res.users',string="Property Advisor")
    date = fields.Date(string="Date",required=True)
    
    def print_rent_outstanding_report(self):
        return self.env.ref('zb_bf_custom.report_rent_outstanding_xlsx').report_action(self)