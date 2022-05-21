from odoo import models, fields, api
from datetime import date,datetime


class ContractCommissionDeductionWizard(models.TransientModel):
    _name = 'contract.commission.deduction.wizard'
    _description = "Contract Commission Deduction Wizard"


    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    

    def print_commission_deduction_Report(self):
        return self.env.ref('zb_bf_custom.report_contract_commission_deduction').report_action(self)