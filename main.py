import os
from google.appengine.ext.webapp import template

import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from gehol2csv import gehol2csv


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

        content = self.request.get('content')
        error,csv,ical = gehol2csv(content)
        events_csv = csv.splitlines()
        events_ical = ical.splitlines()

        #if success, the request is recorded
        if not error:
            request.content = self.request.get('content')
            request.put()


        template_values = {
            'content':content,
            'events_csv': events_csv,
            'events_ical': events_ical,
            }

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