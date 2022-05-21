from odoo import fields, models,api

class OtherFeatures(models.Model):

    _name = "other.features"
    _description = "Other Features"
    
    
    name = fields.Char('Name')
    name_arabic = fields.Char('Name Arabic')
    lease_agreement_id = fields.Many2one('zbbm.module.lease.rent.agreement',string="Lease Agreement")
    module_id = fields.Many2one('zbbm.module',string="Flat")
    is_car_park = fields.Boolean('Is Car Park',default=False)
