from odoo import models, fields, api
from datetime import date,datetime




class BuildingIncomeStatementWizard(models.TransientModel):
    _name = 'building.income.statement.wizard'
    _description = "Building Wise Income Statement"

    
    building_id = fields.Many2one('zbbm.building',string="Building")
    report_for = fields.Selection([
                    ('management', 'Management'),
                    ('owner_association', 'Owner Association'),
                    ], 'Report For')
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    service_product_id = fields.Many2one('product.product',string="Service Product")
    
    

    def print_building_income_statement(self):
        return self.env.ref('zb_bf_custom.report_building_income_statement').report_action(self)