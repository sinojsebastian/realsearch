from odoo import models, fields, api,exceptions
from odoo.tools.translate import _
from datetime import datetime
# from datetime import date, timedelta

from lxml import etree
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class OpenUNit(models.TransientModel):
    
    _name = "unit.unit.wizard"
    _description = "Unit Payment Configuration"
    
    
    
    @api.multi
    def return_unit(self):
            
        self.ensure_one()
        view_id = self.env.ref('zb_building_management.'
                               'view_building_form')
    
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'zbbm.unit',
            'view_mode': 'form',
            'res_id': self.env['crm.lead'].browse(self.env.context.get('active_id', False)).unit_id.id or False,
            'view_id': view_id.id,
            'views': [(False, 'form')],
            'target': 'current',
        }

    


class Rejectreason(models.TransientModel):
    
     """ Reject reason for Service (project task model)"""
    
     _name = "service.reject.reason"
     _description = "Unit Payment Configuration"
     
     
     @api.multi
     def return_unit(self):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        active = self.env['project.task'].browse(self._context.get('active_ids'))
        if self._context.get('active_model') == 'project.task':
            active.state = 'rejected'
            active.msg =self.reason
            user = self.env['res.users'].browse(self._uid)
            msg = 'Changed to Rejected State  by  by %s ' %(user.name)
            active.message_post(body=msg)
     
     reason = fields.Char('Reason')
     
     
     
# 
# class CustomPopMessage(models.TransientModel):
#     _name = "custom.pop.message"
# 
#     name = fields.Char('Message')
#  
    
class FilterAccount(models.TransientModel):
    
     """ Reject reason for Service (project task model)"""
    
     _name = "filter.account"
     
     
     @api.onchange('from_date')
     def onchange_place(self):
         res = {}
         ac =[]
         accnt = self.env['account.account'].search([('user_type_id.type','=','liquidity')])
         for all in accnt:
             ac.append(all.id)
         if ac != []:
             res['domain'] = {'account_id': [('id', 'in', ac)]}
         return res
     
     
     
     current_year = datetime.now().year
     account_id = fields.Many2one('account.account',string='Account')   
     from_date  = fields.Date('From Date',default=datetime.strptime('%s-01-01' % (current_year),'%Y-%m-%d'))
     todate = fields.Date('To Date',default=datetime.today())
     
     def get_filter(self):   
#                  query = """select m.id from account_move_line m where m.move_id in (select  a.id from account_move a,account_move_line l where a.id =l.move_id and l.account_id=%s and a.date between %s and  %s) """%(self.account_id.id,datetime.strptime(self.from_date, '%Y-%m-%d'),datetime.strptime(self.todate, '%Y-%m-%d'))

        query = """select m.id from account_move_line m where m.move_id in (select  a.id from account_move a,account_move_line l where a.id =l.move_id and l.account_id=%s) """%(self.account_id.id)
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
#         print(data,"dd--------------------------------") 
        l =[]
        m = []
        for all in data:
            l.append(all['id'])
#         print(l,"l---------------------------------------")    
        s_lis = set(l)
        l_list = list(s_lis)
        daterange = self.env['account.move.line'].search([('date','>=',self.from_date),('date','<=',self.todate),('id','in',l_list)])
        date = datetime.strptime(self.from_date,"%Y-%m-%d")
        month = datetime.date(date).strftime('%B')
        account = ((self.account_id.name).split())[0]
        year = date.year
        value = "%s %s- %s"%(account,year, month)
#         print ('///',value)
        
        
        for all in daterange:
            m.append(all.id)
        domain  = [('id', 'in',m)]
        
        #Filter creation
        filter_vals={
                        'name':value,
                        'model_id':'account.move.line',
                        'domain' : domain,
                        'user_id' :False
            }
#         filter_id = self.env['ir.filters'].create(filter_vals)
        
        view_id = self.env.ref('account.view_move_line_tree').id
        return {
#             'view_id':False,
            'name' : "Transactions",
            'view_mode': 'tree,form,pivot,graph',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'domain':domain,
            'context' : {'search_default_Test3':True},
            'target': 'current',
#             'readonly':False,
            'flags': {'tree': {'action_buttons': True,}},
            }   
     
     
     
     
     
     
    
