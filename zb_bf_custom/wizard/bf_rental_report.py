from odoo import models, fields, api
from datetime import date, datetime


class BFRentalReport(models.TransientModel):
    _name = 'wiz.bf.rental.report'
    _description = "BF Rental Report"

    def _set_years(self):
        return [ (x,x) for x in range(datetime.now().year-3,datetime.now().year+10)]
    
    def _set_current_year(self):
        return datetime.now().year
    
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    month=fields.Selection([('01','January'),
                            ('02','February'),
                            ('03','March'),
                            ('04','April'),
                            ('05','May'),
                            ('06','June'),
                            ('07','July'),
                            ('08','August'),
                            ('09','September'),
                            ('10','October'),
                            ('11','November'),
                            ('12','December')
                            ],string='Month',default="01") 
    year = fields.Selection(_set_years,string='Year',default=_set_current_year)
    
    def print_rental_report(self):
        return self.env.ref('zb_bf_custom.bf_rental_reports_xlsx').report_action(self)
