from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError,Warning
from odoo.tools.misc import formatLang, format_date, get_lang
import time


class EWAInternetQweb(models.AbstractModel):

    _name = 'report.zb_bf_custom.report_ewa_internet_batelco_inv'
    _description='Model For EWA Batelco Internet Invoice'

    
   
         

    @api.model
    def _get_report_values(self, docids,data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        result =[]
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        company = self.env.user.company_id and self.env.user.company_id.name or 'Real Search' 
        
        params = self.env['ir.config_parameter'].sudo()  
        ewa_product_id = params.get_param('zb_bf_custom.ewa_product_id')
        if not ewa_product_id:
            raise Warning(_("""Please configure EWA Service Product in the Accounting Settings"""))
        
        internet_product_id = params.get_param('zb_bf_custom.internet_product_id')
        if not internet_product_id:
            raise Warning(_("""Please configure Internet Service Product in the Accounting Settings"""))
        
        #EWA Section 
        ewa_obj = self.env['product.product'].browse(int(ewa_product_id[0]))
       
        
        #Internet Section      
        internet_obj = self.env['product.product'].browse(int(internet_product_id[0]))
        
        occuppied_managed = ''
        occuppied_not_managed=''
        not_occuppied_managed=''
        not_occupied_not_mngd=''
        bill_to = ''
        paid_by = ''
        acc_no= ''
        pdt_name =''
        for data in data['form']:
            payment_list =[]
            
            if docs.method_type=='adjustment':
                reconcile_lines = docs.payment_line_ids.filtered(lambda r: r.full_reconcile == True)
                for pv_line in reconcile_lines:
                    service_ids = []
                    if docs.partner_id.id == ewa_obj.service_product_partner_id.id:
                        pdt_name = ewa_obj.name
                        service_ids = self.env['zbbm.services'].search([('product_id','=',ewa_obj.id),('module_id','=',pv_line.inv_id.module_id.id)])
                    if docs.partner_id.id == internet_obj.service_product_partner_id.id:
                        pdt_name = internet_obj.name
                        service_ids = self.env['zbbm.services'].search([('product_id','=',internet_obj.id),('module_id','=',pv_line.inv_id.module_id.id)])
                    
                    if len(service_ids) > 0:
                        service_ids = service_ids[0] if len(service_ids)>1 else service_ids
                        if service_ids[0].trf_status:
                            bill_to = pv_line.inv_id.module_id.owner_id.name or ''
                            if service_ids.managed_by_rs:
                                paid_by = company 
                            else:
                                paid_by = pv_line.inv_id.module_id.owner_id.name or ''
                        else:
                            bill_to = company
                            paid_by = company
                    
                        if service_ids.account_no:
                            acc_no = service_ids.account_no 
    #                 else:
    #                     raise Warning(_("""Please choose EWA/Internet Payments for printing"""))
                    
                    
        #             Bill of flat filtering Process
    #                 filtered_flat = False
    #                 if data['occupied_by']==True and data['managed_by']==True:
    #                     if pv_line.inv_id.module_id.state =='occupied' and pv_line.inv_id.module_id.managed:
    #                         filtered_flat = True
    #                 elif data['occupied_by']==True and data['managed_by']==False:
    #                     if pv_line.inv_id.module_id.state =='occupied' and not pv_line.inv_id.module_id.managed:
    #                         filtered_flat = True
    #                 elif data['occupied_by']==False and data['managed_by']==True:
    #                     if pv_line.inv_id.module_id.state !='occupied' and pv_line.inv_id.module_id.managed:
    #                         filtered_flat = True
    #                 else:
    #                     if pv_line.inv_id.module_id.state !='occupied' and not pv_line.inv_id.module_id.managed:
    #                         filtered_flat = True
                            
                            
                    if pv_line.inv_id.module_id.managed:
                        mgt='Mgt'
                    else:
                        mgt='Not Mgt'
                        
                    
                    tenant_share = 0.000
                    owner_share = 0.000
                    if pv_line.inv_id.raw_service_id:
                        tenant_share = pv_line.inv_id.raw_service_id.tenant_share
                    if pv_line.inv_id.raw_service_id:
                        owner_share = pv_line.inv_id.raw_service_id.owner_share
                            
    #                 if filtered_flat and pv_line.allocation > 0:   
                    payment_list.append(({
                               'building':pv_line.inv_id.building_id,
                               'flat':pv_line.inv_id.module_id,
                               'party_name':pv_line.inv_id.partner_id.name,
                               'mgt_status':mgt,
                               'occ_status':pv_line.inv_id.module_id.state,
                               'inv_no':pv_line.inv_id.name,
                               'inv_date':pv_line.inv_id.invoice_date.strftime(get_lang(self.env).date_format),
                               'description':pv_line.inv_id.name,
                               'amount':pv_line.allocation,
                               'bill_to':bill_to,
                               'paid_by':paid_by,
                               'acc_no':acc_no,
                               'tenant_share':tenant_share,
                               'owner_share':owner_share,
                               }))
                    
            else:
                for inv_line in docs.reconciled_invoice_ids:
                    service_ids = []
                    if docs.partner_id.id == ewa_obj.service_product_partner_id.id:
                        pdt_name = ewa_obj.name
                        service_ids = self.env['zbbm.services'].search([('product_id','=',ewa_obj.id),('module_id','=',inv_line.module_id.id)])
                    if docs.partner_id.id == internet_obj.service_product_partner_id.id:
                        pdt_name = internet_obj.name
                        service_ids = self.env['zbbm.services'].search([('product_id','=',internet_obj.id),('module_id','=',inv_line.module_id.id)])
                    
                    if len(service_ids) > 0:
                        service_ids = service_ids[0] if len(service_ids)>1 else service_ids
                        if service_ids[0].trf_status:
                            bill_to = inv_line.module_id.owner_id.name or ''
                            if service_ids.managed_by_rs:
                                paid_by = company 
                            else:
                                paid_by = inv_line.module_id.owner_id.name or ''
                        else:
                            bill_to = company
                            paid_by = company
                    
                        if service_ids.account_no:
                            acc_no = service_ids.account_no 
                            
                        if inv_line.module_id.managed:
                            mgt='Mgt'
                        else:
                            mgt='Not Mgt'
                        
                    
                        tenant_share = 0.000
                        owner_share = 0.000
                        if inv_line.raw_service_id:
                            tenant_share = inv_line.raw_service_id.tenant_share
                        if inv_line.raw_service_id:
                            owner_share = inv_line.raw_service_id.owner_share
                            
    #                 if filtered_flat and pv_line.allocation > 0:   
                        payment_list.append(({
                                   'building':inv_line.building_id,
                                   'flat':inv_line.module_id,
                                   'party_name':inv_line.partner_id.name,
                                   'mgt_status':mgt,
                                   'occ_status':inv_line.module_id.state,
                                   'inv_no':inv_line.name,
                                   'inv_date':inv_line.invoice_date.strftime(get_lang(self.env).date_format),
                                   'description':inv_line.name,
                                   'amount':inv_line.amount_total,
                                   'bill_to':bill_to,
                                   'paid_by':paid_by,
                                   'acc_no':acc_no,
                                   'tenant_share':tenant_share,
                                   'owner_share':owner_share,
                                   }))


        docargs = {
                   'doc_ids':self._ids,
                   'doc_model': model,
                   'docs': docs,
                   'pdt':pdt_name,
                   'payment_list':payment_list
#                    'data': data['form'],
                   }
        return docargs
