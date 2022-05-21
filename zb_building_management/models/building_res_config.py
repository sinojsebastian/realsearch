# -*- encoding: utf-8 -*-
##############################################################################
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from werkzeug import urls

from odoo import api, fields, models, tools


class ResConfigSettings(models.TransientModel):
    """ Inherit the base settings to add a counter of failed email + configure
    the alias domain. """
    _inherit = 'res.config.settings'
    
    reservation_time = fields.Integer(string='Default Reservation Time')
    max_reservation_time = fields.Integer(string='Maximum Reservation Time for Sale',default=0)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        reservation_time = self.env['ir.config_parameter'].sudo().get_param('zb_building_management.reservation_time')
        max_reservation_time = self.env['ir.config_parameter'].sudo().get_param('zb_building_management.max_reservation_time')
        
        res.update({
            'reservation_time': int(reservation_time),
            'max_reservation_time' : int(max_reservation_time),
        })
        # print (res,'ssss\n\n\n')
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('zb_building_management.reservation_time', int(self.reservation_time) or 0)
        set_param('zb_building_management.max_reservation_time',int(self.max_reservation_time) or 0)



