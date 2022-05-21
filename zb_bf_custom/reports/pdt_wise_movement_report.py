from odoo import models,_
from datetime import datetime, timedelta,date
from odoo.exceptions import AccessError,UserError,Warning

import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


import logging
_logger = logging.getLogger(__name__)



class ProductWiseMovementXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_pdt_wise_movement'
    _description = 'Product Wise Movement Report'
    _inherit = 'report.report_xlsx.abstract'


    
    def generate_xlsx_report(self, workbook, data,wiz):
         
#         periods, product_data = self.get_aging_data(partners)

        worksheet= workbook.add_worksheet('Product Wise Movement Analysis')

        title1 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 16,'border':2,'text_wrap': True})
        title3 = workbook.add_format({'align': 'center', 'valign': 'vcenter',
                                                      'bold': True, 'size': 9,'border':2,'text_wrap': True})
        
        cell_number_format = workbook.add_format({'align': 'right',
                                                  'valign': 'vcenter',
                                                  'bold': False, 'size': 12,
                                                  'num_format': '#,###0.000'})


        style = workbook.add_format({'bold': True,'align': 'center', 'text_wrap': True,'border':1,'valign': 'vcenter','size': 8})
        title2 = workbook.add_format({'bold': True,'align': 'center', 'text_wrap': True,'border':1,'valign': 'vcenter','size': 8})
        
        style2 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})
        style2_wrap = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter','text_wrap': True})
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        from_date = datetime.strptime(str(wiz.from_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        to_date = datetime.strptime(str(wiz.to_date), DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        worksheet.set_row(10, 50)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 13)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.merge_range('E7:H7', 'Product Wise Movement',title1)
        worksheet.write('A11', 'Sr.#', title2)
        worksheet.write('B11', 'Building Name', title2)
        worksheet.write('C11', 'Opening Balance', title2)
        worksheet.write('D11','Invoiced Amount', title2)
        worksheet.write('E11', 'Collected Amount', title2)
        worksheet.write('F11', 'Closing Balance', title2)
        worksheet.write('G11', 'Area Manager', title2)
        
        worksheet.write('A9', 'From Date:', title3)
        worksheet.write('B9', from_date, title2)
        worksheet.write('C9', 'To Date:' , title3)
        worksheet.write('D9', to_date, title2)
        worksheet.write('C10', 'Product:' , title3)
        worksheet.merge_range('D10:E10', wiz.product_id.name, title2)
        company_logo = self.env.user.company_id.logo
        cmpny = self.env.user.company_id
        data = base64.b64decode(company_logo) 
#         im = PILImage.open(BytesIO(data)) 
#         x = im.save('logo.png') 
        if cmpny.name:
            cmpny_name = cmpny.name
        else:
            cmpny_name =''
        if cmpny.street:
            street = cmpny.street
        else:
            street =''
        if cmpny.street2:
            street2 = cmpny.street2
        else:
            street2 =''
        if cmpny.city:
            city = cmpny.city
        else:
            city =''
        if cmpny.country_id.name:
            country_id = cmpny.country_id.name
        else:
            country_id =''
        if cmpny.email:
            email = 'Email:%s'%(cmpny.email)
        else:
            email =''
        worksheet.merge_range('E1:H5','\n %s \n %s  %s \n %s \n %s \n %s'%(cmpny_name,street,street2 ,cmpny.city,country_id,email),title2)
        worksheet.merge_range('A1:B7','')
        worksheet.insert_image('A1:B7','logo.png',{'x_scale': 0.10, 'y_scale': 0.11,'x_offset': 40})
        count = 1
        row = 11
        building_dict ={}
        column = 0
        inv_amount = 0.00
        inv_line_ids = self.env['account.move.line'].search([('product_id','=',wiz.product_id.id),('date','>=',wiz.from_date),('date','<=',wiz.to_date),('move_id.state','=','posted'),('move_id.type','in',['out_invoice','out_refund'])])
        for inv in inv_line_ids:
            building = inv.move_id.building_id.id if inv.move_id.building_id.id else '0000'
            if building in building_dict:
                building_dict[building][0]["inv_amount"] += inv.move_id.amount_total
                building_dict[building][0]["collected_amount"] += inv.move_id.amount_total - inv.move_id.amount_residual
            else:
                building_dict[building] = [{
                    'building':inv.move_id.building_id.name if inv.move_id.building_id.id else '' ,
                    'opening_balance': self.get_opening_balance(wiz.from_date, wiz.to_date, inv),
                    'inv_amount':inv.move_id.amount_total,
                    'collected_amount': inv.move_id.amount_total - inv.move_id.amount_residual,
                    # 'closing_balance':opening_balance + inv_amount - collected_amount,
                    'area_manager':inv.move_id.building_id.area_manager.name if inv.move_id.building_id.area_manager.id else ''
                }]
                
        for build in building_dict:
            worksheet.write(row, column, count, style2)
            worksheet.write(row, column +1, building_dict[build][0]['building'], style2)
            worksheet.write(row, column +2, building_dict[build][0]['opening_balance'] ,cell_number_format)
            worksheet.write(row, column +3, building_dict[build][0]['inv_amount'], cell_number_format)
            worksheet.write(row, column +4, building_dict[build][0]['collected_amount'],cell_number_format)
            worksheet.write(row, column +5, building_dict[build][0]['opening_balance'] + building_dict[build][0]['inv_amount'] - building_dict[build][0]['collected_amount'] , cell_number_format)
            worksheet.write(row, column +6, building_dict[build][0]['area_manager'] , style2)
            row += 1
            count += 1






    def get_opening_balance(self, from_date,to_date, inv):
        '''Function to calculate opening balance'''
        move_line_ids = self.env['account.move.line'].search([('product_id','=',inv.product_id.id),('move_id.building_id','=',inv.move_id.building_id.id),('date','<',from_date),('move_id.state','=','posted')])
        balance = 0.0
        for line in move_line_ids:
            balance += line.move_id.amount_residual
       
        return balance



    # def get_invoice_amount(self, from_date, to_date, inv):

    #     '''Function to calculate opening balance'''
    #     # move_line_search_conditions = """l.account_id = %s and l.product_id = %s
    #     #                                 and m.state in ('posted')
    #     #                               """ % (account_id, product_id)
    #     # if from_date:
    #     #     move_line_search_conditions += "and l.date >= '%s'" % from_date
    #     # if to_date:
    #     #     move_line_search_conditions += "and l.date <= '%s'" % to_date
    #     # move_line_search_conditions += " order by l.debit,l.credit"
    #     # self._cr.execute('select l.id from account_move_line l, \
    #     # account_move m where %s'
    #     #            %move_line_search_conditions)
    #     # line_ids = map(lambda x: x[0], self._cr.fetchall())
    #     move_line_ids = self.env['account.move.line'].search([('product_id','=',inv.product_id.id),('move_id.building_id','=',building_id.id),('date','>=',from_date),('date','<=',to_date),('account_id','=',inv.account_id.id),('move_id.state','=','posted')])
    #     # move_line_ids = self.env['account.move.line'].sudo().browse(line_ids)
    #     debit = credit=0.0
    #     for line in move_line_ids:
    #         # print (line.id,line.credit,line.debit,'ddfff\n')
    #         debit += line.amount_total
    #         credit += line.credit
    #     print (inv.move_id.invoice_payment_state,'inv.move_id.invoice_payment_state',inv.move_id.name)
    #     if inv.move_id.invoice_payment_state== 'paid':
    #         print (inv.move_id.invoice_payments_widget,'>>>>>\n\n\n\n')
    #     vals = ({
    #                  'debit':debit,
    #                  'credit':credit,
    #                  'balance':debit-credit
    #                  })
    #     # print (vals,'sss')
    #     return vals
