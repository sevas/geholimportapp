import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from status import is_status_down, get_last_status_update
from check_status import UpdateGeholStatus
from coursecalendar import CourseCalendar
from icalrenderer import IcalRenderer
from studentsetcalendar import StudentSetSummary, StudentSetIcalRenderer, StudentSetMobileSummary, StudentSetQRCode
from professorcalendar import ProfessorIcalRenderer, ProfessorSummary
from savedrequests import PreviousRequest, PreviousStudentSetRequests
import conf
import version


class MainPage(webapp.RequestHandler):
    def get(self):
        last_fetched_courses = self._get_last_entries_from_store(PreviousRequest)
        last_fetched_studentsets = self._get_last_entries_from_store(PreviousStudentSetRequests)

        template_values = {'last_courses': last_fetched_courses,
                           'last_studentsets':last_fetched_studentsets,
                           'gehol_is_down': is_status_down(),
                           'last_status_update': get_last_status_update(),
                           'version':version.VERSION
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
            student_gehol_url = self.request.get('student_gehol_url')
            if student_gehol_url:
                group_id = StudentSetSummary._extract_group_id(student_gehol_url)
                self.redirect("/student_set/%s" % group_id)
            else:
                professor_gehol_url = self.request.get('professor_gehol_url')
                if professor_gehol_url:
                    staff_member_id = ProfessorSummary._extract_staff_member_id(professor_gehol_url)
                    self.redirect("/staff/%s" % staff_member_id)
                else:
                    self.redirect("/")


class QuestionsPage(webapp.RequestHandler):
    def get(self):
        template_values = {'version':version.VERSION,
                            'gehol_is_down': is_status_down(),
                          'last_status_update': get_last_status_update(),
                          'qrcode_sample_url': conf.QRCODE_SAMPLE_URL
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/questions.html')
        self.response.out.write(template.render(path, template_values))



application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                     ('/redirect', Redirect),
                                     ('/course/ical/.*', IcalRenderer),
                                     ('/course/.*', CourseCalendar),
                                     ('/geholstatus',  UpdateGeholStatus),
                                     ('/student_set/ical/q./.*\.ics', StudentSetIcalRenderer),
                                     ('/student_set/ical/january_exams/.*\.ics', StudentSetIcalRenderer),
                                     ('/student_set/ical/june_exams/.*\.ics', StudentSetIcalRenderer),
                                     ('/student_set/ical/september_exams/.*\.ics', StudentSetIcalRenderer),
                                     ('/student_set/qrcode/.*', StudentSetQRCode),
                                     ('/student_set/m/.*', StudentSetMobileSummary),
                                     ('/student_set/.*', StudentSetSummary ),
                                     ('/staff/ical/.*\.ics', ProfessorIcalRenderer),
                                     ('/staff/.*', ProfessorSummary),
                                     ('/questions.*', QuestionsPage),
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
