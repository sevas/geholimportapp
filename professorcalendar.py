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
from geholwrapper import get_professor_q1_calendar, convert_professor_calendar_to_ical_string
from gehol.utils import convert_weekspan_to_dates
import conf




class StudentSetSummary(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        group_id = parsed.path.split("/")[2]

        if is_status_down():
            render_gehol_down(self, "You asked the schedule for a particular student profile.")
        else:
            if is_studentset_groupid_valid(group_id):
                logging.debug("group '%s' id is valid" % group_id)
                try:
                    cal = get_student_q1_calendar(group_id)
                except DownloadError,e:
                    logging.error("Could not fetch page before deadline")
                    render_deadline_exceeded_page(self)
                    return
                if cal:
                    self._render_calendar_summary(cal, group_id)
                else:
                    logging.debug("did not receive a calendar")
                    self._render_not_found_page()
            else:
                logging.debug("group id '%s' is not valid" % group_id)
                self._render_not_found_page()


    def _render_calendar_summary(self, cal, group_id):
        logging.info("got a calendar from group id: %s" % group_id)
        faculty, student_profile = (cal.header_data['faculty'],
                                    cal.header_data['student_profile'])

        ical_urls = ["/staff/ical/%s/%s.ics" % (q, group_id) for q in ("q1", "q2")]
        ical_url_titles = ["ULB - %s -  %s" % (q, student_profile) for q in ("Q1", "Q2")]


        q1_span = convert_weekspan_to_dates(conf.Q1_WEEKSPAN, conf.FIRST_MONDAY)
        q2_span = convert_weekspan_to_dates(conf.Q2_WEEKSPAN, conf.FIRST_MONDAY)

        template_values = {'gehol_is_down': is_status_down(),
                         'last_status_update': get_last_status_update(),
                         'gehol_url':make_studentset_gehol_url(group_id, conf.Q1_WEEKSPAN),
                         'cal_faculty':faculty,
                         'cal_student_profile':student_profile,
                         'ical_q1_url':ical_urls[0],
                         'ical_q2_url':ical_urls[1],
                         'ical_q1_url_title':ical_url_titles[0],
                         'ical_q2_url_title':ical_url_titles[1],
                         'q1_span': "from %s to %s" %
                           tuple([q1_span[i].strftime("%B %d, %Y") for i in (0, 1)]),
                         'q2_span': "from %s to %s" %
                           tuple([q2_span[i].strftime("%B %d, %Y") for i in (0, 1)]),
        }


        current_session_name = conf.CURRENT_EXAM_SESSION
        exam_session = None
        if current_session_name:
            exam_session = self._extract_current_session_info(current_session_name, group_id, student_profile)

        template_values['exam_session'] = exam_session

        self._save_successful_request(student_profile, "/student_set/%s" % group_id)
        path = os.path.join(os.path.dirname(__file__), 'templates/student.html')
        self.response.out.write(template.render(path, template_values))



    def _extract_current_session_info(self, session_name, group_id, student_profile):
        weekspan = conf.EXAM_SESSION_WEEKSPANS[session_name]

        session_weekspan = convert_weekspan_to_dates(weekspan, conf.FIRST_MONDAY)
        ical_url, title = self._make_exam_session_url_and_title(group_id, student_profile, session_name)

        exam_session = ExamSessionInfo(session_name, ical_url, title,
                                    "from %s to %s" % tuple([session_weekspan[i].strftime("%B %d, %Y") for i in (0, 1)]),
                                    self._is_exam_session_available(group_id, weekspan)
        )

        return exam_session


    @staticmethod
    def _make_exam_session_url_and_title(group_id, student_profile, session_name):
        return ("/student_set/ical/%s_exams/%s.ics" % (session_name, group_id),
                "ULB - %s exams session -  %s" % (session_name.capitalize(), student_profile))



    def _is_exam_session_available(self, group_id, weekspan):
        cal = get_student_exam_calendar(group_id, weekspan)
        return cal.has_events()



    def _render_not_found_page(self):
        render_studentset_notfound_page(self, resource_type="summary page")



    @staticmethod
    def _extract_group_id(gehol_url):
        parsed = urlparse.urlparse(gehol_url)
        p = parsed.params
        # should look like : 'Student%20Set%20Groups;id;%23SPLUS35F073'
        # we keep the last part
        return p.split(';')[-1]


    def _save_successful_request(self, title, url):
        request = PreviousStudentSetRequests()
        request.url = url
        request.title = title
        request.put()












class ProfessorIcalRenderer(webapp.RequestHandler):
    calendar_fetch_funcs = {'q1': get_student_q1_calendar,
                            'q2': get_student_q2_calendar,
                            'january_exams': get_student_jan_calendar,
                            'june_exams': get_student_june_calendar,
                            'september_exams': get_student_sept_calendar}
    def get(self):

        if is_status_down():
            render_gehol_down(self, "You asked an iCalendar file for a particular student profile.")
        else:
            parsed = urlparse.urlparse(self.request.uri)
            group_id = parsed.path.split("/")[4].rstrip(".ics")
            term = parsed.path.split("/")[3]

            if term in ("q1", "q2", "january_exams", "june_exams", "september_exams"):
                try:
                    cal = self.calendar_fetch_funcs[term](group_id)
                except DownloadError,e:
                    logging.error("Could not fetch page before deadline")
                    render_deadline_exceeded_page(self)

                if cal:
                    ical_data = convert_student_calendar_to_ical_string(cal)

                    student_profile = cal.header_data['student_profile']
                    ical_filename = "ULB - "+ term.upper() + " - " + student_profile.encode("iso-8859-1")
                    self.response.headers['Content-Type'] = "text/calendar; charset=utf-8"
                    self.response.headers['Content-disposition'] = "attachment; filename=%s.ics" % ical_filename
                    self.response.out.write(ical_data)
                else:
                    render_studentset_notfound_page(self, resource_type="iCal file")
            else:
                render_studentset_notfound_page(self, resource_type="iCal file")

