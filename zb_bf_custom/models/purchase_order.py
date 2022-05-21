from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    
    owner_approval = fields.Selection([
                    ('notrequired', 'Not Required'),
                    ('waiting', 'Waiting'),
                    ('approved','Approved'),
                    ('rejected','Rejected'),
                    ], 'Owner Approval ',default='notrequired')