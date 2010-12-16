import sys
sys.path.append('./dependencies')
from gehol.coursecalendar import CourseCalendar
from gehol.converters.csvwriter import to_csv
from gehol.converters.icalwriter import to_ical
from gehol import GeholProxy


host = '164.15.72.157:8080'
first_monday = '20/09/2010'

def gehol2csv(course_mnemonic):

    gehol_proxy = GeholProxy(host)
    try:
        cal = gehol_proxy.get_course_calendar(course_mnemonic)
        csv_string = to_csv(cal.metadata, cal.events, first_monday)
        ical_string = to_ical(cal.metadata, cal.events, first_monday)
        error = False
    except Exception,e:
        error = True
        csv_string = 'Problem with: "%s" [%s]'%(course_mnemonic,e.message)
        ical_string = ''

    return [error, csv_string,ical_string]

