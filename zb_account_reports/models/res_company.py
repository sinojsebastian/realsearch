# -*- coding: utf-8 -*-

from odoo import fields, models, api, _



class Company(models.Model):
    _inherit = 'res.company'
    _description = 'Inherited Company Model'
    
    
    header_image = fields.Binary(string="Header Image")
    footer_image = fields.Binary(string="Footer Image")
