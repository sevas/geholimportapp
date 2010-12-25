import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from status import is_status_down, get_last_status_update
from check_status import UpdateGeholStatus
from coursecalendar import CourseCalendar
from icalrenderer import IcalRenderer
from csvrenderer import CSVRenderer
from studentcalendar import StudentCalendarPage, StudentURLQuery, StudentCalendarIcalRenderer
from savedrequests import PreviousRequest


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
        self.redirect("/course/%s" % course_mnemo.upper())



application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                     ('/cal', Calendar),
                                     ('/course/.*', CourseCalendar),
                                     ('/ical/.*', IcalRenderer),
                                     ('/csv/.*', CSVRenderer),
                                     ('/geholstatus',  UpdateGeholStatus),
                                     ('/student_url', StudentURLQuery),
                                     ('/student/ical.*', StudentCalendarIcalRenderer),
                                     ('/student', StudentCalendarPage )
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
