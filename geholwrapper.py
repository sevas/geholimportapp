import sys
sys.path.append('./dependencies')

from gehol.converters.csvwriter import to_csv
from gehol.converters.icalwriter import to_ical
from gehol.converters.rfc5545icalwriter import convert_calendar_to_ical
from gehol import GeholProxy, GeholException

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


def get_student_calendar(group_id):
    gehol_proxy = GeholProxy(host)
    try:
        cal = gehol_proxy.get_student_calendar(group_id)
        return cal
    except Exception,e:
        return None
    

def convert_student_calendar(cal):
    try:
        ical_data = convert_calendar_to_ical(cal, first_monday)
        return ical_data
    except Exception,e:
        return None