__author__ = 'sevas'

import os
import urlparse
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from status import is_status_down, get_last_status_update
from geholwrapper import get_student_calendar, convert_student_calendar
from savedrequests import PreviousStudentSetRequests

def rebuild_gehol_url(group_id):
    return "http://164.15.72.157:8080/Reporting/Individual;Student%20Set%20Groups;id;"+group_id+"?&template=Ann%E9e%20d%27%E9tude&weeks=1-14&days=1-6&periods=5-33&width=0&height=0"


def render_studentset_notfound_page(request_handler, resource_type):
    template_values = {'gehol_is_down': is_status_down(),
                       'last_status_update': get_last_status_update(),
                       'resource_type':resource_type
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/studentset_notfound.html')
    request_handler.response.out.write(template.render(path, template_values))


def is_studentset_groupid_valid(group_id):
    return len(group_id) == 14 and  group_id[:3] == "%23" and group_id[3:].isalnum()


class StudentSetSummary(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        group_id = parsed.path.split("/")[2]

        if is_studentset_groupid_valid(group_id):
            logging.debug("group '%s' id is valid" % group_id)
            cal = get_student_calendar(group_id)
            if cal:
                logging.info("got a calendar from gorup id")
                faculty, student_profile = cal.header_data['faculty'], cal.header_data['student_profile']
                event_titles = set(["%s (%s) [%s]" %  (e['title'], e['type'], e['organizer']) for e in cal.events])
                ical_url = "/student_set/ical/%s.ics" % group_id
                ical_url_title = "ULB - %s" % student_profile



                template_values = {'gehol_is_down': is_status_down(),
                                 'last_status_update': get_last_status_update(),
                                 'gehol_url':rebuild_gehol_url(group_id),
                                 'cal_faculty':faculty,
                                 'cal_student_profile':student_profile,
                                 'cal_events':event_titles,
                                 'ical_url':ical_url,
                                 'ical_url_title':ical_url_title
                }

                self._save_successful_request(student_profile, "/student_set/%s" % group_id)
                path = os.path.join(os.path.dirname(__file__), 'templates/student.html')
                self.response.out.write(template.render(path, template_values))
            else:
                logging.debug("did not receive a calendar")
                self._render_not_found_page()
        else:
            logging.debug("group id '%s' is not valid" % group_id)
            self._render_not_found_page()


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


class StudentSetIcalRenderer(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        group_id = parsed.path.split("/")[3].rstrip(".ics")

        cal = get_student_calendar(group_id)
        if cal:
            ical_data = convert_student_calendar(cal)

            student_profile = cal.header_data['student_profile']
            ical_filename = "ULB - %s" % student_profile

            self.response.headers['Content-Type'] = "text/calendar;  charset=utf-8"
            self.response.headers['Content-disposition'] = "attachment; filename=%s.ics" % ical_filename
            self.response.out.write(ical_data)
        else:
            render_studentset_notfound_page(self, resource_type="iCal file")

