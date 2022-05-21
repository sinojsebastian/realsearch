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
    "name"         : "CRM",
    "version"      : "0.10",
    "author"       : "InforiseIT & ZestyBeanz",
    "website"      : "http://www.zbeanztech.com",
    "description"  : """CRM""",
    "depends"      : ['crm','zb_building_management'],
    "init_xml"     : [],    
    "demo"         : [],
    "data"         : [
                    'wizard/open_unit_wizard.xml',
                    'views/project_view.xml', 
                    'views/building_view.xml',  
                    'views/schedular_reservation.xml',
                    'views/email_temp.xml', 
                    'views/user_groups.xml'

                     ],
    "auto_install" : False,
    "installable"  : True,
    'application'  : True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
