import os
import urlparse
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from status import is_status_down, get_last_status_update
from gehol2csv import get_calendar
from utils import is_course_mnemo_valid
from savedrequests import PreviousRequest

class CourseCalendar(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        course_mnemo = self._get_course_mnemo(parsed.path)

        if is_course_mnemo_valid(course_mnemo):
            cal = get_calendar(course_mnemo)
            ical_url, csv_url = self._build_file_urls(course_mnemo)

            template_values = {'gehol_is_down': is_status_down(),
                               'last_status_update': get_last_status_update(),
                               'mnemo':course_mnemo,
                               'ical_url':ical_url,
                               'csv_url':csv_url
            }

            template_values.update(cal.metadata)

            path = os.path.join(os.path.dirname(__file__), 'templates/course.html')
            self.response.out.write(template.render(path, template_values))

            request = PreviousRequest()
            request.content = course_mnemo
            request.put()

        else:
            self._render_not_found_page(course_mnemo)


    def _render_not_found_page(self, course_mnemo):
        template_values = {'gehol_is_down': is_status_down(),
                           'last_status_update': get_last_status_update(),
                           'mnemo':course_mnemo,
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/course_notfound.html')
        self.response.out.write(template.render(path, template_values))



    @staticmethod
    def _build_file_urls(course_mnemo):
        return ("/ical/%s.ics" % course_mnemo,
                "/csv/%s.csv" % course_mnemo)

    @staticmethod
    def _get_course_mnemo(path):
        return path.split('/')[2]


