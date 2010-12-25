import sys
sys.path.append('./dependencies')
from gehol.coursecalendar import CourseCalendar, GeholException
from gehol.converters.csvwriter import to_csv
from gehol.converters.icalwriter import to_ical
from gehol.converters.icalwriter import convert_student_calendar_to_ics_rfc5545
from gehol import GeholProxy
from gehol.studentcalendar import StudentCalendar
import httplib, urlparse

host = '164.15.72.157:8080'
first_monday = '20/09/2010'


def get_calendar(course_mnemonic):
    gehol_proxy = GeholProxy(host)
    try:
        return gehol_proxy.get_course_calendar(course_mnemonic)
    except GeholException:
        return None


def convert_calendar(cal):
    try:
        csv_string = to_csv(cal.metadata, cal.events, first_monday)
        ical_string = to_ical(cal.metadata, cal.events, first_monday)
        error = False
    except Exception,e:
        error = True
        csv_string = 'Problem with: "%s" [%s]'%(cal.metadata['mnemo'], e.message)
        ical_string = ''
        
    return error, csv_string,ical_string


def get_student_calendar(url):
    try:
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/html",
                   "Accept-Charset":"*"}

        parsed_url = urlparse.urlparse(url)
        scheme, netloc, path, params, query, frag = parsed_url

        conn = httplib.HTTPConnection(netloc)
        conn.request("GET", "%s;%s?%s" % (path, params, query), headers = headers)
        response = conn.getresponse()
        html = response.read()
        cal = StudentCalendar(html)
        return cal
    except Exception,e:
        raise ValueError('Could not get fetch url : %s (Reason : %s)' % (url, e.message))


def convert_student_calendar(cal):
    try:
        ical_data = convert_student_calendar_to_ics_rfc5545(cal, first_monday)
        return ical_data
    except Exception,e:
        return None