# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ReportTax(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_tax'

    @api.model
    def _get_report_values(self, docids, data=None):
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form'],
            'lines': self.get_lines(data.get('form')),
            'server_date':DEFAULT_SERVER_DATE_FORMAT,
            'date_format':date_format,
        }

    # def _sql_from_amls_one(self):     // commented by Neha
    #     sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
    #                 FROM %s
    #                 WHERE %s AND "account_move_line".tax_exigible GROUP BY "account_move_line".tax_line_id"""
    #     return sql
    
    def _sql_from_amls_one(self,options,tax_id,vat_dict):
        print('===========_sql_from_amls_one===========',tax_id,vat_dict)
        sql = """SELECT line.tax_line_id,COALESCE(SUM(line.debit-line.credit), 0)
                FROM account_move_line line
                JOIN account_journal journal ON journal.id = line.journal_id
                JOIN account_move move ON line.move_id = move.id
                WHERE line.date <= '%s' and line.date >= '%s'
                AND journal.type = '%s'
                AND line.tax_line_id = %s
                AND move.state = '%s'
                GROUP BY line.tax_line_id
                """%(options['date_to'],options['date_from'],vat_dict['type'],tax_id,'posted')
        return sql

    # def _sql_from_amls_two(self,options,tax_id,vat_dict):
    #     sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
    #              FROM %s
    #              INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
    #              INNER JOIN account_tax t ON (r.account_tax_id = t.id)
    #              WHERE %s AND "account_move_line".tax_exigible GROUP BY r.account_tax_id
    #              AND 
    #              """
    #     return sql
    
    
    def _sql_from_amls_two(self,options,tax_id,vat_dict):
        sql = """
            SELECT
                tax.id,
                 COALESCE(SUM(account_move_line.balance))
            FROM account_move_line 
            JOIN account_move_line_account_tax_rel rel ON rel.account_move_line_id = account_move_line.id
            JOIN account_tax tax ON tax.id = rel.account_tax_id
            JOIN account_journal journal ON journal.id = account_move_line.journal_id
            JOIN account_move move ON move.id = account_move_line.move_id
            WHERE account_move_line.date <= '%s' and account_move_line.date >= '%s' AND tax.tax_exigibility = 'on_invoice'
            AND journal.type = tax.type_tax_use
            AND move.state = '%s'
            GROUP BY tax.id

            UNION ALL

            SELECT
                child_tax.id,
                 COALESCE(SUM(account_move_line.balance))
            FROM account_move_line 
            JOIN account_move_line_account_tax_rel rel ON rel.account_move_line_id = account_move_line.id
            JOIN account_tax tax ON tax.id = rel.account_tax_id
            JOIN account_tax_filiation_rel child_rel ON child_rel.parent_tax = tax.id
            JOIN account_tax child_tax ON child_tax.id = child_rel.child_tax
            WHERE account_move_line.date <= '%s' and account_move_line.date >= '%s'
                AND child_tax.tax_exigibility = 'on_invoice'
                AND tax.amount_type = 'group'
                AND child_tax.amount_type != 'group'
            GROUP BY child_tax.id
                """%(options['date_to'],options['date_from'],'posted',options['date_to'],options['date_from'])
        return sql

    def _compute_from_amls(self, options, taxes):
        #compute the tax amount
        print('=========================taxes',taxes)
        print('=========================options',options)
        for key,val in taxes.items():
            sql = self._sql_from_amls_one(options,key,val)
            self.env.cr.execute(sql)
            # results = self.env.cr.fetchall()  // commented by Neha
            # tables, where_clause, where_params = self.env['account.move.line']._query_get()
            # query = sql % (tables, where_clause)
            # self.env.cr.execute(query, where_params)
            results = self.env.cr.fetchall()
            print('==============results=============',results)
            for result in results:
                print('==========result=============',result)
                if result[0] in taxes:
                    taxes[result[0]]['tax'] = abs(result[1])

        # compute the net amount
            sql2 = self._sql_from_amls_two(options,key,val)
            self.env.cr.execute(sql2)
            results = self.env.cr.fetchall()
            # query = sql2 % (tables, where_clause)
            # self.env.cr.execute(query, where_params)
            print('=============results=============',results)
            for result in results:
                if result[0] in taxes:
                    taxes[result[0]]['net'] = abs(result[1])

    @api.model
    def get_lines(self, options):
        taxes = {}
        for tax in self.env['account.tax'].search([('type_tax_use', '!=', 'none')]):
            if tax.children_tax_ids:
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    taxes[child.id] = {'tax': 0, 'net': 0, 'name': child.name, 'type': tax.type_tax_use}
            else:
                taxes[tax.id] = {'tax': 0, 'net': 0, 'name': tax.name, 'type': tax.type_tax_use}
        self.with_context(date_from=options['date_from'], date_to=options['date_to'], strict_range=True)._compute_from_amls(options, taxes)
        groups = dict((tp, []) for tp in ['sale', 'purchase'])
        for tax in taxes.values():
            if tax['tax']:
                groups[tax['type']].append(tax)
        return groups
