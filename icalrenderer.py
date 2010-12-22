import os
import urlparse
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from gehol2csv import get_calendar, convert_calendar
from status import is_status_down, get_last_status_update
from utils import is_course_mnemo_valid, render_resource_notfound_page

class IcalRenderer(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        course_mnemo = parsed.path.split("/")[2].rstrip(".ics")

        if is_course_mnemo_valid(course_mnemo):
            if is_status_down():
                self._render_gehol_down_page(course_mnemo)
            else:
                cal = get_calendar(course_mnemo)
                if cal:
                    error,csv,ical = convert_calendar(cal)
                    events_ical = ical

                    self.response.headers['Content-Type'] = "text/calendar;  charset=utf-8"
                    self.response.headers['Content-disposition'] = "attachment; filename=%s.ics" % course_mnemo
                    self.response.out.write(events_ical)
                else:
                    self._render_not_found_page(course_mnemo)
        else:
            self._render_not_found_page(course_mnemo)



    def _render_not_found_page(self, course_mnemo):
        render_resource_notfound_page(self, course_mnemo, 'iCal file')


    def _render_gehol_down_page(self, course_mnemo):
        reason = "You asked the iCal file for the following course : %s." % course_mnemo
        template_values = {'gehol_is_down': True,
                           'last_status_update': get_last_status_update(),
                           'request':reason
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/gehol_down.html')
        self.response.out.write(template.render(path, template_values))