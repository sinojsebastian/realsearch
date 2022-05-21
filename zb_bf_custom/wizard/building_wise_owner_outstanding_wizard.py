from odoo import models, fields, api
from datetime import date,datetime


class BuildingWiseOwnerOutstandingWizard(models.TransientModel):
    _name = 'building.owner.outstanding.wizard'
    _description = "Building Wise Owner Outstanding Summary Wizard"

    
    building_id = fields.Many2one('zbbm.building',string="Building")
    date = fields.Date(string="Date")
    service_product_id = fields.Many2one('product.product',string="Product (Income/Expense)")
    area_manager = fields.Many2one('res.users','Area Manager')

    def print_building_wise_owner_report(self):
        return self.env.ref('zb_bf_custom.report_building_owner_outstanding_xlsx').report_action(self)