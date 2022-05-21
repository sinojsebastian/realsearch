from odoo import models, fields, api
from datetime import date,datetime


class CollectionReportWizard(models.TransientModel):
    _name = 'collection.report.wizard'
    _description = "Collection Report"
    
    
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    building_id = fields.Many2one('zbbm.building',string="Building")
    
    
    def print_collection_report(self):
        
        return self.env.ref('zb_bf_custom.report_colection_report').report_action(self)
    

                   
       