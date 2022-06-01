# -*- coding: utf-8 -*-
##############################################
#
# Inforise IT & ZestyBeanz Technologies Pvt. Ltd
# By Dianne Jose(dianne@zbeanztech.com, dianne@inforiseit.com)
# First Version 2019-04-03

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
    "name"         : "Bank Reconcilation",
    "version"      : "13.0.6",
    "author"       : "ZestyBeanz Technology Solution",
    "website"      : "http://www.zbeanztech.com",
    "description"  : """ZestyBeanz Bank reconcilation odoo version 13""",
    "depends"      : ['account','report_xlsx'],
    "init_xml"     : [],
    "demo"         : [],
    "data"         : [
                    'security/ir.model.access.csv',
                    'security/user_group.xml',
                    'views/bank_reconcilation_view.xml',
                    'views/account_move_view.xml',
                    'views/sequence.xml',
                    'report/report.xml'
                    
                   
                      ],
    "auto_install" : False,
    "installable"  : True,
    'application'  : True
}
