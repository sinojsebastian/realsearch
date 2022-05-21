from odoo import models
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.exceptions import UserError,Warning
import xlsxwriter
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class EwaCaReportXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_ewa_ca'
    _description = 'EWA Common Area Report'
    _inherit = 'report.report_xlsx.abstract'
    
    def get_building_ewa(self, lines, type, final_data):
        '''
            Getting structure Building wise EWA Amount.
        '''
        current_period_amt=0
        prevoius_month_cy=0
        previous_year = 0
        for line in lines:
            if final_data.get((line[0],line[2])):
                if type == 'current':
                    final_data[(line[0],line[2])]['current_period_amt'] += line[1]
                elif type == 'prevoius_month_cy':
                    final_data[(line[0],line[2])]['prevoius_month_cy'] += line[1]
                elif type == 'previous_year':
                    final_data[(line[0],line[2])]['previous_year'] += line[1]
            else:
                if type == 'current':
                   current_period_amt = line[1]
                elif type == 'prevoius_month_cy':
                    prevoius_month_cy = line[1]
                elif type == 'previous_year':
                    previous_year = line[1]
                final_data.update({(line[0],line[2]):{
                                            'current_period_amt':current_period_amt,
                                            'account_no' :line[2],
                                            'prevoius_month_cy':prevoius_month_cy,
                                            'previous_year':previous_year
                                            }})
        return final_data
    
        
    
    def generate_xlsx_report(self, workbook, data, wiz):
        
        worksheet= workbook.add_worksheet('EWA Common Area Report')
        style1 = workbook.add_format({'size': 10,'bold': True,'align': '    '})
        # date_format = workbook.add_format({'num_format': 'dd/mm/yyyy','size': 10,'align': 'center', 'valign': 'vcenter'})
        style = workbook.add_format({'align': 'center', 'valign': 'vcenter','size': 10})
        float_style = workbook.add_format({'align': 'right', 'valign': 'vcenter','size': 10})
        heading_format = workbook.add_format({'align': 'center','valign': 'vcenter','bold': True,'size': 14,})
        address_format = workbook.add_format({'align': 'left','valign': 'vcenter','bold': True,'size': 10,'text_wrap': True})
        wrap = workbook.add_format({'size': 10,'bold': True,'align': 'left'})
        wrap.set_text_wrap()                               
        
#         worksheet.set_row(0, 50)
        worksheet.set_row(4, 20)
        worksheet.set_row(9, 30)
        worksheet.set_row(12, 35)
        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 17)
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:D', 16)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        
        worksheet.merge_range('A6:H6', 'EWA Common Area Report', heading_format)
        worksheet.write('A8', 'From Date:',style1)
        worksheet.write('D8', 'To Date:',style1)
        worksheet.write('A13', 'Sr.#',style1)
        worksheet.write('B13', 'Building',style1)
        worksheet.write('C13', 'Area',style1)
        worksheet.write('H13', 'Variance',wrap)
        worksheet.write('I13', 'Variance %',wrap)
        
        lang_code = self.env.user.lang
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        
        company = self.env.user.company_id
        logo = False
        if self.env.user.company_id.logo:
            logo = BytesIO(base64.b64decode(self.env.user.company_id.logo or False))

        if company.name:
          company_name = company.name
        else:
          company_name =''
        if company.street:
          street = company.street
        else:
          street =''
        if company.street2:
          street2 = company.street2
        else:
          street2 =''
        if company.city:
          city = company.city
        else:
          city =''
        if company.country_id.name:
          country_id = company.country_id.name
        else:
          country_id =''
          
        #Company Details     
        worksheet.merge_range('C1:D5','%s \n %s \n %s \n %s \n %s'%(company_name,street,street2 ,city,country_id),address_format)
        worksheet.insert_image('A1:A4','picture.png', {'image_data': logo,'x_offset': 0,'x_scale': 0.13, 'y_scale': 0.13})

        #Date details
        from_date = datetime.strptime(str(wiz.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        to_date = datetime.strptime(str(wiz.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        worksheet.write('B8',from_date,style1)
        worksheet.write('E8',to_date, style1)
        
        #Prevoius Month Selected year
        fdate = datetime.strptime(str(wiz.from_date),'%Y-%m-%d')
        tdate = datetime.strptime(str(wiz.to_date),'%Y-%m-%d')
        prev_month_tdate = fdate - timedelta(days=1)
        prev_month_fdate = prev_month_tdate.replace(day=1)
        
        #Prevoius Month Previous year
        prevois_year_fdate = fdate.replace(year=int(wiz.year)-1)
        prevois_year_tdate = tdate.replace(year=int(wiz.year)-1)
        
        #Date formatting
        prev_month_tdate = datetime.strptime(str(prev_month_tdate),'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        prev_month_fdate = datetime.strptime(str(prev_month_fdate),'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        prevois_year_fdate = datetime.strptime(str(prevois_year_fdate),'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        prevois_year_tdate = datetime.strptime(str(prevois_year_tdate),'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        
        worksheet.write('D13', 'EWA Account No',style1)
        worksheet.write('E13', fdate.strftime('%B %Y'),style1)
        worksheet.write('F13', datetime.strptime(str(prev_month_tdate),'%Y-%m-%d').strftime('%B %Y'),wrap)
        worksheet.write('G13', datetime.strptime(str(prevois_year_fdate),'%Y-%m-%d').strftime('%B %Y'),wrap)
        
        params = self.env['ir.config_parameter'].sudo() 
        common_service_product_id = params.get_param('zb_bf_custom.common_service_product_id') or False
#         product = self.env['product.product'].search([('id','=',ewa_product_id)])
        
        if not common_service_product_id:
            raise Warning(_("""Please configure Common Service Product in the Building Settings"""))
        
        row=14
        count=1
        final_data = {}
        area =''
        #Selected year and Month EWA data
        self._cr.execute("""select rs.building_id,sum(amount),rs.account_no from raw_services rs  where rs.module_id is null and rs.product_id=%s and rs.service_date>='%s' and rs.service_date<='%s' GROUP BY rs.building_id,rs.account_no"""%(str(int(common_service_product_id)),str(wiz.from_date),str(wiz.to_date)))
        building_service_line_ids = self._cr.fetchall()
        final_data = self.get_building_ewa(building_service_line_ids,'current',final_data)
        
         #Previous Month  Current year EWA data
        self._cr.execute("""select rs.building_id,sum(amount),rs.account_no from raw_services rs  where rs.module_id is null and rs.product_id=%s and rs.service_date >='%s' and rs.service_date <='%s' GROUP BY rs.building_id,rs.account_no"""%(str(int(common_service_product_id)),str(prev_month_fdate),str(prev_month_tdate)))
        prevoius_mnth_service_line_ids = self._cr.fetchall()
        final_data = self.get_building_ewa(prevoius_mnth_service_line_ids,'prevoius_month_cy',final_data)
        
        #Previous Year  Selected Month EWA data
        self._cr.execute("""select rs.building_id,sum(amount),rs.account_no from raw_services rs  where rs.module_id is null and rs.product_id=%s and rs.service_date >='%s' and rs.service_date <='%s' GROUP BY rs.building_id,rs.account_no"""%(str(int(common_service_product_id)),str(prevois_year_fdate),str(prevois_year_tdate)))
        prevoius_year_service_line_ids = self._cr.fetchall()
        final_data = self.get_building_ewa(prevoius_year_service_line_ids,'previous_year', final_data)
        for k,v in final_data.items():
            area = ''
            building_obj = self.env['zbbm.building'].browse(k[0])
            service_config_ids = self.env['zbbm.services'].search([('account_no','=',v['account_no']),('building_id','=',building_obj.id),('product_id','=',int(common_service_product_id))])
            if len(service_config_ids) > 0:
               area = service_config_ids[0].area
            varience = v['current_period_amt'] - v['prevoius_month_cy'] 
            varience_percent = 0
            if v['prevoius_month_cy'] > 0:
                varience_percent = (varience/v['prevoius_month_cy'])
                
            worksheet.write(row,0,count or '',style)
            worksheet.write(row,1,building_obj.name or '',style)
            worksheet.write(row,2,area or '',style)
            worksheet.write(row,3,v['account_no'] or '',style)
            worksheet.write(row,4,'%.3f' %v['current_period_amt'] or 0.000,float_style)
            worksheet.write(row,5,'%.3f' %v['prevoius_month_cy'] or 0.000,float_style)
            worksheet.write(row,6,'%.3f' %v['previous_year'] or 0.000,float_style)
            worksheet.write(row,7,'%.3f' %varience or 0.000,float_style)
            worksheet.write(row,8,'%.2f' %varience_percent or 0.00,float_style)
            row=row+1
            count=count+1
        
        
        