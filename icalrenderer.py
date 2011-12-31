import os
import urlparse
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api.urlfetch import DownloadError
from geholwrapper import get_calendar, convert_course_calendar_to_ical
from status import is_status_down, get_last_status_update
from utils import is_course_mnemo_valid, render_course_notfound_page, render_deadline_exceeded_page
import conf

class IcalRenderer(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        course_mnemo = parsed.path.split("/")[3].rstrip(".ics")

        if is_course_mnemo_valid(course_mnemo):
            if is_status_down():
                self._render_gehol_down_page(course_mnemo)
            else:
                try:
                    cal = get_calendar(course_mnemo, conf.Q2_WEEKSPAN)
                except DownloadError,e:
                    logging.error("Could not fetch page before deadline")
                    render_deadline_exceeded_page(self)
                    return
                if cal:
                    ical_content = convert_course_calendar_to_ical(cal)
                    self.response.headers['Content-Type'] = "text/calendar;  charset=utf-8"
                    self.response.headers['Content-disposition'] = "attachment; filename=%s.ics" % course_mnemo
                    self.response.out.write(ical_content)
                else:
                    self._render_not_found_page(course_mnemo)
        else:
            self._render_not_found_page(course_mnemo)



    def _render_not_found_page(self, course_mnemo):
        render_course_notfound_page(self, course_mnemo, "iCal file")


    def _render_gehol_down_page(self, course_mnemo):
        reason = "You asked the iCal file for the following course : %s." % course_mnemo
        template_values = {'gehol_is_down': True,
                           'last_status_update': get_last_status_update(),
                           'request':reason
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/gehol_down.html')
        self.response.out.write(template.render(path, template_values))