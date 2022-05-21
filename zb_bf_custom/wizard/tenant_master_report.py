from odoo import models, fields, api
from datetime import date,datetime

class TenantMasterReport(models.TransientModel):
    _name = 'wiz.tenant.master.report'
    _description = "Tenant Master Report"
    
    @api.model
    def _get_building(self):
        bd = self._context.get('active_id')
        return bd
    
    date = fields.Date("As On Date")
    building_id = fields.Many2one('zbbm.building',default=_get_building)
    def print_tenant_master_report(self):
        
        return self.env.ref('zb_bf_custom.report_tenant_master_report_xlsx').report_action(self)
    
    
#     def _get_data(self):
#         date_new=datetime.strptime(str(self.date),'%Y-%m-%d').strftime('%m/%d/%Y')
#         res = self.env['res.partner'].search([('date','=',date_new)])
#         docargs = []
#         for rec in res:
#             
#     
#             docargs.append(
#     
#                 { 'building' : rec.building_id.name })
#         return docargs

                   
       