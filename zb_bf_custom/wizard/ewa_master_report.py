from odoo import models, fields, api
from datetime import date,datetime

class EWAMasterReport(models.TransientModel):
    _name = 'wiz.ewa.master.report'
    _description = "EWA Master Report"

    
    @api.model
    def _get_building(self):
        bd = self._context.get('active_id')
        return bd
    date = fields.Date("As On Date")
    building_id = fields.Many2one('zbbm.building',default=_get_building)
    
    

    def print_ewa_master_report(self):
        return self.env.ref('zb_bf_custom.report_ewa_master_report_xlsx').report_action(self)