# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import date


import logging
_logger = logging.getLogger(__name__)


def first_day_of_month(d):
    return date(d.year, d.month, 1)



class OwnerRentalStatementWizard(models.TransientModel):
    
    _name = 'owner.rental.statement.wizard'
    _description = 'Owner Rental Statement Report Wizard'
    
    
    def print_owner_rental_statement(self):
        
        datas = {
            'ids': self.ids,
            'form': self.read(),
            
        }
        return self.env.ref('zb_bf_custom.report_owner_rental_statement_qweb').report_action(self,data=datas)
        
   
    @api.model
    def default_partner_id(self):
        owner = False
        context = self._context
        if context.get('active_model', '') and context['active_model'] == 'zbbm.module.lease.rent.agreement':
            if context.get('active_id', False):
                lease_id = self.env.get('zbbm.module.lease.rent.agreement').browse(context['active_id'])
                if lease_id:
                    if lease_id.owner_id:
                        owner = lease_id.owner_id.id
                    else:
                        owner = False
                else:
                    owner = False
        return owner
    
    def default_start_date(self):
        start_date = ''
        context = self._context
        if context.get('active_model', '') and context['active_model'] == 'zbbm.module.lease.rent.agreement':
            if context.get('active_id', False):
                lease_id = self.env.get('zbbm.module.lease.rent.agreement').browse(context['active_id'])
                if lease_id:
                    if lease_id.agreement_start_date:
                        start_date = lease_id.agreement_start_date
                    else:
                        start_date = ''
                else:
                    start_date = ''
        return start_date
    
    def default_end_date(self):
        end_date = ''
        context = self._context
        if context.get('active_model', '') and context['active_model'] == 'zbbm.module.lease.rent.agreement':
            if context.get('active_id', False):
                lease_id = self.env.get('zbbm.module.lease.rent.agreement').browse(context['active_id'])
                if lease_id:
                    if lease_id.agreement_end_date:
                        end_date = lease_id.agreement_end_date
                    else:
                        end_date = ''
                else:
                    end_date = ''
        return end_date
                          
     
    from_date = fields.Date("From Date",default=default_start_date)
    to_date = fields.Date("To Date",default=default_end_date)
    partner_id = fields.Many2one('res.partner','Owner',default=default_partner_id)
    date_start = fields.Date(string='Date From', required=True)
    date_end = fields.Date(string='Date To', required=True)
    service_date_start = fields.Date(string='Date From')
    service_date_end = fields.Date(string='Date To')
    service_amount = fields.Float(string='Service Charge Amount',digits=(16,3))
        
       



