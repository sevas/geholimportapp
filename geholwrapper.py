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
    except gehol.GeholException:
        return None


def convert_course_calendar_to_csv(cal):
    try:
        csv_string = to_csv(cal.metadata, cal.events, first_monday)
        return csv_string

    except Exception,e:
        logging.debug("something went wrong while converting calendar %s : %s" % (cal.name, e.message))
        return None


def convert_course_calendar_to_ical(cal):
    ical = convert_geholcalendar_to_ical(cal, first_monday)
    return ical.as_string()


def get_student_q1_calendar(group_id):
    return get_student_calendar(group_id, "1-14")


def get_student_q2_calendar(group_id):
    return get_student_calendar(group_id, "21-36")


def get_student_jan_calendar(group_id):
    return get_student_calendar(group_id, "17-19")


def get_student_calendar(group_id, weeks):
    try:
        gehol_proxy = gehol.GeholProxy(host)
        cal = gehol_proxy.get_studentset_calendar(group_id, weeks)
        return cal
    except gehol.GeholException:
        return None

def convert_student_calendar_to_ical_string(cal):
    try:
        ical_data = convert_geholcalendar_to_ical(cal, first_monday)
        return ical_data.as_string()
    except Exception,e:
        return None


def rebuild_studentset_gehol_url(group_id):
    return "http://164.15.72.157:8080/Reporting/Individual;Student%20Set%20Groups;id;"+group_id+"?&template=Ann%E9e%20d%27%E9tude&weeks=1-14&days=1-6&periods=5-33&width=0&height=0"

def rebuild_studentset_gehol_url(group_id, weeks):
    return "http://164.15.72.157:8080/Reporting/Individual;Student%20Set%20Groups;id;"+group_id+"?&template=Ann%E9e%20d%27%E9tude&weeks="+weeks+"days=1-6&periods=5-33&width=0&height=0"

def rebuild_course_gehol_url(course_mnemo):
    return "http://164.15.72.157:8080/Reporting/Individual;Courses;name;"+course_mnemo+"?days=1-6&height=0&width=0&periods=5-29&template=cours&weeks=1-36"
