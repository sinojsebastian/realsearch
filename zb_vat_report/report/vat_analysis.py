# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class VatAnalysisReport(models.Model):
    _name = "vat.analysis.report"
    _description = "Vat Analysis"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    date = fields.Date(readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    move_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    account_id = fields.Many2one('account.account', string="Account", readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    origin = fields.Char(string='Source Document', readonly=True)
    invoice_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund'),
    ], 'Invoice Type', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    name = fields.Char(string="Description", readonly=True)
    product_qty = fields.Float(string='Quantity', readonly=True)
    price_total = fields.Float(string='Total W/O Tax', readonly=True)
    taxes = fields.Char(string='Taxes', readonly=True)
    tax_amount = fields.Float(string='Tax Amount', readonly=True)
    price_subtotal = fields.Float(string='Total With Tax', readonly=True, digits=(16, 3))
    debit = fields.Float(string="Debit", readonly=True, digits=(16, 3))
    credit = fields.Float(string="Credit", readonly=True, digits=(16, 3))
    vat_report_type = fields.Selection([('Standard', 'Standard Rate'),
                                        ('exempt', 'Exempted'),
                                        ('zero', 'Zero Rate'),
                                        ('rev_charge', 'Reverse Charge')],
                                       string='VAT Type')

    def _select(self):
        select_str = """
                SELECT aml.id as id,
                    am.date AS date,
                    am.name as name,
                    am.id as move_id,
                    aml.account_id as account_id,
                    aml.partner_id as partner_id,
                    am.name as origin,
                    aml.quantity as product_qty,
                    at.name as taxes,
                    CASE when
                        aml.move_id IS NOT NULL
                        then
                            am.type
                        end
                    as invoice_type,
                    at.vat_report_type as vat_report_type,
                    rcm.id as company_id,
                    SUM(aml.credit) as credit,
                    SUM(aml.debit) as debit,
                    abs(SUM(aml.credit-aml.debit)) as tax_amount,
                    CASE WHEN
                        aml.tax_line_id IS NULL
                        then 
                            abs(SUM((aml.credit-aml.debit)/(.05))) 
                        else
                            
                            CASE WHEN
                                at.amount > 0.000
                                then
                                    abs(SUM((aml.credit-aml.debit)*100)/at.amount)
                                
                                else
                                    0.000   
                                end
                        end
                    as price_total,
                    CASE WHEN
                        aml.tax_line_id IS NULL

                        then
                            abs(SUM((aml.credit-aml.debit)+((aml.credit-aml.debit)/(.05))))
                        else
                            abs(SUM((aml.credit-aml.debit)*100)/at.amount)
                    end as price_subtotal
        """
        return select_str

    def _from(self):
        from_str = """
                FROM account_move_line aml
                left join account_move am on am.id = aml.move_id
                left join account_account ac on ac.id = aml.account_id
                left join account_tax at on at.id = aml.tax_line_id
                LEFT JOIN product_product pp ON pp.id = aml.product_id
                LEFT JOIN res_partner rp ON rp.id = aml.partner_id
                LEFT JOIN res_company rcm on rcm.id= aml.company_id
                LEFT JOIN account_journal aj on aj.id= aml.journal_id
        """
        return from_str

    def _where(self, cr):
        account_final = []

        account_str = """select at.account_id from
                                account_tax_repartition_line at"""

        cr.execute(account_str)

        account_list = cr.dictfetchall()
        for account in account_list:
            if account.get('account_id', False):
                account_final.append(account.get('account_id', False) or False)
            if account.get('refund_account_id', False):
                account_final.append(account.get('refund_account_id', False) or False)
        where = """ where am.state in ('posted')"""
        if account_final:
            where += """ and aml.account_id in %s""" % (str(tuple(account_final)))
        return where

    def _group_by(self):
        group_by_str = """
                GROUP BY aml.account_id, 
                    aml.id, 
                    am.id,
                    am.date,
                    am.name,
                    rp.state_id,
                    aml.partner_id,
                    aml.name,
                    aml.product_id,
                    aml.quantity,
                    at.name,
                    am.type,
                    rcm.id,
                    at.amount,
                    at.vat_report_type
                    """
        return group_by_str

    @api.model
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as(
                %s %s %s %s)"""
                            % (self._table,
                               self._select(), self._from(), self._where(self.env.cr), self._group_by()))
