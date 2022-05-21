from odoo import models, fields, api,_

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

class PartnerLedgerXlsx(models.AbstractModel):
    _name = 'report.account_dynamic_plg.partner_ledger_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
        """
        self.format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 14,
            'bg_color': '#FFF58C',
            'border': False
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True
        })
        self.content_header = workbook.add_format({
            'bold': False,
            'bg_color': '#FFFFFF',
            'border': True
        })
        self.line_header = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFFF',
            'border': False
        })
        self.line_header_light = workbook.add_format({
            'bold': False,
            'bg_color': '#FFFFFF',
            'border': True
        })

    def prepare_report_filters(self,filter):
        self.row_pos += 3
        if filter:
            # Date from
            self.sheet.write_string(self.row_pos, 0, _('Date from'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 1, _('Date to'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 2, _('Target moves'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 3, _("Partner's"),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 4, _('With currency'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 5, _('Reconciled'),
                                    self.format_header)
            self.row_pos += 1

            self.sheet.write_string(self.row_pos, 0, str(filter.get('date_from')),
                                    self.content_header)
            self.sheet.write_string(self.row_pos, 1, str(filter.get('date_to')),
                                    self.content_header)
            self.sheet.write_string(self.row_pos, 2, str(filter.get('target_move')),
                                    self.content_header)

            if filter['result_selection'] == 'customer':
                self.sheet.write_string(self.row_pos, 3, _('Receivable accounts'),
                                        self.content_header)
            if filter['result_selection'] == 'supplier':
                self.sheet.write_string(self.row_pos, 3, _('Payable accounts'),
                                        self.content_header)
            if filter['result_selection'] == 'customer_supplier':
                self.sheet.write_string(self.row_pos, 3, _('Receivable and Payable accounts'),
                                        self.content_header)

            if filter['amount_currency']:
                self.sheet.write_string(self.row_pos, 4, 'Yes',
                                        self.content_header)
            else:
                self.sheet.write_string(self.row_pos, 4, 'No',
                                        self.content_header)

            if filter['reconciled']:
                self.sheet.write_string(self.row_pos, 5, 'Yes',
                                        self.content_header)
            else:
                self.sheet.write_string(self.row_pos, 5, 'No',
                                        self.content_header)


    def prepare_report_contents(self, Accounts, Filters):
        self.row_pos += 3
        if Accounts:
            self.sheet.write_string(self.row_pos, 0, _('Date'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 1, _('Journal'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 2, _('Account'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 3, _('Ref'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 4, _('Debit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 5, _('Credit'),
                                    self.format_header)
            self.sheet.write_string(self.row_pos, 6, _('Balance'),
                                    self.format_header)
            if Filters['form']['amount_currency']:
                self.sheet.write_string(self.row_pos, 7, _('Currency'),
                                        self.format_header)
            for line in Accounts:
                self.row_pos += 1
                if line['main']:
                    if line.get('ref'):
                        self.sheet.write_string(self.row_pos, 0, str(line.get('ref'),
                                                self.line_header))
                    else:
                        self.sheet.write_string(self.row_pos, 0, '',
                                                self.line_header)
                    self.sheet.write_string(self.row_pos, 1, str(line.get('name')),
                                            self.line_header)
                    self.sheet.write_string(self.row_pos, 4, self._format_currency(line['debit'], line['precision']),
                                            self.line_header)
                    self.sheet.write_string(self.row_pos, 5, self._format_currency(line['credit'], line['precision']),
                                            self.line_header)
                    self.sheet.write_string(self.row_pos, 6, self._format_currency(line['debit-credit'], line['precision']),
                                            self.line_header)
                if not line['main']:
                    self.sheet.write_string(self.row_pos, 0, str(line.get('date')),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 1, str(line.get('code')),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 2, str(line.get('a_name')),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 3, str(line.get('displayed_name')),
                                            self.line_header_light)

                    self.sheet.write_string(self.row_pos, 4, self._format_currency(line['debit'],line['precision']),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 5, self._format_currency(line['credit'],line['precision']),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 6, self._format_currency(line['progress'], line['precision']),
                                            self.line_header_light)
                    if Filters['form']['amount_currency']:
                        if line['currency_id']:
                            a = str(line['amount_currency']) + str(line.get('currency_code'))
                            self.sheet.write_string(self.row_pos, 7, a,
                                                    self.line_header_light)
                        else:
                            self.sheet.write_string(self.row_pos, 7, '-',
                                                    self.line_header_light)

    def _format_currency(self, amount, precision):
        format_amount = b = '{:.' + str(precision) + 'f}'
        return format_amount.format(amount)

    def generate_xlsx_report(self, workbook, data, ids):
        self._define_formats(workbook)
        self.row_pos = 0
        self.sheet = workbook.add_worksheet('Partner Ledger')
        self.sheet.merge_range(0, 0, 0, 5, 'Partner Ledger', self.format_title)
        if data:
             # Filter section
             self.prepare_report_filters(data['data']['form'])
             # Content section
             self.prepare_report_contents(data['lines'],data['data'])
