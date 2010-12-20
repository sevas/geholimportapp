import httplib
import socket

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from status import set_status_down

def update_gehol_status():
    host = "164.15.72.157:8080"
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    conn = httplib.HTTPConnection(host)
    try:
        conn.request("GET", '/', headers = headers)
        response = conn.getresponse()
        set_status_down(False)
    except socket.error,e:
        set_status_down(True)


class UpdateGeholStatus(webapp.RequestHandler):
    def get(self):
        update_gehol_status()
        
application = webapp.WSGIApplication([('/geholstatus', UpdateGeholStatus)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()