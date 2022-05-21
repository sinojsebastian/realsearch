from odoo import fields, models,api

class ViewUnit(models.Model):

    _name = "view.unit"
    _description = "View Unit"
    
    name = fields.Char('Name')