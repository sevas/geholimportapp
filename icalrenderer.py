import os
import urlparse
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from status import is_status_down, get_last_status_update
from gehol2csv import get_calendar, convert_calendar


class IcalRenderer(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        course_mnemo = parsed.path.split("/")[2].rstrip(".ics")

        if self._is_course_mnemo_valid(course_mnemo):
            cal = get_calendar(course_mnemo)

            error,csv,ical = convert_calendar(cal)
            events_ical = ical

            self.response.headers['Content-Type'] = "text/plain;  charset=utf-8"
            self.response.out.write(events_ical)
        else:
            self.redirect("/ical/notfound")

    @staticmethod
    def _is_course_mnemo_valid(course_mnemo):
        return course_mnemo.isalnum() and len(course_mnemo) == 8