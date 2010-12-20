import os
import urlparse
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from gehol2csv import get_calendar, convert_calendar
from status import is_status_down, get_last_status_update
from check_status import UpdateGeholStatus

class PreviousRequest(db.Model):
    author = db.UserProperty()
    content = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        requests_query = PreviousRequest.all().order('-date')
        requests = requests_query.fetch(10)


        template_values = {'requests': requests,
                           'gehol_is_down': is_status_down(),
                           'last_status_update': get_last_status_update()
                        }

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))



class Calendar(webapp.RequestHandler):
    def post(self):
        course_mnemo = self.request.get('course_mnemo')

        cal = get_calendar(course_mnemo)

        error,csv,ical = convert_calendar(cal)
        events_csv = csv.splitlines()
        events_ical = ical.splitlines()


        request = PreviousRequest()
        #if success, the request is recorded
        if not error:
            request.content = self.request.get('course_mnemo')
            request.put()

        template_values = {
            'mnemo':course_mnemo,
            'calendar':cal,
            'events_csv@': events_csv,
            'events_ical': events_ical,
        }

        template_values.update(cal.metadata)
        template_values.update({'gehol_is_down' : is_status_down(),
                                'last_status_update': get_last_status_update()})

        path = os.path.join(os.path.dirname(__file__), 'templates/calendar.html')
        self.response.out.write(template.render(path, template_values))



class CourseCalendar(webapp.RequestHandler):
    def get(self):
        parsed = urlparse.urlparse(self.request.uri)
        course_mnemo = self._get_course_mnemo(parsed.path)

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


    @staticmethod
    def _build_file_urls(course_mnemo):
        return ("/ical/%s.ics" % course_mnemo,
                "/csv/%s.csv" % course_mnemo)

    @staticmethod
    def _get_course_mnemo(path):
        return path.split('/')[2]



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


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                     ('/cal', Calendar),
                                     ('/course/.*', CourseCalendar),
                                     ('/ical/.*\.ics', IcalRenderer),
                                     ('/geholstatus',  UpdateGeholStatus),
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
