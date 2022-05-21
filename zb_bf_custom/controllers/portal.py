# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii
from datetime import date

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression



class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        partner = request.env.user.partner_id

        UnitModule = request.env['zbbm.module']
        units_count = UnitModule.search_count([
            ('owner_id', '=', partner.id),
            ('state', 'in', ['new', 'available','occupied'])
        ])
        AgreementModel = request.env['zbbm.module.lease.rent.agreement']
        agreement_count = AgreementModel.search_count([
            ('tenant_id', '=', partner.id),
            ('state', 'in', ['draft', 'active','expired'])
        ])

        values.update({
            'units_count': units_count,
            'agreement_count': agreement_count,
        })
        return values



    @http.route(['/my/units', '/my/units/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_units(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        UnitModule = request.env['zbbm.module']

        domain = [
            ('owner_id', '=', partner.id),
            ('state', 'in', ['new', 'available','occupied'])
        ]

        searchbar_sortings = {
            'monthly_rate': {'label': _('Monthly Rent'), 'order': 'monthly_rate desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'stage': {'label': _('Status'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('zbbm.module', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        units_count = UnitModule.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/units",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=units_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        units = UnitModule.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_units_history'] = units.ids[:100]

        values.update({
            'date': date_begin,
            'units': units.sudo(),
            'page_name': 'unit',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/units',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("zb_bf_custom.portal_my_units", values)


    @http.route(['/my/units/<int:unit_id>'], type='http', auth="public", website=True)
    def portal_unit_page(self, unit_id, report_type=None, access_token=None, message=False, **kw):
        try:
            unit_sudo = self._document_check_access('zbbm.module', unit_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=unit_sudo, report_type=report_type, report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if unit_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_unit%s' % unit_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_unit%s' % unit_sudo.id] = now
                body = _('Units viewed by customer %s') % unit_sudo.owner_id.name
                _message_post_helper(
                    "zbbm.module",
                    unit_sudo.id,
                    body,
                    token=unit_sudo.access_token,
                    message_type="notification",
                    subtype="mail.mt_note",
                    partner_ids=unit_sudo.user_id.sudo().partner_id.id
                )

        values = {
            'unit_details': unit_sudo,
            'message': message,
            'token': access_token,
            # 'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': unit_sudo.owner_id.id,
            'report_type': 'html',
            # 'action': unit_sudo._get_portal_return_action(),
        }
        # if unit_sudo.company_id:
        #     values['res_company'] = order_sudo.company_id

        # if order_sudo.has_to_be_paid():
        #     domain = expression.AND([
        #         ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order_sudo.company_id.id)],
        #         ['|', ('country_ids', '=', False), ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
        #     ])
        #     acquirers = request.env['payment.acquirer'].sudo().search(domain)

        #     values['acquirers'] = acquirers.filtered(lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
        #                                              (acq.payment_flow == 's2s' and acq.registration_view_template_id))
        #     values['pms'] = request.env['payment.token'].search([('partner_id', '=', order_sudo.partner_id.id)])
        #     values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order_sudo.amount_total, order_sudo.currency_id, order_sudo.partner_id.country_id.id)

        # if order_sudo.state in ('draft', 'sent', 'cancel'):
        #     history = request.session.get('my_quotations_history', [])
        # else:
        #     history = request.session.get('my_orders_history', [])
        # values.update(get_records_pager(history, unit_sudo))
        return request.render('zb_bf_custom.units_portal_template', values)



    @http.route(['/my/agreements', '/my/agreements/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_agreements(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AgreementModule = request.env['zbbm.module.lease.rent.agreement']

        domain = [
            ('tenant_id', '=', partner.id),
            ('state', 'in', ['draft', 'active','expired'])
        ]

        searchbar_sortings = {
            'reference_no': {'label': _('Reference'), 'order': 'reference_no'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'reference_no'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('zbbm.module.lease.rent.agreement', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        agreement_count = AgreementModule.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/agreements",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=agreement_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        agreements = AgreementModule.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_agreements_history'] = agreements.ids[:100]

        values.update({
            'date': date_begin,
            'agreements': agreements.sudo(),
            'page_name': 'agreement',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/agreements',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("zb_bf_custom.portal_my_agreements", values)


    @http.route(['/my/agreements/<int:agreement_id>'], type='http', auth="public", website=True)
    def portal_agreement_page(self, agreement_id, report_type=None, access_token=None, message=False, **kw):
        try:
            agreement_sudo = self._document_check_access('zbbm.module.lease.rent.agreement', agreement_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=unit_sudo, report_type=report_type, report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if agreement_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_agreement%s' % agreement_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_agreement%s' % agreement_sudo.id] = now
                body = _('Agreement viewed by customer %s') % agreement_sudo.tenant_id.name
                _message_post_helper(
                    "zbbm.module.lease.rent.agreement",
                    agreement_sudo.id,
                    body,
                    token=agreement_sudo.access_token,
                    message_type="notification",
                    subtype="mail.mt_note",
                    partner_ids=agreement_sudo.user_id.sudo().partner_id.id
                )

        values = {
            'agreement_details': agreement_sudo,
            'message': message,
            'token': access_token,
            # 'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': agreement_sudo.tenant_id.id,
            'report_type': 'html',
            # 'action': unit_sudo._get_portal_return_action(),
        }
        # if unit_sudo.company_id:
        #     values['res_company'] = order_sudo.company_id

        # if order_sudo.has_to_be_paid():
        #     domain = expression.AND([
        #         ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order_sudo.company_id.id)],
        #         ['|', ('country_ids', '=', False), ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
        #     ])
        #     acquirers = request.env['payment.acquirer'].sudo().search(domain)

        #     values['acquirers'] = acquirers.filtered(lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
        #                                              (acq.payment_flow == 's2s' and acq.registration_view_template_id))
        #     values['pms'] = request.env['payment.token'].search([('partner_id', '=', order_sudo.partner_id.id)])
        #     values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order_sudo.amount_total, order_sudo.currency_id, order_sudo.partner_id.country_id.id)

        # if order_sudo.state in ('draft', 'sent', 'cancel'):
        #     history = request.session.get('my_quotations_history', [])
        # else:
        #     history = request.session.get('my_orders_history', [])
        # values.update(get_records_pager(history, unit_sudo))
        return request.render('zb_bf_custom.agreements_portal_template', values)
