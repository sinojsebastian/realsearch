# -*- coding: utf-8 -*-
##############################################
#
# Inforise IT & ZestyBeanz Technologies Pvt. Ltd
# By Sinoj Sebastian (sinoj@zbeanztech.com, sinoj@inforiseit.com)
# First Version 2020-09-22
# Website1 : http://www.zbeanztech.com
# Website2 : http://www.inforiseit.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################

{
    "name"         : "Building Management",
    "version"      : "0.43",
    "author"       : "InforiseIT & ZestyBeanz",
    "website"      : "http://www.zbeanztech.com",
    "description"  : """Building and rent management""",
    "category"     : "Client Modules/Real Estate",
    "depends"      : ['report_xlsx','account','base','web', "bh_account_vat","bh_sale_vat","bh_address_format","l10n_bh",'analytic','stock','payment','crm'],
    "init_xml"     : [],
    "demo"         : [],
    "data"         : [
                    'security/user_groups.xml',
                    'security/ir.model.access.csv',
                    'wizard/account_voucher.xml',
                    'views/account_invoice.xml',
                    'views/building_view.xml',
                    'reports/rental_analysis_report_view.xml',
                    'wizard/complaints.xml',
                    'views/legal_case.xml',
                    'views/sequence_legal.xml',
#PV                     'views/project_view.xml',
                    'views/xls_reporsts.xml',
                    'views/analytic_account.xml',
                    'views/sequence.xml',
                    'views/user_groups.xml',
                    'views/res_config_view.xml',
                    'views/address_format.xml',
                    'reports/custom_paperformat.xml',
                    'reports/tijaria_report.xml',
                    'wizard/update_customer.xml',
                    'views/invoice_generation_view.xml',
                    'views/schedular_reservation.xml',
                    'views/email_temp.xml',
                    'reports/invoice_report.xml',
                    'reports/paymenr_receipt.xml',
                                      
# 
#                       'views/image_temp.xml',
#                       'views/layout.xml',
#                       'reports/payment_voucher_inherit.xml',                      
#                       'reports/report_invoice_creation.xml',
#                       'reports/new_cus_invoice.xml',
     
                      ],
    "auto_install" : False,
    "installable"  : True,
    'application'  : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
