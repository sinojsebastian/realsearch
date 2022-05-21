# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
import json
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ReportDynamicPartnerLedger(models.AbstractModel):
    _name = 'report.account.dynamic.report_partnerledger'

    def get_date_from_filter(self, filter):
        '''
        :param filter: dictionary
                {u'disabled': False, u'text': u'This month', u'locked': False, u'id': u'this_month', u'element': [{}]}
        :return: date_from and date_to
        '''
        if filter.get('id'):
            date = datetime.today()
            if filter['id'] == 'today':
                date_from = date.strftime("%Y-%m-%d")
                date_to = date.strftime("%Y-%m-%d")
                return date_from, date_to
            if filter['id'] == 'this_week':
                day_today = date - timedelta(days=date.weekday())
                date_from = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
                return date_from, date_to
            if filter['id'] == 'this_month':
                date_from = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                date_to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
                return date_from, date_to
            if filter['id'] == 'this_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # First quarter
                    date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # First quarter
                    date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # First quarter
                    date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
                return date_from, date_to
            if filter['id'] == 'this_financial_year':
                date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(day=1))
            if filter['id'] == 'yesterday':
                date_from = date.strftime("%Y-%m-%d")
                date_to = date.strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(day=7))
            if filter['id'] == 'last_week':
                day_today = date - timedelta(days=date.weekday())
                date_from = (day_today - timedelta(days=date.weekday())).strftime("%Y-%m-%d")
                date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(months=1))
            if filter['id'] == 'last_month':
                date_from = datetime(date.year, date.month, 1).strftime("%Y-%m-%d")
                date_to = datetime(date.year, date.month, calendar.mdays[date.month]).strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(months=3))
            if filter['id'] == 'last_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 3, calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 6, calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 9, calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 12, calendar.mdays[12]).strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(years=1))
            if filter['id'] == 'last_financial_year':
                date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                return date_from, date_to

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code, m.id AS move_id
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date'].strftime(date_format)
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id')).id
            r['currency_symbol'] = currency.browse(r.get('currency_id')).symbol
            r['currency_precision'] = currency.browse(r.get('currency_id')).decimal_places
            full_account.append(r)
        return full_account

    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))
        lines_op = []
        k = 1
        for partner in partners:
            lines_op.append({'debit':self._sum_partner(data, partner, 'debit'),
                             'credit':self._sum_partner(data, partner, 'credit'),
                             'debit-credit': self._sum_partner(data, partner, 'debit - credit'),
                             'main': True,
                             'id': k,
                             'ref': partner.ref,
                             'name': partner.name,
                             'symbol': self.env.user.company_id.currency_id.symbol,
                             'precision': self.env.user.company_id.currency_id.decimal_places,
                             'position': self.env.user.company_id.currency_id.position
                             })
            for line in self._lines(data, partner):
                line['parent'] = k
                line['main'] = False
                line['symbol'] = self.env.user.company_id.currency_id.symbol
                line['precision'] = self.env.user.company_id.currency_id.decimal_places
                line['position'] = self.env.user.company_id.currency_id.position
                lines_op.append(line)
            k += 1

        return {
            'data': data,
            'lines': lines_op,
        }

    def prepare_local_ctx(self, docids, data=None):
        data = dict({'form': data})

        date_from, date_to = False, False
        used_context = {}
        if data['form'].get('date_filter'):
            date_from, date_to = self.get_date_from_filter(data['form'].get('date_filter')[0])
            used_context['date_from'] = date_from
            used_context['date_to'] = date_to
            data['form']['date_from'] = date_from
            data['form']['date_to'] = date_to
        else:
            used_context['date_from'] = data['form'].get('date_from', False)
            used_context['date_to'] = data['form'].get('date_to', False)

        used_context['strict_range'] = True
        used_context['journal_ids'] = data['form']['journal_ids']
        used_context['date_to'] = data['form'].get('date_to', '')
        used_context['date_from'] = data['form'].get('date_from', '')
        used_context['state'] = data['form'].get('target_move', '')
        data['form']['used_context'] = used_context
        return docids,data


    @api.model
    def action_view(self, docids, data=None):
        docids, data = self.prepare_local_ctx(docids, data)
        report_vals = self.get_report_values(docids, data)
        return json.dumps(report_vals)

    @api.model
    def action_pdf(self, docids, data=None):
        docids, data = self.prepare_local_ctx(docids, data)
        report_lines = self.get_report_values(docids, data)
        # this dict is new (for original,uncomment line 280 and comment 279)
        if not data['form']['date_filter']:
            if not data['form']['used_context']['date_from'] or not data['form']['used_context']['date_to']:
                raise UserError(_("Enter Start Date and End Date"))
            
        dict = {'journal_ids': report_lines['data']['form']['journal_ids'], 
              'amount_currency': report_lines['data']['form']['amount_currency'], 
              'reconciled':report_lines['data']['form']['reconciled'], 
              'result_selection': report_lines['data']['form']['result_selection'], 
              'target_move': report_lines['data']['form']['target_move'], 
              'date_from':  report_lines['data']['form']['date_from'],
              'date_to': report_lines['data']['form']['date_to'],
                 
            }

        wizard = self.env['account.report.partner.ledger'].create(dict)
#         wizard = self.env['account.report.partner.ledger'].create(report_lines['data']['form'])
        action = wizard._print_report(report_lines['data'])
        action['context']['active_id'] = action['context']['active_ids'][0]
        action['context']['active_model'] = 'account.report.partner.ledger'
        return action

    @api.model
    def action_xlsx(self, docids, data=None):
        docids, data = self.prepare_local_ctx(docids, data)
        report_vals = self.get_report_values(docids, data)
        return report_vals