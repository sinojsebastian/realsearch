from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    
    ticket = fields.Selection([
            ('satisfactory', 'Satisfactory'),
            ('unsatisfactory', 'Unsatisfactory')],default='satisfactory')
    reason = fields.Selection([
            ('not_completed', 'Job Not Completed'),
            ('repeated', 'Job Repeated'),
            ('not_cleaned','Site Not Cleaned'),
            ('delayed','Job Delayed')])
    
    narration = fields.Text('Narration')  
    
    area =   fields.Selection([
            ('common_area', 'Common Area')])
    call_conducted = fields.Boolean('Call Conducted')   
    

            
class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'
    _description = 'Helpdesk Stage'
    
    running_stage = fields.Boolean('Running Stage')
    
    