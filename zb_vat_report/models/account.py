# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    vat_report_type = fields.Selection([('standard', 'Standard'),
                                        ('zero', 'Zero'),
                                        ('exempt', 'Exempt'),
                                        ('customs_paid','Import Subject Paid to Customs'),
                                        ('reverse_charge_mechanism','Import Subjected to VAT accounted through Reverse Charge Mechanism'),
                                        ('domestic_reverse_charge','Purchase Subjected to domestic Reverse Charge Mechanism'),
                                        ('non-registered suppliers','Purchases from non-registered suppliers, zero-rated purchases/exempt purchases')
                                        ], string="VAT Report Type")


class ResCountry(models.Model):
    _inherit = 'res.country'

    gcc_vat = fields.Boolean(string="GCC VAT Implementing", default=False)
