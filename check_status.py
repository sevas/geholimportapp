import httplib
import socket
import logging
from google.appengine.ext import webapp
from status import set_status_down


def check_server(host):
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    conn = httplib.HTTPConnection(host)
    conn.request("GET", '/', headers = headers)
    response = conn.getresponse()
    return True


def check_gateway():
    host = "164.15.72.157"    
    logging.info("Testing GeHoL gateway : %s " % host)
    return check_server(host)

def check_scientia_backend():
    host = "164.15.72.157:8080"    
    logging.info("Testing Scientia backend : %s " % host)
    return check_server(host)



class UpdateGeholStatus(webapp.RequestHandler):
    def get(self):
        logging.info("Launching UpdateGeholStatus cron job")
        self.update_gehol_status()


    def update_gehol_status(self):
        try:
            check_gateway()
            check_scientia_backend()
            set_status_down(False)
        except Exception,e:
            set_status_down(True)
