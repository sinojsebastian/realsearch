from odoo import models, fields, api
from datetime import date,datetime




class BuildingInternetWizard(models.TransientModel):
    _name = 'building.internet.wizard'
    _description = "Building Wise Internet Wizard"

    
    @api.model
    def default_building_id(self):
        building = False
        context = self._context
        if context.get('active_model', '') and context['active_model'] == 'zbbm.building':
            if context.get('active_id', False):
                building = self.env.get('zbbm.building').browse(context['active_id'])
                if building:
                    building = building.id
                else:
                    building = False
        return building
    
    
    building_id = fields.Many2one('zbbm.building',string="Building",default=default_building_id)
    

    def print_building_internet_Report(self):
        return self.env.ref('zb_bf_custom.report_building_internet').report_action(self)