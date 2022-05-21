# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ReportGeneralLedger(models.AbstractModel):
	_inherit = 'report.accounting_pdf_reports.report_general_ledger'

	@api.model
	def get_report_values(self, docids, data=None):
		res = super(ReportGeneralLedger, self).get_report_values(docids, data)
		lang_code = self.env.context.get('lang') or 'en_US'
		lang = self.env['res.lang']
		lang_id = lang._lang_get(lang_code)
		date_format = lang_id.date_format
		if res['data']['date_from']:
			res['data'].update(
				{
				'date_from': datetime.strptime(res['data']['date_from'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),
				})
		if res['data']['date_to']:
			res['data'].update(
				{
				'date_to': datetime.strptime(res['data']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
			})
		if res['Accounts']:
			for accounts in res['Accounts']:
				for lines in accounts.get('move_lines'):
					lines['ldate'] = datetime.strptime(lines['ldate'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
		return res