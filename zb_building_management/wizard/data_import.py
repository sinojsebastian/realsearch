# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import csv
import base64
from io import StringIO
import xlrd
from io import BytesIO
from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo import tools as openerp_tools
import os
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class data_import_wizard(models.TransientModel):
    _name = 'data_import.wizard'
    
    def get_data_from_attchment(self, binary_file, file_name):
        list_raw = []
        if '.csv' in file_name:
            response =(base64.b64decode(binary_file))
            res = str(response,'utf-8')
           
            for raw_data in csv.DictReader(StringIO(res),delimiter=',', quotechar='"'):
                list_raw.append(raw_data)
        if '.xls' in file_name or '.xlsx' in file_name:   
            path = openerp_tools.config['addons_path'].split(",")[-1]
            if '.xls' in file_name:
                fullpath = os.path.join(path, 'emp_attendance.xls')
            if '.xlsx' in file_name:
                fullpath = os.path.join(path, 'emp_attendance.xlsx')
            with open(fullpath, 'w') as f:
                f.write(base64.decodestring(binary_file))
            rb = xlrd.open_workbook(fullpath)
            sheet = rb.sheet_by_index(0)
            headers = []
            for rownum in range(sheet.nrows):
              row = sheet.row_values(rownum)
              if headers:
                  raw_data = {}
                  cell_count = -1
                  for cell in row:
                      cell_count = cell_count + 1
                      raw_data.update({headers[cell_count] : cell})
                  list_raw.append(raw_data)    
              if not headers:
                  headers = row
        return list_raw
                
    
data_import_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: