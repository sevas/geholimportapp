# -*- coding: utf-8 -*-
__author__ = 'sevas'

import os
import urlparse
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api.urlfetch import DownloadError
from status import is_status_down, get_last_status_update
from utils import render_deadline_exceeded_page
from geholwrapper import get_professor_q1_calendar, get_professor_q2_calendar
from geholwrapper import convert_professor_calendar_to_ical_string, make_professor_gehol_url
from gehol.utils import convert_weekspan_to_dates
import conf
import version

def is_staff_member_id_valid(staff_member_id):
    return staff_member_id.isdigit()



def render_professor_notfound_page(request_handler, resource_type):
    template_values = {'gehol_is_down': is_status_down(),
                       'last_status_update': get_last_status_update(),
                       'resource_type':resource_type,
                       'version':version.VERSION
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/professor_notfound.html')
    request_handler.response.out.write(template.render(path, template_values))




def render_gehol_down(renderer, reason):
    template_values = {'gehol_is_down': True,
                       'last_status_update': get_last_status_update(),
                       'request':reason,
                       'version':version.VERSION
                       }
    path = os.path.join(os.path.dirname(__file__), 'templates/gehol_down.html')
    renderer.response.out.write(template.render(path, template_values))


class ProfessorSummary(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        staff_member_id = parsed.path.split("/")[2]

        if is_status_down():
            render_gehol_down(self, "You asked the schedule for a particular student profile.")
        else:
            if is_staff_member_id_valid(staff_member_id):
                logging.debug("staff member '%s' id is valid" % staff_member_id)
                try:
                    cal = get_professor_q1_calendar(staff_member_id)
                except DownloadError,e:
                    logging.error("Could not fetch page before deadline")
                    render_deadline_exceeded_page(self)
                    return
                if cal:
                    self._render_calendar_summary(cal, staff_member_id)
                else:
                    logging.debug("did not receive a calendar")
                    self._render_not_found_page()
            else:
                logging.debug("staff member id '%s' is not valid" % staff_member_id)
                self._render_not_found_page()


    def _render_calendar_summary(self, cal, staff_member_id):
        logging.info("got a calendar from staff member id: %s" % staff_member_id)
        
        professor_name = cal.header_data['teacher_name']

        ical_urls = ["/staff/ical/%s/%s.ics" % (q, staff_member_id) for q in ("q1", "q2")]
        ical_url_titles = ["ULB - %s -  %s" % (q, professor_name) for q in ("Q1", "Q2")]

        q1_span = convert_weekspan_to_dates(conf.Q1_WEEKSPAN, conf.FIRST_MONDAY)
        q2_span = convert_weekspan_to_dates(conf.Q2_WEEKSPAN, conf.FIRST_MONDAY)

        template_values = {'gehol_is_down': is_status_down(),
                         'last_status_update': get_last_status_update(),
                         'version':version.VERSION,
                         'gehol_url':make_professor_gehol_url(staff_member_id, conf.Q1_WEEKSPAN),
                         'professor_name':professor_name,
                         'ical_q1_url':ical_urls[0],
                         'ical_q2_url':ical_urls[1],
                         'ical_q1_url_title':ical_url_titles[0],
                         'ical_q2_url_title':ical_url_titles[1],
                         'q1_span': "from %s to %s" %
                           tuple([q1_span[i].strftime("%B %d, %Y") for i in (0, 1)]),
                         'q2_span': "from %s to %s" %
                           tuple([q2_span[i].strftime("%B %d, %Y") for i in (0, 1)]),
        }


        #self._save_successful_request(professor_name, "/staff/%s" % staff_member_id)
        path = os.path.join(os.path.dirname(__file__), 'templates/staff.html')
        self.response.out.write(template.render(path, template_values))



    def _render_not_found_page(self):
        render_professor_notfound_page(self, resource_type="summary page")



    @staticmethod
    def _extract_staff_member_id(gehol_url):
        parsed = urlparse.urlparse(gehol_url)
        p = parsed.params
        # should look like : 'Staff;id;52485'
        # we keep the last part
        return p.split(';')[-1]






class ProfessorIcalRenderer(webapp.RequestHandler):
    calendar_fetch_funcs = {'q1': get_professor_q1_calendar,
                            'q2': get_professor_q2_calendar}
    def get(self):

        if is_status_down():
            render_gehol_down(self, "You asked an iCalendar file for a particular professor.")
        else:
            parsed = urlparse.urlparse(self.request.uri)
            staff_member_id = parsed.path.split("/")[4].rstrip(".ics")
            term = parsed.path.split("/")[3]

            if term in ("q1", "q2"):
                try:
                    cal = self.calendar_fetch_funcs[term](staff_member_id)
                except DownloadError,e:
                    logging.error("Could not fetch page before deadline")
                    render_deadline_exceeded_page(self)

                if cal:
                    ical_data = convert_professor_calendar_to_ical_string(cal)

                    professor_name = cal.header_data['teacher_name']
                    ical_filename = "ULB - "+ term.upper() + " - " + professor_name.encode("iso-8859-1")
                    self.response.headers['Content-Type'] = "text/calendar; charset=utf-8"
                    self.response.headers['Content-disposition'] = "attachment; filename=%s.ics" % ical_filename
                    self.response.out.write(ical_data)
                else:
                    render_professor_notfound_page(self, resource_type="iCal file")
            else:
                render_professor_notfound_page(self, resource_type="iCal file")

