import os
import urlparse
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api.urlfetch import DownloadError
from status import is_status_down, get_last_status_update
from geholwrapper import get_calendar, rebuild_course_gehol_url
from utils import is_course_mnemo_valid, render_course_notfound_page, render_deadline_exceeded_page
from savedrequests import PreviousRequest
from gehol.utils import convert_weekspan_to_dates
from conf import COURSE_QRCODE_URL_TEMPLATE

def rebuild_gehol_url(group_id):
    return "http://164.15.72.157:8080/Reporting/Individual;Student%20Set%20Groups;id;"+group_id+"?&template=Ann%E9e%20d%27%E9tude&weeks=1-14&days=1-6&periods=5-33&width=0&height=0"



class CourseCalendar(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        course_mnemo = self._get_course_mnemo(parsed.path)


        if is_course_mnemo_valid(course_mnemo):
            if is_status_down():
                self._render_gehol_down_page(course_mnemo)
            else:
                try:
                    cal = get_calendar(course_mnemo)
                except DownloadError,e:
                    logging.error("Could not fetch page before deadline")
                    render_deadline_exceeded_page(self)
                    return

                if cal:
                    self._render_calendar_summary(cal, course_mnemo)
                    self._save_successful_request(course_mnemo)
                else:
                    self._render_not_found_page(course_mnemo)
        else:
            self._render_not_found_page(course_mnemo)
            

    def _render_calendar_summary(self, cal, course_mnemo):
        ical_url, csv_url = self._build_file_urls(course_mnemo)
        start, end = convert_weekspan_to_dates("1-36", "20/09/2010")
        caption = "Schedule from %s to %s" % (start.strftime("%B %d, %Y"),
                                              end.strftime("%B %d, %Y"))

        template_values = {'gehol_is_down': is_status_down(),
                         'last_status_update': get_last_status_update(),
                        'mnemo':course_mnemo,
                        'ical_url':ical_url,
                        'csv_url':csv_url,
                        'caption':caption,
                        'gehol_url': rebuild_course_gehol_url(course_mnemo),
                        'big_qrcode_url': COURSE_QRCODE_URL_TEMPLATE % (course_mnemo, 512, 512),
                        'small_qrcode_url': COURSE_QRCODE_URL_TEMPLATE % (course_mnemo, 256, 256)
        }

        template_values.update(cal.metadata)
        path = os.path.join(os.path.dirname(__file__), 'templates/course.html')
        self.response.out.write(template.render(path, template_values))


    def _save_successful_request(self, course_mnemo):
        request = PreviousRequest()
        request.content = course_mnemo
        request.put()


    def _render_not_found_page(self, course_mnemo):
        render_course_notfound_page(self, course_mnemo, "summary page")


    def _render_gehol_down_page(self, course_mnemo):
        reason = "You asked the schedule for the following course : %s." % course_mnemo
        template_values = {'gehol_is_down': is_status_down(),
                           'last_status_update': get_last_status_update(),
                           'request':reason
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/gehol_down.html')
        self.response.out.write(template.render(path, template_values))

    @staticmethod
    def _build_file_urls(course_mnemo):
        return ("/course/ical/%s.ics" % course_mnemo,
                "/course/csv/%s.csv" % course_mnemo)

    @staticmethod
    def _get_course_mnemo(path):
        return path.split('/')[2]


