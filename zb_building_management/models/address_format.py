from datetime import datetime, timedelta
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from lxml import etree
import json    
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
 

class res_partner(models.Model):
    _inherit = "res.partner"
    _description = 'Partner'
    
    
    @api.onchange('partnerz_id')
    def get_cr(self):
        for cr in self:
            if cr.partnerz_id and cr.partnerz_id:
                if cr.partnerz_id.cr:
                    cr.cr= cr.partnerz_id.cr
                
    
    deed = fields.Char('Deed Number')
    proper = fields.Char('Property Number')
    fax = fields.Char('Fax')
    partnerz_id = fields.Many2one('res.partner','Owner', domain=[('company_type','=', 'company')])
    attachment_id4_cr = fields.Many2many('ir.attachment', 'caddress_ir_attachcr_rel', 'cr_id', 'attachmnt_id', 'CR/CPR')
    attachment_id4_cr1 = fields.Many2many('ir.attachment', 'caddress_ir_attachcr_rel1', 'cr1_id', 'attachmnt_id1', 'Business Card')
    attachment_id4_cr2= fields.Many2many('ir.attachment', 'caddress_ir_attachcr_rel2', 'cr2_id', 'attachmnt_id2', 'Vendor Card')
    attachment_id4_cr3 = fields.Many2many('ir.attachment', 'caddress_ir_attachcr_rel3', 'cr3_id', 'attachmnt_id3', 'Additional Document')


class res_company(models.Model):
    _inherit = "res.company"
    _description = 'Company'
    
    agent_commission_comment = fields.Text(String="Agent Commission Text")
    arab_address = fields.Text('Address In Arabic')
    fax = fields.Char('Fax')
