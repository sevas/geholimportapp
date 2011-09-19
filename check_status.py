import httplib
import logging
from google.appengine.ext import webapp
from status import set_status_down
from conf import SCIENTIA_BACKEND_HOST, GEHOL_FRONTEND_URL

def check_server(host):
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    conn = httplib.HTTPConnection(host)
    conn.request("GET", '/', headers = headers)
    response = conn.getresponse()
    return True


def check_gateway():
    host = GEHOL_FRONTEND_URL
    logging.info("Testing GeHoL gateway : %s " % host)
    return check_server(host)


def check_scientia_backend():
    host = SCIENTIA_BACKEND_HOST
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
