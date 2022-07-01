# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Bin Faqeeh Real Estate Investment Company',
    'author': "Zesty Beanz Technologies Pvt LTD",
    'website': "http://www.zbeanztech.com",
    'summary': 'Bin Faqeeh Customization Module',
    'description': """
        Bin Faqeeh Customization



    """,
    'version': '6.56',
    'depends': ['base', 'account', 'snailmail_account', 'bh_account_vat', 'zb_crm_property', 'zb_building_management',
                'purchase', 'crm', 'product','report_xlsx',],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/schedular.xml',
        # 'data/mail_data.xml',
        'reports/reports.xml',
        'reports/resale_report.xml',
        'reports/commission_invoice.xml',
        'reports/commission_invoice.xml',
        'reports/owner_rental_statement_report.xml',
        'wizard/owner_rental_statement.xml',
        'wizard/supplier_wise_statement_report.xml',
        'wizard/tenant_master_report.xml',
        'wizard/tenant_deposit_view.xml',
        'wizard/owner_master_report.xml',
        'wizard/ewa_master_report.xml',
        'wizard/leasing_details_report_wiz.xml',
        'wizard/agreement_wizard.xml',
        'wizard/terminate_agreement_wizard.xml',
        'wizard/service_charge_wizard.xml',
        'wizard/rent_outstanding_report_view.xml',
        'wizard/building_wise_income_statement_wizard.xml',
        'wizard/service_charge_outstanding_wiz.xml',
        'wizard/buildingwise_internet_wizard.xml',
        'wizard/ewa_excess_tenantwise_wiz.xml',
        'wizard/collection_report_wizard.xml',
        'wizard/import_account.xml',
        'wizard/ewa_common_area_wiz.xml',
        'wizard/wiz_building_wise_ewa_account.xml',
        'wizard/contract_commission_deduction_wizard.xml',
        'wizard/customer_call_center_report_wiz.xml',
        'wizard/product_wise_movement_wiz.xml',
        'wizard/ewa_internet_inv_report.xml',
        'wizard/building_wise_owner_outstanding_wizard.xml',
        'wizard/owner_rental_statement_report_wizard.xml',
        'wizard/wiz_project_wise_income_stmnt.xml',
        'wizard/service_charge_report_wiz.xml',
        'wizard/wizard_import_data.xml',
        'wizard/resale_report_wizard.xml',
        'wizard/create_jv_import_wizard_view.xml',
        'wizard/helpdesk_feedback_wiz_view.xml',
        'wizard/bf_rental_report.xml',
        'wizard/tax_adjustment_wizard.xml',
	'wizard/payment_adjustment_import.xml',
        'reports/receipt_voucher_report.xml',
        'reports/rent_invoice_report.xml',
        'reports/payment_advice_report.xml',
        'reports/tax_invoice_report.xml',
        'reports/debit_note_report.xml',
        'reports/payment_voucher_report.xml',
        'reports/rent_agreement_report.xml',
        'reports/ewa_batelco_internet_qweb.xml',
        'reports/report_owner_rental_statement.xml',
        'reports/rental_agreement_sheet_report.xml',
        'reports/non_managed_lease_agreement.xml',
        'reports/renewal_agreement_report.xml',
        'reports/customer_call_center_division_report.xml',
        'reports/management_contract_report.xml',
        'reports/management_fee_invoice_report.xml',
        'reports/purchase_quotation_report.xml',
        'reports/purchase_order_report..xml',
        'reports/report_layout.xml',
        'reports/tenant_deposit_invoice_report.xml',
        'views/product_view.xml',
        'views/res_partner_views.xml',
        'views/units_views.xml',
        'views/title_deed_views.xml',
        'views/other_features_views.xml',
        'views/purchase_order.xml',
        'views/view_unit_views.xml',
        'views/crm_lead.xml',
        'views/account_view.xml',
        'views/activity_view.xml',
        'views/services_view.xml',
        'views/res_config_settings_views.xml',
        'views/building_portal_templates.xml',
        'views/helpdesk_ticket.xml',
        'views/sale_view.xml',
        'views/bank_reconciliation.xml',
        'views/search_template_view.xml',
        'wizard/import_account_balance_view.xml',
        'views/assets.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
