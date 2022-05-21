# -*- coding: utf-8 -*-

from odoo import models


class AccMoveReport(models.Model):
    _inherit = 'account.move'

    def print_journal_entry(self):
        self.ensure_one()
        return self.env.ref('zb_journal_entry_report.report_journal_entry').report_action(self)
