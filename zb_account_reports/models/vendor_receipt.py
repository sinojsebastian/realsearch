from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning


class ReceiptVoucherReportQWeb(models.AbstractModel):
    _name = 'report.zb_account_reports.report_payment_receipt'
    _description = 'Model For Vendor Receipt'

    @api.model
    def _get_report_values(self, docids, data=None):
        payment_ids = self.env['account.payment'].browse(docids)
        for payment_id in payment_ids:
            if payment_id.state == 'draft':
                raise Warning(_('You cannot take the print on Draft payment'))
        return {
            'doc_ids': docids,
            'docs': self.env['account.payment'].browse(docids),
            'doc_model': self.env['account.payment'],
        }














