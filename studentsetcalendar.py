__author__ = 'sevas'

import os
import urlparse
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from status import is_status_down, get_last_status_update
from geholwrapper import get_student_calendar, convert_student_calendar
from utils import render_resource_notfound_page


class StudentURLQuery(webapp.RequestHandler):
    def get(self):

        template_values = {'gehol_is_down': is_status_down(),
                         'last_status_update': get_last_status_update(),
        }

        #http://164.15.72.157:8080/Reporting/Individual;Student%20Set%20Groups;id;%23SPLUS3C1E8E?&template=Ann%E9e%20d%27%E9tude&weeks=1-14&days=1-6&periods=5-33&width=0&height=0
        path = os.path.join(os.path.dirname(__file__), 'templates/student_url.html')
        self.response.out.write(template.render(path, template_values))


class StudentCalendarPage(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        group_id = parsed.path.split("/")[2]

        # TODO = sanitize url
        cal = get_student_calendar(group_id)
        if cal:
            faculty, student_profile = cal.header_data['faculty'], cal.header_data['student_profile']
            event_titles = set(["%s (%s) [%s]" %  (e['title'], e['type'], e['organizer']) for e in cal.events])
            ical_url = "/student_set/ical/%s" % group_id
            ical_url_title = "ULB - %s" % student_profile



            template_values = {'gehol_is_down': is_status_down(),
                             'last_status_update': get_last_status_update(),
                             #'gehol_url':gehol_url,
                             'cal_faculty':faculty,
                             'cal_student_profile':student_profile,
                             'cal_events':event_titles,
                             'ical_url':ical_url,
                             'ical_url_title':ical_url_title
            }

            path = os.path.join(os.path.dirname(__file__), 'templates/student.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self._render_not_found_page(group_id)


    def _render_not_found_page(self, group_id):
        render_resource_notfound_page(self, group_id, 'student set page')


    @staticmethod
    def _extract_group_id(gehol_url):
        parsed = urlparse.urlparse(gehol_url)
        p = parsed.params
        # should look like : 'Student%20Set%20Groups;id;%23SPLUS35F073'
        # we keep the last part
        return p.split(';')[-1]



class StudentCalendarIcalRenderer(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        group_id = parsed.path.split("/")[3]

        cal = get_student_calendar(group_id)
        if cal:
            ical_data = convert_student_calendar(cal)

            student_profile = cal.header_data['student_profile']
            ical_filename = "ULB - %s" % student_profile

            self.response.headers['Content-Type'] = "text/calendar;  charset=utf-8"
            self.response.headers['Content-disposition'] = "attachment; filename=%s.ics" % ical_filename
            self.response.out.write(ical_data)
        else:
            pass

    @staticmethod
    def _rebuild_gehol_url(group_id):
        return "http://164.15.72.157:8080/Reporting/Individual;Student%20Set%20Groups;id;"+group_id+"?&template=Ann%E9e%20d%27%E9tude&weeks=1-14&days=1-6&periods=5-33&width=0&height=0"