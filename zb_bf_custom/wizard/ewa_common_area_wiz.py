from odoo import models, fields, api
import datetime 
from calendar import monthrange

MONTH_LIST= [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'),('12', 'Dec')]

class EWACommonAreaReport(models.TransientModel):
    _name = 'wiz.ewa.common.area.report'
    _description = "EWA Common Area Report"
    
    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        
        this_year = datetime.datetime.now().year
        this_month = datetime.datetime.now().month
        print(datetime.datetime.now().year,datetime.datetime.now().month)
        res.update(
            {
                "month": str(this_month),
                "year": str(datetime.datetime.now().year),
            }
        )
        return res
    
    
    @api.onchange('month','year')
    def onchange_month(self):
        if self.month and self.year:
            first_last_month = monthrange(int(self.year), int(self.month))
            self.from_date ='%s-%s-01'%(self.year,self.month)
            self.to_date = '%s-%s-%s'%(self.year,self.month,first_last_month[1])

    
    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    month = fields.Selection(MONTH_LIST, string='Month', required=True)
    this_year = datetime.datetime.now().year
    range_of_years = range(2000, this_year + 1)
    descending_range = sorted(range_of_years, reverse=True)
    year =  fields.Selection([(str(num), str(num)) for num in descending_range],string='Year')
    
    

    def print_ewa_ca_report(self):
        return self.env.ref('zb_bf_custom.report_ewa_ca_report_xlsx').report_action(self)