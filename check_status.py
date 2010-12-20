import httplib
import socket
import logging
from google.appengine.ext import webapp
from status import set_status_down

class UpdateGeholStatus(webapp.RequestHandler):
    def get(self):
        logging.info("Launching UpdateGeholStatus cron job")
        self.update_gehol_status()


    def update_gehol_status(self):
        host = "164.15.72.157:8080"
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        try:
            conn = httplib.HTTPConnection(host)
            conn.request("GET", '/', headers = headers)
            response = conn.getresponse()
            set_status_down(False)
        except socket.error,e:
            set_status_down(True)
