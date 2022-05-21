from odoo import models, fields, api
import datetime 
from calendar import monthrange


class EwaInternetInvoiceReport(models.TransientModel):
    _name = 'wiz.ewa.internet.invoice.report'
    _description = "EWA / Batelco Internet Invoice Report"
    
#     @api.model
#     def _get_pv(self):
#         pv_id = self._context.get('active_id')
#         return pv_id
    
#     managed_by = fields.Boolean("Managed By RS")
#     occupied_by = fields.Boolean("Occupied")
#     pv_id = fields.Many2one('account.payment', default=_get_pv)
    
    
    
    
    def print_ewa_internet_inv_report(self):
        datas = {
            'ids': self.ids,
            'form': self.read(),
            
        }
        return self.env.ref('zb_bf_custom.report_ewa_internet_batelco_invoice').report_action(self,data=datas)