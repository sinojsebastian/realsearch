from odoo import models, fields, api,exceptions,tools,_
from odoo.tools.translate import _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
# import re
from dateutil import relativedelta
import odoo.addons.decimal_precision as dp
from datetime import datetime, date, timedelta

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

import logging

_logger = logging.getLogger(__name__)



class Installment(models.Model):

    _inherit = 'installment.details'
    
    
    
    def invoice_create(self):
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        for items in self:
            if not items.invoice_id:
                if items.unit_id.state in ['new','reserved']:
                    raise UserError(_('Unit should be booked to Client to generate invoice !'))
                     
                if items.unit_id.invoice_total >= items.unit_id.price:
                    raise Warning(_('Already Paid/Invoiced Full Amount'))
                if items.amount > items.unit_id.price:
                    raise Warning(_('You need to pay only %s'%(items.unit_id.price)))    
    #             if items.unit_id.building_id.account_id:
    #                 acct_line_id = items.unit_id.building_id.account_id.id
    #             else:
    #                 acct_line_id = items.user_id.property_account_payable_id.id   
                if not items.unit_id.building_id.account_id:
                    journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
                    if journal :
                        acct_id = journal[0].default_credit_account_id.id
                else:
                    acct_id = items.unit_id.building_id.account_id.id
                 
    #             journal = self.env.get('account.journal').search([('type','=', 'sale')], limit=1)
    #             if journal:
    #                 acct_id = journal[0].default_credit_account_id.id
                if items.unit_id.account_analytic_id:
                    analytic = items.unit_id.account_analytic_id.id
                else:
                    analytic = False 
                if self.fee_for:      
                    fee = dict(self.fields_get(allfields=['fee_for'])['fee_for']['selection'])[self.fee_for] 
                if not self.fee_for:
                    fee = False
                check = ['th',"st","nd","rd",]+["th"]*96
                try:
                    if self.name.split('/')[1] == '0':
                        order = ''
                    else:
                        order = check[int(self.name.split('/')[1])%100]
                         
                except:
                    order ='th' 
                if self.name.split('/')[1] == '0':
                    name = ''
                else:
                    name =  self.name.split('/')[1]  
                 
#                 config_obj = self.env.get('res.config.settings').search([('type','=', 'sale')], limit=1)
                params = self.env['ir.config_parameter'].sudo()        
                tax_ids = params.get_param('zb_building_management.default_sellable_tax_ids') or False,
                
                installment_journal_id = params.get_param('zb_bf_custom.installment_journal_id') or False
                installment_product_id = params.get_param('zb_bf_custom.installment_product_id') or False
                
                if not installment_journal_id:
                    raise Warning(_('Please Configure Installment Journal'))
                if not installment_product_id:
                    raise Warning(_('Please Configure Installment Product'))
                
                if tax_ids[0]:
                    temp = re.findall(r'\d+', tax_ids[0]) 
                    tax_list = list(map(int, temp))
                 
                vals = {
                        'name':str(items.name),
                        'partner_id': items.unit_id.buyer_id and items.unit_id.buyer_id.id,
                        'type': 'out_invoice',
#                         'account_id': items.unit_id.buyer_id.property_account_receivable_id.id,
                        'invoice_date_due': items.due_date,
                        'invoice_date': items.invoice_date,
                        'unit_id': items.unit_id and items.unit_id.id,
                        'building_id':items.unit_id.building_id and items.unit_id.building_id.id,
                        'lead_id':items.unit_id.lead_id and items.unit_id.lead_id.id,
                        'journal_id':int(installment_journal_id),
                        'invoice_line_ids': [(0, 0, {
                                                    'product_id':int(installment_product_id),
                                                    'name': '{} {} {} for Unit {} in {}, {}th floor , {}  , Area - {} Sqm, Sale price BD {}/- '.format(name,order,fee,self.unit_id.name,self.unit_id.building_id.name,self.unit_id.floor,self.unit_id.bedroom.name,self.unit_id.total_area,round(self.unit_id.price)),
                                                    'price_unit': items.amount,
                                                    'tax_ids' : [(6, 0, tax_list)] if tax_ids[0] else '',
                                                    'quantity': 1,
    #                                                 'from_date': items.contract_date,
                                                    'account_analytic_id':analytic,
                                                    'account_id': acct_id,
                                                     })],
                            }
                invoice_id = self.env['account.move'].create(vals)
                items.unit_id.update({'invoice_ids1': [(4,invoice_id.id)]})
                if invoice_id.invoice_date:
                    items.unit_id.las_date = invoice_id.invoice_date
                if invoice_id.state =='open':
                    status= 'Posted'
                else:
                    status =  invoice_id.state  
                items.write({'state':status,
                             'invoice_id':invoice_id.id
                             })
             
            else:
                pass
    
    