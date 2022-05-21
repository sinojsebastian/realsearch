from odoo import models, fields


class TenantDepositReport(models.TransientModel):
    _name = 'wiz.tenant.deposit.report'
    _description = "Tenant Deposit Details Report"

    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    building_id = fields.Many2one('zbbm.building',string='Building',domain=[('building_type', 'in',['rent','both'])])

    
    def print_report(self):
         
        return self.env.ref('zb_bf_custom.report_tenant_deposit_xlsx').report_action(self)
    
    

                   
       