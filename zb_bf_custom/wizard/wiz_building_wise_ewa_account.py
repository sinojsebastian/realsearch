from odoo import models, fields, api
from datetime import date,datetime

class Building_Wise_EWA_Account_Wiz(models.TransientModel):
    _name = 'building.wise.ewa.account.wiz'
    _description = "Building Wise EWA Account Wizard"

    
    building_id = fields.Many2one('zbbm.building','Building')
    
    def print_building_ewa_account_report(self):
         
        return self.env.ref('zb_bf_custom.report_building_ewa_account_report_xlsx').report_action(self)