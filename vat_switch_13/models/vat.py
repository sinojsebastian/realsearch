# -*- coding: utf-8 -*-


import logging
import datetime

from odoo import api, fields, models, _, tools

_logger = logging.getLogger(__name__)


class VATSwitch(models.Model):
    _name = "vat.switch"
    _description = "VAT Switch"

    name = fields.Char(string='Name', required=True, readonly=True, states={'draft': [('readonly', False)]})
    switch_date = fields.Datetime(string='Switch Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=True, default=fields.Datetime.now().replace(year=fields.Datetime.now().year+1, month=1, day=1, hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S'), help="Time of VAT switch")
    state = fields.Selection([
        ('draft', 'New'),
        ('active', 'Active and waiting'),
        ('done', 'Executed'),
        ], string='Status', readonly=True, copy=False, default='draft')

    vat_mapping_ids = fields.One2many('vat.switch.mapping', 'vat_switch_id', string='VAT Mapping', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    cron_id = fields.Many2one('ir.cron', string='Scheduler', required=True, default=lambda self: self.env.ref('vat_switch_13.ir_cron_vat_switch', raise_if_not_found=False))

    def action_confirm(self):
        self.write({'state': 'active'})
        
    def action_cancel(self):
        self.write({'state': 'draft'})
        
    def _update_vat(self):        
        records = self.search([('state', '=', 'active'), ('switch_date', '<=', fields.Date.today())])
        for record in records:
            for line in record.vat_mapping_ids:
                product_ids=[]
                if line.categ_ids:
                    product_ids = self.env['product.template'].search([('categ_id','child_of',[x.id for x in line.categ_ids])])
                else:
                    product_ids =  self.env['product.template'].search([])                    
                    
                for product in product_ids:
                    tax_ids = [x.id for x in product.taxes_id]
                    if line.from_vat_id.id in tax_ids:
                        tax_ids.remove(line.from_vat_id.id)
                        tax_ids.append(line.to_vat_id.id)
                        product.write({'taxes_id':[[6, False, tax_ids]]})
                    s_tax_ids = [x.id for x in product.supplier_taxes_id]
                    if line.from_vat_id.id in s_tax_ids:
                        s_tax_ids.remove(line.from_vat_id.id)
                        s_tax_ids.append(line.to_vat_id.id)
                        product.write({'taxes_id':[[6, False, s_tax_ids]]})
            record.write({'state' : 'done'})
        return True

class VATSwitchMapping(models.Model):
    _name = "vat.switch.mapping"
    _description = "VAT Switch Mapping"

    vat_switch_id = fields.Many2one('vat.switch', string='VAT Switch', required=True, ondelete='cascade', index=True, copy=False)
    categ_ids = fields.Many2many('product.category', 'vat_switch_mapping_categ_rel', 'mapping_line_id', 'categ_id', string='Product Category [Optional]')
    from_vat_id = fields.Many2one('account.tax', string='From VAT', required=True)
    to_vat_id = fields.Many2one('account.tax', string='To Vat', required=True)

