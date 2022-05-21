from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class Attendence_report(models.TransientModel):
    _name = 'wiz.complaints.report'


    def print_report(self):
        return self.env.ref('zb_building_management.complaints_xlsx').with_context(landscape=True).report_action(self)
    


class summary_all_assets(models.TransientModel):
    _name = 'wiz.rentable.report'
     
 
    def print_report(self):
        return self.env.ref('zb_building_management.summary_all_assets_xlsx').with_context(landscape=True).report_action(self)
 
 
 
class Occupancy_Summary(models.TransientModel):
    _name = 'wiz.occupancy.summary'
    
    managed = fields.Boolean('Managed') 
 
    def print_report(self):
        return self.env.ref('zb_building_management.occupancy_summary_xlsx').with_context(landscape=True).report_action(self)
     
  

class Outstanding_Statement(models.TransientModel):
    _name = 'wiz.outstanding.statement'
     
    date = fields.Date('Date',default=lambda self: self._context.get('date', fields.Date.context_today(self)))
     
 
    def print_report(self):
        return self.env.ref('zb_building_management.outstanding_statement_xlsx').with_context(landscape=True).report_action(self)
                           


class sellablePie_report(models.TransientModel):
    _name = 'wiz.sellablepie.report'
 
    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
     
 
    def print_report(self):
        return self.env.ref('zb_building_management.pie_chart_xlsx').report_action(self)
 
  
    
class sellable_report(models.TransientModel):
    _name = 'wiz.sellable.report'
 
 
    building_id=fields.Many2one('zbbm.building',string='Building',domain=[('building_type', 'in', ('sell', 'both'))])
 
     
    def print_report(self):
        return self.env.ref('zb_building_management.sellable_xlsx').with_context(landscape=True).report_action(self)
     
     

      