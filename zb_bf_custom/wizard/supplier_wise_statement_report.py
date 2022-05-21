# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import date

class SupplierStatementReport(models.TransientModel):
    
    _name = 'zb_bf_custom.supplier.statement.report'
    _description = 'Supplier Statement Report'
    
    date = fields.Date("As On Date")

 
    def print_supplier_statement(self):
        
        return self.env.ref('zb_bf_custom.report_supplier_statement_xlsx').report_action(self)

          
                          
     



