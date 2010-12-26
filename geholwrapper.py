import sys
sys.path.append('./dependencies')
import logging
from gehol.converters.csvwriter import to_csv
from gehol.converters.rfc5545icalwriter import convert_geholcalendar_to_ical
import gehol
host = '164.15.72.157:8080'
first_monday = '20/09/2010'

def get_calendar(course_mnemonic):
    gehol_proxy = gehol.GeholProxy(host)
    try:
        return gehol_proxy.get_course_calendar(course_mnemonic)
    except GeholException:
        return None


def convert_calendar(cal):
    try:
        csv_string = to_csv(cal.metadata, cal.events, first_monday)
        ical_string = cal.as_string()
        return csv_string,ical_string

    except Exception,e:
        return None
        


def get_student_calendar(group_id):
    gehol_proxy = gehol.GeholProxy(host)
    cal = gehol_proxy.get_studentset_calendar(group_id, "1-14")
    return cal
    

def convert_student_calendar(cal):
    try:
        ical_data = convert_geholcalendar_to_ical(cal, first_monday)
        return ical_data.as_string()
    except Exception,e:
        return None