# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, fields,_lt
from odoo.tools.misc import format_date
from odoo.exceptions import UserError,Warning,ValidationError




class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    code = fields.Char(string='Code', size = 15, Translate = True, readonly = True,default='New')
    owner = fields.Boolean('Owner',default=False)
    payment_mode = fields.Selection([
                    ('cash', 'Cash'),
                    ('bank', 'Bank'),
                    ('cheque','Cheque'),
                    ], 'Payment Mode',default='cash')
#     nationality_arabic = fields.Char(string='Nationality in Arabic')
    cpr_arabic = fields.Char(string='CPR in Arabic')
    passport_arabic = fields.Char(string='Passport in Arabic')
    name_arabic = fields.Char(string='Name in Arabic')
    address_arabic = fields.Text(string='Address in Arabic')
    nationality_id = fields.Many2one('res.nationality','Nationality')
    pa_ids = fields.Many2many('res.users',compute='_compute_pa', store=True,string="Property Adviser")
    owner_module_ids =fields.One2many('zbbm.module','owner_id','Modules Owner list')
    tenant_module_ids =fields.One2many('zbbm.module','tenant_id','Modules Tenant list')
    additional_pa_ids = fields.Many2many('res.users', 'partner_pa_rel', 'partner_id', 'pa_id',string="Additional PA")
    crm_process = fields.Selection(
        [('sale', 'Sale'),
        ('resale', 'Resale'),
        ('rental', 'Rental Activity'),
        ], 'Process')
    
    
    def get_owner_id(self,module_id,lease_id):
        params = self.env['ir.config_parameter'].sudo()    
        move_config_owner_id = params.get_param('zb_bf_custom.owner_id') or False
        config_owner_obj = self.browse(int(move_config_owner_id))
        if not move_config_owner_id:
            raise Warning(_('Please Configure Owner'))
        owner_id = False
        if lease_id and not module_id:
            # lease = self.env['zbbm.module.lease.rent.agreement'].browse(lease_id)
            owner_id = lease_id.owner_id
        elif not lease_id and module_id:
            # module = self.env['zbbm.module'].browse(module_id)
            if module_id.offer_start_date and module_id.offer_end_date:
                owner_id = config_owner_obj
            else:
                owner_id = module_id.owner_id
        elif lease_id and module_id:
            # lease = self.env['zbbm.module.lease.rent.agreement'].browse(lease_id)
            # module = self.env['zbbm.module'].browse(module_id)
            if module_id.offer_start_date and module_id.offer_end_date:
                if lease_id.agreement_start_date >= module_id.offer_start_date and lease_id.agreement_start_date <= module_id.offer_end_date:
                    owner_id = config_owner_obj
                else:
                    owner_id = module_id.owner_id
            else:
                owner_id = module_id.owner_id
        else:
            owner_id = config_owner_obj
                    
            
        return owner_id
    
    
    
    @api.depends('tenant_module_ids','owner_module_ids','additional_pa_ids')
    def _compute_pa(self):
        self.pa_ids = False
        for record in self:
            pa_list = []
            final_modules = list(set(record.owner_module_ids.ids + record.tenant_module_ids.ids))
            building_ids = list(set([x.building_id for x in self.env['zbbm.module'].browse(final_modules)]))
            building_list = []
            for building in building_ids:
                pa_list += building.pa_ids.ids 
                building_list.append(building.building_address)
            add_pa_ids = list(set(record.additional_pa_ids.ids))
            for pa in add_pa_ids:
                pa_list.append(pa)
            if pa_list :
                record.pa_ids = list(set(pa_list))
                for buil in building_list:
                    buil.pa_ids = list(set(pa_list))
    
    @api.model
    def create(self, vals):
        context = self._context
        if self._context.get('module_tenant') or vals.get('is_tenant') == True or self._context.get('default_is_tenant'):
            seq = self.env['ir.sequence'].next_by_code('tenant') 
            vals['code'] = seq
        else:
            seq = self.env['ir.sequence'].next_by_code('res.partner') 
            vals['code'] = seq
        
        if 'is_a_prospect' in context:
            pass
            
        elif 'default_crm_process' in context and context.get('default_crm_process') == 'rental':
            pass
        
        elif 'lease_reference_person' in context and context.get('lease_reference_person') == True:
            pass
        
        elif 'default_is_an_agent' in context:
            pass
        
        elif 'is_company' in vals and vals['is_company'] == False:
            if 'res_partner_search_mode' in context and context['res_partner_search_mode'] == 'customer':
                if 'default_crm_process' in context and context.get('default_crm_process') in ['sale','resale']:
                    if 'cpr' in vals and not vals['cpr']:
                        if 'passport' in vals and not vals['passport'] and not self.passport:
                            raise ValidationError(_("Please enter CPR or Passport!!"))
                    else:
                        if 'passport' not in vals:
                            raise ValidationError(_("Please enter CPR or Passport!!"))
                else:
                    if 'cpr' in vals and not vals['cpr'] and not self.cpr:
                        if 'passport' in vals and not vals['passport'] and not self.passport:
                            raise ValidationError(_("Please enter CPR or Passport!!"))
            elif 'res_partner_search_mode' in context and context['res_partner_search_mode'] == 'supplier':
                pass
            else:
                if 'cpr' in vals and not vals['cpr'] and not self.cpr:
                    if 'passport' in vals and not vals['passport'] and not self.passport:
                        raise ValidationError(_("Please enter CPR or Passport!!"))
        return super(ResPartner, self).create(vals)
    
    
    @api.model
    def default_get(self,fields):
        res = super(ResPartner, self).default_get(fields)
        if self._context.get('default_owner')=='1':
            res.update({
            'owner': True ,
            'customer' : True
                    })
        elif self._context.get('res_partner_search_mode') == 'supplier':
            res.update({
            'supplier': True,
            'customer' : True
                    })
        return res
    
    def name_get(self):
        result = super(ResPartner, self.sudo()).name_get()    
        return result

    def open_journal_items(self):
        action = self.env.ref('account.action_account_moves_all').read()[0]
        action['domain'] = [('partner_id','=',self.id)]
        action['context'] = {'search_default_posted':1,'search_default_building_ref_id':1,'search_default_module_id':1,'search_default_receivable':1}
        return action
        
    
class ResNationality(models.Model):
    _name = "res.nationality"
    _description = "Partner Nationality"
    
    name = fields.Char('Nationality')
    nationality_arabic = fields.Char('Nationality in Arabic')
    
class Resusers(models.Model):
    _inherit = 'res.users'
    
    name_arabic = fields.Char('Name in Arabic')
    
class ResBank(models.Model):
    _inherit = 'res.bank'
    
    bank_name_arabic = fields.Char('Name in Arabic')
    
class ResPartnerTitle(models.Model):
    _inherit = 'res.partner.title'
    
    
    abbr_arabic = fields.Char('Abbreviation In Arabic')
    
    
     

class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"
   
    filter_unit = True
    filter_owner_vendor = False
    filter_partner_type = [
        {'id': 'owner', 'name': _lt('Owner'), 'selected': False},
        {'id': 'vendor', 'name': _lt('Vendor'), 'selected': False},
        {'id': 'tenant', 'name': _lt('Tenant'), 'selected': False},
    ]


    # UNIT FILTER INTIALIZATION
    @api.model
    def _init_filter_unit(self, options, previous_options=None):
        if not self.filter_unit:
            return
        options['unit'] = True
        options['unit_ids'] = previous_options and previous_options.get('unit_ids') or []
        selected_unit_ids = [int(unit) for unit in options['unit_ids']]
        selected_units = selected_unit_ids and self.env['zbbm.module'].browse(selected_unit_ids) or self.env['zbbm.module']
        options['selected_unit_ids'] = selected_units.mapped('name')

    @api.model
    def _get_options_unit_domain(self, options):
        domain = []
        if options.get('unit_ids'):
            unit_ids = [int(unit) for unit in options['unit_ids']]
            domain.append(('module_id', 'in', unit_ids))
        return domain
    
    
    @api.model
    def _get_options_partner_type(self, options):
        ''' Get select account type in the filter widget (see filter_account_type).
        :param options: The report options.
        :return:        Selected account types.
        '''
        domain = []
        for partner_type_option in options.get('partner_type', []):
            if partner_type_option['id'] == 'owner':
                if partner_type_option['selected']:
                    domain.append(('partner_id.owner', '=', True))
            if partner_type_option['id'] == 'vendor':
                if partner_type_option['selected']:
                    domain.append(('partner_id.supplier', '=', True))
            if partner_type_option['id'] == 'tenant':
                if partner_type_option['selected']:
                    domain.append(('partner_id.is_tenant', '=', True))
        return domain
    
    @api.model
    def _get_options_domain(self, options):
        print('==============options===============',options)
        # OVERRIDE
        # Handle filter_unreconciled + 
        domain = super(ReportPartnerLedger, self)._get_options_domain(options)
        domain += self._get_options_unit_domain(options)
        if options.get('unreconciled'):
            domain.append(('reconciled','=',False))
        domain += self._get_options_partner_type(options)
        return domain
    

    #OVERRIDE JS CALL FUNCTION TO INCLUDE
    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        
        options = self._get_options(options)
        

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in (options.get('partner_categories') or [])]
        if options.get('unit'):
            options['selected_unit_ids'] = [self.env['zbbm.module'].browse(int(unit)).name for unit in options['unit_ids']]
        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        if options.get('journals'):
            journals_selected = set(journal['id'] for journal in options['journals'] if journal.get('selected'))
            for journal_group in self.env['account.journal.group'].search([('company_id', '=', self.env.company.id)]):
                if journals_selected and journals_selected == set(self._get_filter_journals().ids) - set(journal_group.excluded_journal_ids.ids):
                    options['name_journal_group'] = journal_group.name
                    break

        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view'].render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        
        return info

    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _('JRNL')},
            {'name': _('Unit')},
            {'name': _('Account')},
            {'name': _('Ref')},
            {'name': _('Due Date'), 'class': 'date'},
            {'name': _('Matching Number')},
            {'name': _('Initial Balance'), 'class': 'number'},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'}]

        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': _('Amount Currency'), 'class': 'number'})

        columns.append({'name': _('Balance'), 'class': 'number'})

        return columns



    @api.model
    def _get_query_amls(self, options, expanded_partner=None, offset=None, limit=None):
        ''' Construct a query retrieving the account.move.lines when expanding a report line with or without the load
        more.
        :param options:             The report options.
        :param expanded_partner:    The res.partner record corresponding to the expanded line.
        :param offset:              The offset of the query (used by the load more).
        :param limit:               The limit of the query (used by the load more).
        :return:                    (query, params)
        '''
        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

        # Get sums for the account move lines.
        # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
        if expanded_partner:
            domain = [('partner_id', '=', expanded_partner.id)]
        elif unfold_all:
            domain = []
        elif options['unfolded_lines']:
            domain = [('partner_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]

        new_options = self._get_options_sum_balance(options)
        tables, where_clause, where_params = self._query_get(new_options, domain=domain)
        ct_query = self._get_query_currency_table(options)

        query = '''
            SELECT
                account_move_line.id,
                account_move_line.date,
                account_move_line.date_maturity,
                account_move_line.name,
                account_move_line.building_module_ref,
                account_move_line.ref,
                account_move_line.company_id,
                account_move_line.account_id,             
                account_move_line.payment_id,
                account_move_line.partner_id,
                account_move_line.currency_id,
                account_move_line.amount_currency,
                ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                account_move_line__move_id.name         AS move_name,
                company.currency_id                     AS company_currency_id,
                partner.name                            AS partner_name,
                account_move_line__move_id.type         AS move_type,
                account.code                            AS account_code,
                account.name                            AS account_name,
                journal.code                            AS journal_code,
                journal.name                            AS journal_name,
                full_rec.name                           AS full_rec_name
            FROM account_move_line
            LEFT JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN res_company company               ON company.id = account_move_line.company_id
            LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
            LEFT JOIN account_account account           ON account.id = account_move_line.account_id
            LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
            LEFT JOIN account_full_reconcile full_rec   ON full_rec.id = account_move_line.full_reconcile_id
            WHERE %s
            ORDER BY account_move_line.id
        ''' % (ct_query, where_clause)

        if offset:
            query += ' OFFSET %s '
            where_params.append(offset)
        if limit:
            query += ' LIMIT %s '
            where_params.append(limit)
        return query, where_params



    @api.model
    def _get_report_line_move_line(self, options, partner, aml, cumulated_init_balance, cumulated_balance):
        if aml['payment_id']:
            caret_type = 'account.payment'
        elif aml['move_type'] in ('in_refund', 'in_invoice', 'in_receipt'):
            caret_type = 'account.invoice.in'
        elif aml['move_type'] in ('out_refund', 'out_invoice', 'out_receipt'):
            caret_type = 'account.invoice.out'
        else:
            caret_type = 'account.move'

        date_maturity = aml['date_maturity'] and format_date(self.env, fields.Date.from_string(aml['date_maturity']))
        columns = [
            {'name': aml['journal_code']},
            {'name': aml['building_module_ref']},
            {'name': aml['account_code']},
            {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name'])},
            {'name': date_maturity or '', 'class': 'date'},
            {'name': aml['full_rec_name'] or ''},
            {'name': self.format_value(cumulated_init_balance), 'class': 'number'},
            {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
            {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
        ]
        if self.user_has_groups('base.group_multi_currency'):
            if aml['currency_id']:
                currency = self.env['res.currency'].browse(aml['currency_id'])
                formatted_amount = self.format_value(aml['amount_currency'], currency=currency, blank_if_zero=True)
                columns.append({'name': formatted_amount, 'class': 'number'})
            else:
                columns.append({'name': ''})
        columns.append({'name': self.format_value(cumulated_balance), 'class': 'number'})
        return {
            'id': aml['id'],
            'parent_id': 'partner_%s' % partner.id,
            'name': format_date(self.env, aml['date']),
            'class': 'date',
            'columns': columns,
            'caret_options': caret_type,
            'level': 4,
        }
