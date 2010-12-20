import os
import urlparse
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from gehol2csv import get_calendar, convert_calendar
from status import is_status_down, get_last_status_update
from check_status import UpdateGeholStatus
from coursecalendar import CourseCalendar
from icalrenderer import IcalRenderer
#from csvrenderer import CSVRenderer


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
