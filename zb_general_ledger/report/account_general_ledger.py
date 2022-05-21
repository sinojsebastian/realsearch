from datetime import datetime
import time
from odoo import api, models,fields, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import pytz
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ReportGeneralLedger(models.AbstractModel):
    _inherit= 'report.accounting_pdf_reports.report_general_ledger'
    
    
    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, 0.0 AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                NULL AS currency_id,\
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                '' AS partner_name\
                FROM account_move_line l\
                LEFT JOIN account_move m ON (l.move_id=m.id)\
                LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                JOIN account_journal j ON (l.journal_id=j.id)\
                WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id) \
            WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
        return account_res
    def get_opening_entry(self, account_id, from_date, target_move,partner_id):
        if not account_id.user_type_id.include_initial_balance:
            return {'debit': 0.00, 'credit': 0.00, 'amount_currency':0.00}
        where_cond = "where aml.account_id = %s and aml.date < '%s' and aml.company_id = %s"%(account_id.id, from_date,
                                                                                self.env.user.company_id.id)
        if target_move == 'posted':
            where_cond += " and am.state = 'posted'"
        if partner_id:
            where_cond += " and aml.partner_id = %s"%(partner_id.id)
            
        query = """SELECT COALESCE(sum(aml.debit), 0.00) as debit, COALESCE(sum(aml.credit), 0.00) as credit,
                    COALESCE(sum(aml.amount_currency), 0.00) as amount_currency
                    from account_move_line aml
                    left join account_move am on am.id = aml.move_id %s"""%(where_cond)
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        if data:
            credit = data[0]['credit']
            debit = data[0]['debit']
            amount_currency = data[0]['amount_currency']
        else:
            credit = 0.00
            debit = 0.00
            amount_currency = 0.00
#         return {'debit': debit, 'credit': credit,'amount_currency':amount_currency}
        return debit-credit
    
    def get_ledger_data(self, account_ids, from_date, to_date, target_move, partner_id, analytic_id):
        result = []
        if partner_id:
            _logger.warning('ppppppppppppppppppppppppppppp %s',partner_id)
            com_where_cond = """where aml.date >= '%s' and aml.date <= '%s' and aml.company_id=%s and aml.partner_id=%s"""%(from_date, to_date,
                                                                                                 self.env.user.company_id.id,partner_id.id)
        else:
            
            com_where_cond = """where aml.date >= '%s' and aml.date <= '%s' and aml.company_id=%s"""%(from_date, to_date,
                                                                                                 self.env.user.company_id.id)
        if target_move == 'posted':
            com_where_cond += " and am.state = 'posted'"
        if analytic_id:
            com_where_cond += """ and aml.analytic_account_id=%s"""%(analytic_id.id)
        for account in account_ids:
            if account.user_type_id.include_initial_balance:
                opening_bal = self.get_opening_entry(account, from_date, target_move,partner_id)
                _logger.warning('oooooooooooooooooooooo %s',opening_bal)
            else:
                _logger.warning('oooooooooooooooooooooo else %s',opening_bal)
                opening_bal = 0.00
            where_cond = com_where_cond
            where_cond += " and aml.account_id = %s"%(account.id)
            query = """Select
            aml.name as label,
            aml.ref as reference,
            aml.date as date,
            rp.name as partner,
            am.name as jv_name,
            aj.name as journal,
            aml.debit as debit,
            aml.credit as credit,
            curr.name as currency,
            aml.amount_currency as amount_currency,
            aaa.name as analytic_account
            from account_move_line aml
            left join account_move am on am.id=aml.move_id
            left join res_partner rp on rp.id = aml.partner_id
            left join account_journal aj on aj.id = am.journal_id
            left join res_currency curr on curr.id = aml.currency_id
            left join account_analytic_account aaa on aaa.id = aml.analytic_account_id
            
            %s
            order by aml.date,aml.id
            """%(where_cond)
            self.env.cr.execute(query)
            data = self.env.cr.dictfetchall()
            _logger.warning('data ===================================== %s',data)
#             balance = opening_bal
            balance = 0.0
            debit_sum = 0.0
            credit_sum = 0.0
            balance_sum = 0.0
            for line in data:
                debit_sum += line['debit']
                credit_sum += line['credit']
                _logger.warning('cred------------------------------------%s %s %s',line['credit'],credit_sum,type(line['credit']))
                _logger.warning('debitttt------------------------------------ %s',line['debit'],debit_sum,type(line['debit']))
                balance += (line['debit'] - line['credit'])
                line.update({'balance':balance})
            res = {
                'account_name': "[%s]%s"%(account.code, account.name),
                'opening_balance': opening_bal,
                'data': data,
                'debit_sum':debit_sum,
                'credit_sum':credit_sum,
                'balance_sum':balance
                }
            result.append(res)
        return result
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        _logger.warning('1111111111111111111111111111111 %s 999 999999999999 %s',self,docids)
        super(ReportGeneralLedger, self)._get_report_values(docids, data)
        _logger.warning('get 666666666666666666666666666666 %s .......... %s',self,docids)
        
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_datetime = False
        if cur_time:
            time_obj = datetime.strptime(cur_time, DEFAULT_SERVER_DATETIME_FORMAT)
            tz_time = ''
            tz_name = self._context.get('tz', False) \
                or self.env.user.tz
            if not tz_name:
                raise UserError(_('Please configure your time zone in preferance'))
            if tz_name and time_obj:
                current_datetime = time_obj.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone(tz_name)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if current_datetime:
            printed_on = datetime.strptime(current_datetime,"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
        else:
            printed_on = False
            
        final_account_ids = False
        if data['form'].get('account_ids'):
            if data['form'].get('account_ids'):
                final_account_ids = self.env['account.account'].browse(data['form']['account_ids'])
            else:
                final_account_ids = self.env['account.account'].browse(data['form']['used_context']['account_ids_list'])
        else:
            final_account_ids = self.env['account.account'].search([])
        init_balance = data['form'].get('initial_balance', True)
        sortby = data['form'].get('sortby', 'sort_date')
        display_account = data['form']['display_account']
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        accounts_res = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, init_balance, sortby, display_account)
        _logger.warning('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb _______________________%s',data['form'])
        return {'printed_on':printed_on,
               'get_opening_entry':self.get_opening_entry,
               'final_account_ids':final_account_ids,
               'get_ledger_data':self.get_ledger_data(final_account_ids, data['form']['date_from'], data['form']['date_to'], data['form']['target_move'], '', ''),
                'doc_ids': docids,
                'doc_model': self.model,
                'data': data['form'],
                'Accounts': accounts_res,
                'docs': docs,
                'time': time,
                       }
