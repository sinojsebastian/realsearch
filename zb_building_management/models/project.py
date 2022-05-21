from odoo import models, fields, api,exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools.translate import _
from datetime import datetime,date,timedelta
import pprint
from dateutil import relativedelta


class Projectname(models.Model):
    _name = "project.name"
    _description = "Project"
    
    name= fields.Char('Name', 
                    required=False)


#PV class ProjectProject(models.Model):
#     _inherit = "project.project"
#     
#   
#     building_id = fields.Many2one('zbbm.building', 'Building', 
#                     required=False)
# #     module_id =  fields.Many2one('zbbm.module', string='Modules / Flats',domain= tuple(lis))
# 
# 
# class ProjectTask(models.Model):
#     _inherit = "project.task"
#     
#     domain =[]
#     lis= pp=l=[]
#     
#     
#     def make_reject(self):
#         view_id = self.env.ref('zb_building_management.'
#                                'view_open_rejectwizard')
#     
#             
#         return {
#                 'name':'Reason For Rejection',
#                 'type': 'ir.actions.act_window',
#                 'res_model': 'service.reject.reason',
#                 'view_mode': 'form',
#                 'view_type': 'form',
#                 'view_id': view_id.id or False,
#                 'views': [(False, 'form')],
#                 'target': 'new',
#             }  
#         
#          
#         
#     def make_available(self):
#         for items in self:
#             if not items.building_id:
#                 raise Warning(_('Please Select Building'))
#             elif not items.module_id:
#                 raise Warning(_('Please Select Module'))
#             elif not items.partner_id:
#                 raise Warning(_('Please select Sub Contract'))
#              
# #             if items.kanban_state == 'done':
# #                 items.state = 'start'
#             else:
#                 items.state = 'new'
#     #                 raise Warning(_('Only  Process(green) Status can be Validate'))
#                 user = self.env['res.users'].browse(self._uid)
#                 msg = 'Changed to Approved State  by  by %s ' %(user.name)
#                 self.message_post(body=msg)
#             
# 
#     
#     def make_approve(self):
#         for items in self:
#             if not items.building_id:
#                 raise Warning(_('Please Select Building'))
#             elif not items.module_id:
#                 raise Warning(_('Please Select Module'))
#             elif not items.partner_id:
#                 raise Warning(_('Please select Sub Contract'))
#              
# #             if items.kanban_state == 'done':
# #                 items.state = 'start'
#             else:
#                 items.state = 'Waiting'
#                 user = self.env['res.users'].browse(self._uid)
#                 msg = 'Requested and Changed to Waiting for Approval State by  by %s ' %(user.name)
#                 self.message_post(body=msg)
#                 
#                 
# 
#     def make_done(self):
#         for items in self:
#             if items.state =='new':
#                 if items.building_id:
#                     items.date_done = datetime.today()
#                     items.state = 'done'
#                     user = self.env['res.users'].browse(self._uid)
#                     msg = 'Changed to Done State by  by %s ' %(user.name)
#                     self.message_post(body=msg)
#                 else:
#                     raise Warning(_('Only Complaints with Building can be Validated'))
#             else:
#                 raise Warning(_('Only Complaints In In Processs State can be Validate'))
#     
#     
#     def _compute_invoice(self):
#         for order in self:
#             invoices = self.env['account.move'].search([('name','=',order.id),('type','=','in_invoice')])
#             order.invoice_ids = invoices
#             order.invoice_count = len(invoices)       
#     
# 
#     def action_view_invoice(self):
#         invoices = self.mapped('invoice_ids')
#         action = self.env.ref('account.action_invoice_tree1').read()[0]
#         if len(invoices) > 1:
#             action['domain'] = [('id', 'in', invoices.ids)]
#         elif len(invoices) == 1:
#             action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
#             action['res_id'] = invoices.ids[0]
#         else:
#             action = {'type': 'ir.actions.act_window_close'}
#         return action
#     
#     
#     def start_again(self):
#         for items in self:
#             items.state = 'new'
#             user = self.env['res.users'].browse(self._uid)
#             msg = 'Changed to IN PROCESS State by  by %s ' %(user.name)
#             self.message_post(body=msg)
#             
#            
# 
#     def get_readonly(self):
#         if self.env['res.users'].browse(self._uid).has_group('project.group_project_user'):
#             for all in self:
#                 if all.state == 'Waiting':
#                     all.make_reado = True
#                 else:
#                     all.make_reado = False
#     
#     
#     
#     make_reado = fields.Boolean('Is Read only',default=False,compute='get_readonly')   
#     pjt_name_id = fields.Many2one('project.name',"Job Type" ,required =True )
#     msg = fields.Text('Reason For Rejection')     
#     state = fields.Selection([
#         ('start', 'New'),
#         ('Waiting','Waiting for approval'),
#         ('new', 'In Process'),
#         ('done', 'Done'),
#         ('rejected','Rejected')
#         
#         ], 'Status', readonly=True,default='start')  
#     
#     date_done = fields.Date('Completion Date',readonly =True)
#     invoice_count = fields.Integer(compute="_compute_invoice", string='# of Bills', default=0)
#     invoice_ids = fields.Many2many('account.move', compute="_compute_invoice", string='Bills')     
#     module_id =  fields.Many2one('zbbm.module', string='Flat/Office No.')
#     building_id = fields.Many2one('zbbm.building', 'Building',domain =[('building_type','=','rent')])
#     partner_id = fields.Many2one('res.partner',
#         string='Vendor',
#         domain =[('supplier','=',True)])
#     job_type = fields.Char('Job Type')
#     amount = fields.Float('Amount')
#     quat_no = fields.Char('Quotation No')
#     attachments_ids = fields.Many2many('ir.attachment', 'document_ir_attachments_rel',
#         'doc_mailing_id', 'attachments_id', string='Attachments')
#     
#     category =fields.Selection([('gen','General'),('qr','Quotation required')],string='Category',default='gen') 
#     
# 
# 
#     @api.onchange('pjt_name_id')
#     def task_name(self):
#         if self.pjt_name_id:
#             self.name= self.pjt_name_id.name


    
class PartnerTitle(models.Model):
    _inherit= 'res.partner.title'
    _rec_name = 'shortcut'
    

    @api.depends('name')
    def name_get(self):
        result = []
        for event in self:
            result.append((event.id, '%s' % (event.shortcut)))
        return result
    
    shortcut = fields.Char(string='Abbreviation', translate=True)  
   
   


