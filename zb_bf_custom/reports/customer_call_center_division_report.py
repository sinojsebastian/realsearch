from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from num2words import num2words
import math
from odoo.tools.float_utils import float_round
import time

from datetime import datetime, timedelta, date

from calendar import monthrange

from dateutil.relativedelta import relativedelta

from dateutil.rrule import rrule, MONTHLY
from datetime import datetime,date


from odoo.tools import DEFAULT_SERVER_DATE_FORMAT



import logging
_logger = logging.getLogger(__name__)


class CustomerCallCenterFeedback(models.AbstractModel):

    _name = 'report.zb_bf_custom.helpdesk_feedback_report'
    _description='Customer Call Center Feedback Report'

    

    @api.model
    def _get_report_values(self, docids,data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        result ={}
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id', []))
        
        if data['form']:
        
            from_date = data['form'][0].get('from_date')
            to_date = data['form'][0].get('to_date')
            date_from = datetime.strptime(str(from_date),'%Y-%m-%d').strftime('%B %d,%Y')
            date_to = datetime.strptime(str(to_date),'%Y-%m-%d').strftime('%B %d,%Y')
            
            tickets = self.env['helpdesk.ticket'].search([('complaint_date','<=',to_date),('complaint_date','>=',from_date)])
            call_count = 0
            satisfied_tickets = 0
            incomplete_jobs = 0
            repeated_jobs = 0
            cleanup_jobs = 0
            delayed_jobs = 0
            key = ''
            for record in tickets:
                if record.building_id:
                    key = record.building_id
                    call_count = tickets.filtered(lambda r: r.building_id.id == record.building_id.id and r.call_conducted == True)
                    satisfied_tickets = tickets.filtered(lambda r: r.building_id.id == record.building_id.id and r.ticket == 'satisfactory')
                    incomplete_jobs = tickets.filtered(lambda r: r.building_id.id == record.building_id.id and r.reason == 'not_completed')
                    repeated_jobs = tickets.filtered(lambda r: r.building_id.id == record.building_id.id and r.reason == 'repeated')
                    cleanup_jobs = tickets.filtered(lambda r: r.building_id.id == record.building_id.id and r.reason == 'not_cleaned')
                    delayed_jobs = tickets.filtered(lambda r: r.building_id.id == record.building_id.id and r.reason == 'delayed')
                if key in result:
                    result[key]['calls_conducted'] = len(call_count)
                    result[key]['satisfactory'] = len(satisfied_tickets)
                    result[key]['incomplete_jobs'] = len(incomplete_jobs)
                    result[key]['repeated_jobs'] = len(repeated_jobs)
                    result[key]['cleanup_jobs'] = len(cleanup_jobs)
                    result[key]['delayed_jobs'] = len(delayed_jobs)
                    
                else:
                    result.update({key:{'calls_conducted':len(call_count),
                                        'satisfactory':len(satisfied_tickets),
                                        'incomplete_jobs':len(incomplete_jobs),
                                        'repeated_jobs':len(repeated_jobs),
                                        'cleanup_jobs':len(cleanup_jobs),
                                        'delayed_jobs':len(delayed_jobs)}})
                    
                
            
            
            docargs = {
                       'doc_ids':self._ids,
                       'doc_model': model,
                       'docs': docs,
                       'data': data['form'],
                       'from_date':date_from,
                       'to_date':date_to,
                       'result':result
                       }
            return docargs