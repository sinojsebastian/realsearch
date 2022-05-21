from odoo import models
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
import base64 
from io import BytesIO 
from PIL import Image as PILImage
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import xlsxwriter

class CallCenterReportXlsx(models.AbstractModel):
    _name = 'report.zb_bf_custom.report_call_center'
    _description = 'Customer Call Center Division Report'
    _inherit = 'report.report_xlsx.abstract'
    
    
        
    
    def generate_xlsx_report(self, workbook, data, wiz):
        
        worksheet= workbook.add_worksheet('Customer Call Center Division Report')
        style1 = workbook.add_format({'size': 10,'bold': True,'align': 'center', 'valign': 'vcenter'})
        # date_format = workbook.add_format({'num_format': 'dd/mm/yyyy','size': 10,'align': 'center', 'valign': 'vcenter'})
        style = workbook.add_format({'align': 'center', 'valign': 'vcenter','size': 10,'bold':True,'border':1})
        float_style = workbook.add_format({'align': 'right', 'valign': 'vcenter','size': 10})
        heading_format = workbook.add_format({'align': 'center','valign': 'vcenter','bold': True,'size': 14,})
        address_format = workbook.add_format({'align': 'left','valign': 'vcenter','bold': True,'size': 10,'text_wrap': True})
        wrap = workbook.add_format({'size': 10,'bold': True,'align': 'left'})
        wrap.set_text_wrap()   
        style3 = workbook.add_format({'size': 10,'align': 'center', 'valign': 'vcenter'})                            
        
#         worksheet.set_row(0, 50)
        worksheet.set_row(4, 20)
        worksheet.set_row(9, 30)
        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 17)
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:D', 16)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        
        worksheet.merge_range('C6:F6', 'Customer Call Center Division Report', heading_format)
        worksheet.write('A10:A10','', style)
        worksheet.merge_range('B10:D10','Total Maintenance Complaints',style)
        worksheet.merge_range('E10:K10','Maintenance Compaints Types',style)


        worksheet.write('A8', 'From Date:',style1)
        worksheet.write('D8', 'To Date:',style1)
        worksheet.write('A11', 'Location',style1)
        worksheet.write('B11', 'Total Received',style1)
        worksheet.write('C11', 'Total Completed',style1)
        worksheet.write('D11', 'Total Pending',style1)
#         worksheet.write('E11', 'AC',style1)
#         worksheet.write('F11', 'Plumbing',style1)
#         worksheet.write('G11', 'Electrical',style1)
#         worksheet.write('H11', 'Paint',style1)
#         worksheet.write('I11', 'Masionary',style1)
#         worksheet.write('J11', 'Carpentry',style1)
#         worksheet.write('K11', 'TV',style1)
        
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
        from_date = datetime.strptime(str(wiz.from_date),DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%b/%Y')
        to_date = datetime.strptime(str(wiz.to_date),DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%b/%Y')
        worksheet.write('B8',from_date,style1)
        worksheet.write('E8',to_date, style1)
        
        ticket_ids = self.env['helpdesk.ticket'].search([('complaint_date','>=',from_date),('complaint_date','<=',to_date)])
        question_ticket_ids = self.env.ref('helpdesk.type_question')
        
        issue_ticket_ids = self.env.ref('helpdesk.type_incident')
        
        ticket_type_list = []
        if question_ticket_ids or issue_ticket_ids:
            ticket_type = self.env['helpdesk.ticket.type'].search([('id','!=',question_ticket_ids.id),('id','!=',issue_ticket_ids.id)])
        else:
            ticket_type = self.env['helpdesk.ticket.type'].search([])
        
        for type in ticket_type:
            ticket_type_list.append(type)
        
        #Call Center Functionalities
        closed_pending_dict = {}
        building_ticket_dict = {}
        count = 0
        count1 = 0
        for ticket in ticket_ids:
            
            pending_tickets = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.stage_id.is_close == False)
            closed_tickets = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.stage_id.is_close == True)
            ticket_dict_key = ticket.building_id
            
            if ticket_dict_key in closed_pending_dict:
                    closed_pending_dict[ticket_dict_key]['closed_tickets'] = len(closed_tickets)
                    closed_pending_dict[ticket_dict_key]['pending_ticket'] = len(pending_tickets)
            else:
                closed_pending_dict.update({ticket_dict_key:{'closed_tickets' : len(closed_tickets),
                                                             'pending_ticket': len(pending_tickets),
                                                        }})
            
            for typess in ticket_type:
     
                ticket_type_key = typess
                
                ticket_types = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.ticket_type_id.id == typess.id)
                if ticket_dict_key in building_ticket_dict:
                    building_ticket_dict[ticket_dict_key][ticket_type_key] = len(ticket_types)
                else:
                    building_ticket_dict.update({ticket_dict_key:{
                                                            ticket_type_key:len(ticket_types)}})
                    


        key_list = []
        row = 12
        column=0
              
        for key,values in building_ticket_dict.items():
            key_list.append(key)
            worksheet.write(row,column,key.name,style3)
            row+=1
            
        worksheet.write(row,0,'Total',style3)
        
        row = 10
        column=4
            
        for item in ticket_type_list:
            type_count = 0
            worksheet.write(row,column,item.name,style1)
            
            for keys,values in building_ticket_dict.items():
                type_count += values[item]
            worksheet.write(row+len(key_list)+2,column,type_count,style3)
            column+=1
        worksheet.merge_range(9, 4, 9, column-1, 'Maintenance Compaints Types', style)
#         worksheet.write(row,column,'',style1)
        
        row = 12
        column=4
        
        for key1,value1 in building_ticket_dict.items():
            received_count = 0
            for vals in value1.items():
                received_count += vals[1]
                worksheet.write(row,column,vals[1],style3)
                column+=1
                
            column=4
            worksheet.write(row,1,received_count,style3)
            row+=1
            
        worksheet.write_formula(row,1,'{=SUM(B%s:B%s)}'%(13,row),style3)
        
        
        row = 12
        column=2
        for key2,value2 in closed_pending_dict.items():
            for vals in value2.items():
                worksheet.write(row,column,vals[1],style3)
                column+=1
            row+=1
            column=2
        
        worksheet.write_formula(row,2,'{=SUM(C%s:C%s)}'%(13,row),style3)
        worksheet.write_formula(row,3,'{=SUM(D%s:D%s)}'%(13,row),style3)















#             ac_ticket_ids = self.env.ref('zb_bf_helpdesk.ticket_type_ac')
#             plumbing_ids = self.env.ref('zb_bf_helpdesk.ticket_type_plumbing')
#             electrical_ids = self.env.ref('zb_bf_helpdesk.ticket_type_electrical')
#             paint_ids = self.env.ref('zb_bf_helpdesk.ticket_type_paint')
#             masionary_ids = self.env.ref('zb_bf_helpdesk.ticket_type_masionary')
#             carpentry_ids = self.env.ref('zb_bf_helpdesk.ticket_type_carpentry')
#             tv_ids = self.env.ref('zb_bf_helpdesk.ticket_type_tv')
            
#             pending_tickets = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.stage_id.is_close == False)
#             closed_tickets = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.stage_id.is_close == True)
#             print('=================closed_tickets======================',closed_tickets)
            
#             ac_ticket = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.ticket_type_id.id == ac_ticket_ids.id)
#             plumbing_ticket = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.ticket_type_id.id == plumbing_ids.id)
#             electrical_ticket = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.ticket_type_id.id == electrical_ids.id)
#             paint_ticket = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.ticket_type_id.id == paint_ids.id)
#             masionary_ticket = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.ticket_type_id.id == masionary_ids.id)
#             carpentry_ticket = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.ticket_type_id.id == carpentry_ids.id)
#             tv_ticket = ticket_ids.filtered(lambda r: r.building_id.id == ticket.building_id.id and r.ticket_type_id.id == tv_ids.id)
            
#             if ticket_dict_key in building_ticket_dict:
#                 if ticket_type_key in building_ticket_dict[ticket_dict_key]:
#                     count = count+1
#                     print('=================iff-1======================',count)
#                     building_ticket_dict[ticket_dict_key][ticket_type_key].update({'count':count})
#                 else:
#                     count = 0
#                     count = count+1
#                     print('=================else-1======================',count)
#                     building_ticket_dict[ticket_dict_key][ticket_type_key] = {'count':count}
#             else:
#                 count = 0
#                 count = count+1
#                 print('=================else-2======================',count)
#                 building_ticket_dict[ticket_dict_key] = {ticket_type_key:{'count':count}}
#             print('====================building_ticket_dict======================',building_ticket_dict)
                    
                
#                 building_ticket_dict[ticket_dict_key]['closed_tickets'] = len(closed_tickets)
#                 building_ticket_dict[ticket_dict_key]['pending_ticket'] = len(pending_tickets)
#                 building_ticket_dict[ticket_dict_key][''] = len(ac_ticket)
#                 building_ticket_dict[ticket_dict_key]['plumbing_ticket'] = len(plumbing_ticket)
#                 building_ticket_dict[ticket_dict_key]['electrical_ticket'] = len(electrical_ticket)
#                 building_ticket_dict[ticket_dict_key]['paint_ticket'] = len(paint_ticket)
#                 building_ticket_dict[ticket_dict_key]['masionary_ticket'] = len(masionary_ticket)
#                 building_ticket_dict[ticket_dict_key]['carpentry_ticket'] = len(carpentry_ticket)
#                 building_ticket_dict[ticket_dict_key]['tv_ticket'] = len(tv_ticket)
#             else:
#                 
#                 building_ticket_dict.update({ticket_dict_key:{'closed_tickets':len(closed_tickets),
#                                                             'pending_ticket':len(pending_tickets),
#                                                             'ac_ticket':len(ac_ticket),
#                                                               'plumbing_ticket':len(plumbing_ticket),
#                                                               'electrical_ticket':len(electrical_ticket),
#                                                               'paint_ticket':len(paint_ticket),
#                                                               'masionary_ticket':len(masionary_ticket),
#                                                               'carpentry_ticket':len(carpentry_ticket),
#                                                               'tv_ticket':len(tv_ticket)}})
                
        
#         row = 11
#         column=4
#         for type in ticket_type:
#             worksheet.write(row,column, type.name,style1)
#             column+=1
#             worksheet.write('F11', 'Plumbing',style1)
#             worksheet.write('G11', 'Electrical',style1)
#             worksheet.write('H11', 'Paint',style1)
#             worksheet.write('I11', 'Masionary',style1)
#             worksheet.write('J11', 'Carpentry',style1)
#             worksheet.write('K11', 'TV',style1)
        
        
        
#         row = 12
#         column=0
#              
#         for key,values in building_ticket_dict.items():
#             print('==================key=====================',key)
#             print('==================values=====================',values)
#              
#             worksheet.write(row,column,key.name,style3)
#             worksheet.write_formula(row,column+1,'{=SUM(E%s:K%s)}'%(row+1,row+1),style3)
#             worksheet.write(row,column+2,values['closed_tickets'],style3)
#             worksheet.write(row,column+3,values['pending_ticket'],style3)
#             worksheet.write(row,column+4,values['ac_ticket'],style3)
#             worksheet.write(row,column+5,values['plumbing_ticket'],style3)
#             worksheet.write(row,column+6,values['electrical_ticket'],style3)
#             worksheet.write(row,column+7,values['paint_ticket'],style3)
#             worksheet.write(row,column+8,values['masionary_ticket'],style3)
#             worksheet.write(row,column+9,values['carpentry_ticket'],style3)
#             worksheet.write(row,column+10,values['tv_ticket'],style3)
#             
#             row+=1
#         worksheet.write(row,0,'Total',style3)
#         worksheet.write_formula(row,1,'{=SUM(B%s:B%s)}'%(13,row),style3)
#         worksheet.write_formula(row,2,'{=SUM(C%s:C%s)}'%(13,row),style3)
#         worksheet.write_formula(row,3,'{=SUM(D%s:D%s)}'%(13,row),style3)
#         worksheet.write_formula(row,4,'{=SUM(E%s:E%s)}'%(13,row),style3)
#         worksheet.write_formula(row,5,'{=SUM(F%s:F%s)}'%(13,row),style3)
#         worksheet.write_formula(row,6,'{=SUM(G%s:G%s)}'%(13,row),style3)
#         worksheet.write_formula(row,7,'{=SUM(H%s:H%s)}'%(13,row),style3)
#         worksheet.write_formula(row,8,'{=SUM(I%s:I%s)}'%(13,row),style3)
#         worksheet.write_formula(row,9,'{=SUM(J%s:J%s)}'%(13,row),style3)
#         worksheet.write_formula(row,10,'{=SUM(K%s:K%s)}'%(13,row),style3)


        
        
        

            
        
            
            
        
        
        
        
        
        
        
        














#         worksheet.write(row,0,count or '',style)
#         worksheet.write(row,1,building_obj.name or '',style)
# #         worksheet.write(row,2,area or '',style)
# #         worksheet.write(row,3,v['account_no'] or '',style)
# #         worksheet.write(row,4,'%.3f' %v['current_period_amt'] or 0.000,float_style)
# #         worksheet.write(row,5,'%.3f' %v['prevoius_month_cy'] or 0.000,float_style)
# #         worksheet.write(row,6,'%.3f' %v['previous_year'] or 0.000,float_style)
# #         worksheet.write(row,7,'%.3f' %varience or 0.000,float_style)
# #         worksheet.write(row,8,'%.2f' %varience_percent or 0.00,float_style)
#         row=row+1
#         count=count+1
        
        
        