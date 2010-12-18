import os
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from gehol2csv import get_calendar, convert_calendar


class PreviousRequest(db.Model):
    author = db.UserProperty()
    content = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        requests_query = PreviousRequest.all().order('-date')
        requests = requests_query.fetch(10)
        
        template_values = {
            'requests': requests,
            }

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))



class Calendar(webapp.RequestHandler):
    def post(self):

        request = PreviousRequest()

        course_mnemo = self.request.get('content')

        cal = get_calendar(course_mnemo)

        error,csv,ical = convert_calendar(cal)
        events_csv = csv.splitlines()
        events_ical = ical.splitlines()

        #if success, the request is recorded
        if not error:
            request.content = self.request.get('content')
            request.put()

        template_values = {
            'mnemo':course_mnemo,
            'calendar':cal,
            'events_csv': events_csv,
            'events_ical': events_ical,
            }

        template_values.update(cal.metadata)

        path = os.path.join(os.path.dirname(__file__), 'templates/calendar.html')
        self.response.out.write(template.render(path, template_values))




application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                     ('/cal', Calendar),
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()