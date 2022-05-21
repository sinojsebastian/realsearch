# # -*- coding: utf-8 -*-
# from odoo import api, fields, models, _
# 
# class AccountTaxReport(models.TransientModel):
#     _inherit = "account.common.report"
#     _name = 'zb_account.tax.report'
#     _description = 'Tax Report'
#     
#     
#     name = fields.Char('Name')
#     from_date = fields.Date(string='Start Date')
#     to_date = fields.Date(string='End Date')
#     
#     @api.multi
#     def print_tax_report(self):
#         datas = {
#                     'ids': self._ids,
#                     'model': self._name,
#                     'form': self.read()
#                 }
#         return self.env.ref('zb_vat_report.action_report_vats').report_action(self,data=datas)
