from odoo import fields, models,api

class TitleDeed(models.Model):

    _name = "title.deed"
    _description = "Title Deed"
    
    name = fields.Char('Name')