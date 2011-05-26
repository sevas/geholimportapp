import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from status import is_status_down, get_last_status_update
from check_status import UpdateGeholStatus
from coursecalendar import CourseCalendar
from icalrenderer import IcalRenderer
from csvrenderer import CSVRenderer
from studentsetcalendar import StudentSetSummary, StudentSetIcalRenderer, StudentSetMobileSummary, StudentSetQRCode 
from savedrequests import PreviousRequest, PreviousStudentSetRequests


class MainPage(webapp.RequestHandler):
    def get(self):
        last_fetched_courses = self._get_last_entries_from_store(PreviousRequest)
        last_fetched_studentsets = self._get_last_entries_from_store(PreviousStudentSetRequests)

        template_values = {'last_courses': last_fetched_courses,
                           'last_studentsets':last_fetched_studentsets,
                           'gehol_is_down': is_status_down(),
                           'last_status_update': get_last_status_update()
                        }

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))


    def _get_last_entries_from_store(self, Datastore):
        # TODO : see if we can filter the last 10 entries earlier
        query = Datastore.all().order('-date')
        return query.fetch(10)

class Redirect(webapp.RequestHandler):
    def post(self):
        course_mnemo = self.request.get('course_mnemo')
        if course_mnemo:
            self.redirect("/course/%s" % course_mnemo.upper())
        else:
            gehol_url = self.request.get('gehol_url')
            if gehol_url:
                group_id = StudentSetSummary._extract_group_id(gehol_url)
                self.redirect("/student_set/%s" % group_id)
            else:
                self.redirect("/")


class QuestionsPage(webapp.RequestHandler):
    def get(self):
        template_values = {'gehol_is_down': is_status_down(),
                          'last_status_update': get_last_status_update()
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/questions.html')
        self.response.out.write(template.render(path, template_values))



application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                     ('/redirect', Redirect),
                                     ('/course/ical/.*', IcalRenderer),
                                     ('/course/csv/.*', CSVRenderer),
                                     ('/course/.*', CourseCalendar),
                                     ('/geholstatus',  UpdateGeholStatus),
                                     ('/student_set/ical/q./.*\.ics', StudentSetIcalRenderer),
                                     ('/student_set/ical/january_exams/.*\.ics', StudentSetIcalRenderer),
                                     ('/student_set/ical/june_exams/.*\.ics', StudentSetIcalRenderer),
                                     ('/student_set/ical/september_exams/.*\.ics', StudentSetIcalRenderer),
                                     ('/student_set/qrcode/.*', StudentSetQRCode),
                                     ('/student_set/m/.*', StudentSetMobileSummary),
                                     ('/student_set/.*', StudentSetSummary ),
                                     ('/questions.*', QuestionsPage),
                                     #('.*', MainPage)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
