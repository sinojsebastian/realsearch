# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields,api

class ResUsers(models.Model):

    _inherit = 'res.users'
    
#     

#     @api.multi
#     def write(self, vals):
#         print("group,""group---Before----------------",self.groups_id,vals)
#               
#         existing_group = [x.id for x in self.groups_id]
#         rem = []
#          
#         group2 = self.env.ref('zb_building_management.group_property_user')
#         group_name = 'in_group_'+str(group2.id)
#         invoice_group = self.env.ref('account.group_account_invoice')
#         print(group_name,"group_name-------------------------------")
#         if vals.get(group_name) or group2.id in existing_group:
#             print("enter--------------------")
#             if invoice_group.id in existing_group: 
#                 rem.append((3,invoice_group.id))
#                 rem.append((4,group2.id))
#         if len(rem)>0:
#             vals.update({'groups_id':rem})
#         user = super(ResUsers, self).write(vals)
#                    
#         
#         print("group,""group----After---------------",self.groups_id,vals) 
# #         partner = self.env.user
# #         group = self.env.ref('account.group_account_invoice')
# #         group2 = self.env.ref('zb_building_management.group_property_user')
# #         print(group,group2,"222222")
# #         a =[]
# #         b =[]
# #         for groupz in self.groups_id:
# #             a.append(groupz.id)
# #         if group2.id in a:
# #             if group.id in a:
# #                 f =a.index(group.id)
# #                 a.pop(f)
# #         print(a,"aaaaaaaaaaaaaaaaaaaa-----------------")
# #         vals['groups_id'] = [(4,x) for x in a]     
# #                   
#         return user


    
    
    
