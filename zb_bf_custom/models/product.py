
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Product Template"
    
    
    ewa = fields.Boolean(string="EWA")
    
    
class ProductProduct(models.Model):
    _inherit = "product.product"
    _description = "Product"
    
    
    service_product_journal_id = fields.Many2one('account.journal',string="Service Product Journal")
    service_product_vendor_journal_id = fields.Many2one('account.journal',string="Service Purchase Journal")
    service_product_partner_id = fields.Many2one('res.partner',string="Service Provider")
    
    