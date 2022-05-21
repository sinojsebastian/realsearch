from odoo import models, fields, api
from datetime import date,datetime

class TenantEWAExcessReport(models.TransientModel):
    _name = 'wiz.tenant.ewa.excess.report'
    _description = "Tenant-wise EWA Excess Report"

    
    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    building_id = fields.Many2one('zbbm.building', 'Building', required=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant')
    
    

    def print_tenant_ewa_excess_report(self):
        return self.env.ref('zb_bf_custom.report_tenant_ewa_excess_report_xlsx').report_action(self)