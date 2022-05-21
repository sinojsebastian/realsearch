from odoo import models, api, fields, _
from odoo.tools.misc import format_date
from odoo.addons.web.controllers.main import clean_action

class AccountReport(models.AbstractModel):
    _description = "Account Report"
    _inherit = 'account.report'
    
    def open_action(self, options, domain,tax):
        assert isinstance(domain, (list, tuple))
        domain += [('date', '>=', options.get('date').get('date_from')),
                   ('date', '<=', options.get('date').get('date_to')),('journal_id.type','=',tax.type_tax_use)]
        if not options.get('all_entries'):
            domain += [('move_id.state', '=', 'posted')]

        ctx = self.env.context.copy()
        ctx.update({'search_default_account': 1, 'search_default_groupby_date': 1})

        action = self.env.ref('account.action_move_line_select_tax_audit').read()[0]
        action = clean_action(action)
        action['domain'] = domain
        action['context'] = ctx
        return action

    def open_tax(self, options, params=None):
        print('============open_tax=============')
        active_id = int(str(params.get('id')).split('_')[0])
        print('===========active_id===============',active_id)
        tax = self.env['account.tax'].browse(active_id)
        domain = ['|', ('tax_ids', 'in', [active_id]),
                       ('tax_line_id', 'in', [active_id])]
        if tax.tax_exigibility == 'on_payment':
            domain += [('tax_exigible', '=', True)]
        return self.open_action(options, domain,tax)
    
    def tax_tag_template_open_aml(self, options, params=None):
        active_id = int(str(params.get('id')).split('_')[0])
        tax = self.env['account.tax'].browse(active_id)
        tag_template = self.env['account.tax.report.line'].browse(active_id)
        domain = [('tag_ids', 'in', tag_template.tag_ids.ids), ('tax_exigible', '=', True)]
        return self.open_action(options, domain,tax)

    def open_tax_report_line(self, options, params=None):
        active_id = int(str(params.get('id')).split('_')[0])
        tax = self.env['account.tax'].browse(active_id)
        line = self.env['account.financial.html.report.line'].browse(active_id)
        domain = ast.literal_eval(line.domain)
        action = self.open_action(options, domain,tax)
        action['display_name'] = _('Journal Items (%s)') % line.name
        return action


class report_account_aged_partner(models.AbstractModel):
    _inherit = "account.aged.partner"
    _description = "Aged Partner Balances"

    
    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _("Due Date"), 'class': 'date', 'style': 'white-space:nowrap;'},
            {'name': _("Journal"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'},
            {'name': _("Reference"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'},
            {'name': _("Account"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'},
            {'name': _("Exp. Date"), 'class': 'date', 'style': 'white-space:nowrap;'},
            {'name': _("As of: %s") % format_date(self.env, options['date']['date_to']), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("1 - 30"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("31 - 60"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("61 - 90"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("91 - 120"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("Older"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
            {'name': _("Total"), 'class': 'number sortable', 'style': 'white-space:nowrap;'},
        ]
        return columns
    
    @api.model
    def _get_lines(self, options, line_id=None):
        # print('============_get_lines=====================',options)
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        context = {'include_nullified_amount': True}
        if line_id and 'partner_' in line_id:
            # we only want to fetch data about this partner because we are expanding a line
            partner_id_str = line_id.split('_')[1]
            if partner_id_str.isnumeric():
                partner_id = self.env['res.partner'].browse(int(partner_id_str))
            else:
                partner_id = False
            context.update(partner_ids=partner_id)
        results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(**context)._get_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)

        for values in results:
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v}
                                                 for v in [values['direction'], values['4'],
                                                           values['3'], values['2'],
                                                           values['1'], values['0'], values['total']]],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
                'partner_id': values['partner_id'],
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    if aml.move_id.is_purchase_document():
                        caret_type = 'account.invoice.in'
                    elif aml.move_id.is_sale_document():
                        caret_type = 'account.invoice.out'
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    else:
                        caret_type = 'account.move'

                    line_date = aml.date_maturity or aml.date
                    if not self._context.get('no_format'):
                        line_date = format_date(self.env, line_date)
                    vals = {
                        'id': aml.id,
                        'name': aml.move_id.name,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in [format_date(self.env, aml.date_maturity or aml.date), aml.journal_id.code,aml.move_id.ref, aml.account_id.display_name, format_date(self.env, aml.expected_pay_date)]] +
                                   [{'name': self.format_value(sign * v, blank_if_zero=True), 'no_format': sign * v} for v in [line['period'] == 6-i and line['amount'] or 0 for i in range(7)]],
                        'action_context': {
                            'default_type': aml.move_id.type,
                            'default_journal_id': aml.move_id.journal_id.id,
                        },
                        'title_hover': self._format_aml_name(aml.name, aml.ref, aml.move_id.name),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v} for v in [total[6], total[4], total[3], total[2], total[1], total[0], total[5]]],
            }
            lines.append(total_line)
        return lines