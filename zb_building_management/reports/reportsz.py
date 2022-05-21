# Copyright 2014 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
  
import json
from odoo import http
from odoo.addons.web.controllers import main
from odoo.addons.mail.models import mail_template
import calendar
from datetime import datetime,date,timedelta
from odoo.addons.web.controllers.main import ExcelExport
# from odoo.addons.web.controllers import main
import calendar
from odoo.addons.web.controllers import main as report
from odoo.http import route, request

import json


from odoo.addons.web.controllers.main import ReportController





class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'xlsx':
            report = request.env['ir.actions.report']._get_report_from_name(
                reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(',')]
            if data.get('options'):
                data.update(json.loads(data.pop('options')))
            if data.get('context'):
                # Ignore 'lang' here, because the context in data is the one
                # from the webclient *but* if the user explicitely wants to
                # change the lang, this mechanism overwrites it.
                data['context'] = json.loads(data['context'])
                if data['context'].get('lang'):
                    del data['context']['lang']
                context.update(data['context'])
            xlsx = report.with_context(context).render_xlsx(
                docids, data=data
            )[0]
           
            xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    'attachment; filename=' + report.report_file + '.xlsx'
                )
            ]
            datetime.now().month
            if report.report_file == 'Sales_Analysis_Report':
                xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    'attachment; filename=' + report.report_file + ' %s- %s -%s'%(str(calendar.month_name[datetime.now().month]),str(datetime.now().day),str(datetime.now().year))+ '.xlsx'
                )
                 ]
                
            if report.report_file == 'sales_report':
                xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    'attachment; filename=' + report.report_file + ' %s- %s -%s'%(str(calendar.month_name[datetime.now().month]),str(datetime.now().day),str(datetime.now().year))+ '.xlsx'
                )
                 ]
                
            if report.report_file == 'summary_all_assets':
                xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    'attachment; filename=' + report.report_file + ' %s- %s -%s'%(str(calendar.month_name[datetime.now().month]),str(datetime.now().day),str(datetime.now().year))+ '.xlsx'
                )
                 ]
                
            if report.report_file == 'occupancy_summary':
                xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    'attachment; filename=' + report.report_file + ' %s- %s -%s'%(str(calendar.month_name[datetime.now().month]),str(datetime.now().day),str(datetime.now().year))+ '.xlsx'
                )
                 ]
            if report.report_file == 'occupancy_statement':
                xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    'attachment; filename=' + report.report_file + ' %s- %s -%s'%(str(calendar.month_name[datetime.now().month]),str(datetime.now().day),str(datetime.now().year))+ '.xlsx'
                )
                 ] 
            import pprint
            pp = pprint.PrettyPrinter(indent=4)   
            pprint.pprint(report)
            if report.report_file == 'outstanding_statement':
                print (report.id,"report---------",report.report_name,report.model)
                context = dict(http.request.context)
                report_ids = context.get("active_id", None)
                active_id = request.env.context.get('active_id', False)
                print(report_ids,"------------------------",active_id)
                mod = request.env[report.model].browse(report_ids)
                print (mod.date,"mod-----------------")
                xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    'attachment; filename=' + report.report_file + ' %s- %s -%s'%(str(calendar.month_name[datetime.now().month]),str(datetime.now().day),str(datetime.now().year))+ '.xlsx'
                )
                 ]    
            return request.make_response(xlsx, headers=xlsxhttpheaders)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )



