# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.tools.translate import _
from datetime import datetime, date, timedelta
from odoo.exceptions import AccessError,UserError,Warning

import logging
_logger = logging.getLogger(__name__)


class TerminateAgreementWizard(models.TransientModel):
    _name = 'terminate.agreement.wizard'
    _description = "Terminate Agreement"


    # def get_date(self):
    #     active_model = self.env.context.get('active_model', False)
    #     active_id = self.env.context.get('active_id', False)
    #     agreement = self.env['zbbm.module.lease.rent.agreement'].browse(active_id)
    #     if agreement.agreement_end_date:
    #         return agreement.agreement_end_date
            
    end_date = fields.Date("End Date",default=lambda self: fields.Date.today())
    
            
    def terminate_agreement_invoice(self):
        active_model = self.env.context.get('active_model', False)
        active_id = self.env.context.get('active_id', False)
        agreement = self.env['zbbm.module.lease.rent.agreement'].browse(active_id)
        params = self.env['ir.config_parameter'].sudo()    
        
        if agreement.state not in ['expired']:
            if agreement.subproperty:
                subproperty = agreement.subproperty
                subproperty.make_available()
                subproperty.sudo().tenant_id = agreement.tenant_id.id
                agreement.termination_date = datetime.today()
                agreement.state='terminate'
            
            building_income_account_id = params.get_param('zb_bf_custom.building_income_acccount_id') or False
            if not building_income_account_id:
                raise Warning(_('Please Configure Building Income Account'))
            
            
    #         building_expense_account_id = params.get_param('zb_bf_custom.building_expense_acccount_id') or False
    #         if not building_expense_account_id:
    #             raise Warning(_('Please Configure Building Expense Account'))
    #         
            
            if not building_income_account_id:
                journal = self.env.get('account.journal').search([('type','=', 'purchase')], limit=1)
                if journal :
                    acct_id = journal[0].default_debit_account_id.id
            else:
                acct_id = int(building_income_account_id)
            
            if agreement.subproperty.building_id.analytic_account_id:
                analytic = agreement.subproperty.building_id.analytic_account_id.id
            else:
                analytic = '' 
                    
            if agreement.subproperty.building_id.building_address.street:
                street = agreement.subproperty.building_id.building_address.street
            else:
                street = '' 
                
            if agreement.subproperty.building_id.building_address.street2:
                street2 = agreement.subproperty.building_id.building_address.street2
            else:
                street2 = ''
            
            if agreement.subproperty.building_id.building_address.city:
                city = agreement.subproperty.building_id.building_address.city
            else:
                city = ''
                
            if agreement.subproperty.building_id.building_address.country_id:
                country = agreement.subproperty.building_id.building_address.country_id.name
            else:
                country = ''
            
            end_date = datetime.strptime(str(agreement.agreement_end_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',       
            start_date = datetime.strptime(str(agreement.agreement_start_date), '%Y-%m-%d').strftime('%d-%m-%Y') or '',  
            total_days = (datetime.strptime(str(agreement.agreement_end_date), '%Y-%m-%d')-datetime.strptime(str(agreement.agreement_start_date), '%Y-%m-%d')).days + 1
            total_commission = agreement.agent_commission_amount 
            refund_commission = 0
            
    #DB         if agreement.vendor_id.state == 'draft':
    #             raise UserError('Please Validate The Vendor Bill')
    #         else:
            if self.end_date != agreement.agreement_end_date:
                no_of_days = (datetime.strptime(str(self.end_date), '%Y-%m-%d')-datetime.strptime(str(agreement.agreement_start_date), '%Y-%m-%d')).days + 1
                refund_commission = total_commission - ((agreement.monthly_rent *(agreement.commission_percent/100))/365 * no_of_days)
                print('=================refund_commission===================',refund_commission)
                _logger.info("refund_commissionnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn %s",refund_commission)
    #             vals = {
    #                     'partner_id': agreement.agent.id,
    #                     'invoice_payment_term_id':agreement.agent.property_supplier_payment_term_id.id if agreement.agent.property_supplier_payment_term_id else '',
    #                     'ref':agreement.vendor_id.name,
    #                     'type': 'in_refund',
    #                     'lease_id':agreement.id,
    #                     'invoice_date': agreement.agreement_end_date,
    #                     'module_id': agreement.subproperty.id,
    #                     'building_id':agreement.subproperty.building_id and agreement.subproperty.building_id.id,
    #                     'invoice_line_ids': [(0, 0, {
    #                                                 'name': '{},{},{},{},{},{}, Rent Period:{}  to {}, Tenant:{}'.format(agreement.building_id.name,agreement.subproperty.name,street,street2,city,country,start_date[0],end_date[0],agreement.tenant_id.name),
    #                                                 'price_unit': refund_commission, 
    #                                                 'quantity': 1,
    #                                                 'analytic_account_id':analytic,
    #                                                 'account_id': acct_id,
    #                                                  })],
    #                         }
    #             if agreement.agent:
    #                 invoice_id = self.env['account.move'].create(vals)
    #                 invoice_id.action_post()
    #                 agreement.vendor_refund_id = invoice_id.id
    
                moves = agreement.vendor_id
     
                default_values_list = []
                for move in moves:
                    default_values_list.append(self._prepare_default_reversal(move,refund_commission))
                    refund_method = (len(moves) > 1 or moves.type == 'entry') and 'cancel' or 'refund'
                    new_moves = moves._reverse_moves(default_values_list)
                    new_moves.action_post()
                    agreement.vendor_refund_id = new_moves.id
        else:
            agreement.termination_date = self.end_date
            agreement.state='terminate'

            
    def _prepare_default_reversal(self, move,refund_commission):
        return {
            'ref': _('Reversal of: %s') % (move.name),
            'date': date.today() or move.date,
            'invoice_date': move.is_invoice(include_receipts=True) and (date.today() or move.date) or False,
            'journal_id': move.journal_id.id,
            'invoice_payment_term_id': None,
            'auto_post': True if date.today() >= fields.Date.context_today(self) else False,
            'invoice_user_id': move.invoice_user_id.id,
            'amount_total':refund_commission,
        }

        