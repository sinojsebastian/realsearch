# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class res_partner(models.Model):
    _inherit = "res.partner"
    _description = 'Partner'

    place_id = fields.Many2one('place.details', string='Place')


class res_company(models.Model):
    _inherit = "res.company"
    _description = 'Company'

    place_id = fields.Many2one('place.details', string='Place')


class PlaceDetails(models.Model):

    # Private attributes
    _name = "place.details"
    _description = "Place Details"

    name = fields.Char(string="Place", size=64)
