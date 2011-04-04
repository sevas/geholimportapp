import sys
sys.path.append('./dependencies')
import logging
from gehol.converters.csvwriter import to_csv
from gehol.converters.rfc5545icalwriter import convert_geholcalendar_to_ical
import gehol
import conf

host = conf.SCIENTIA_BACKEND_HOST
first_monday = conf.FIRST_MONDAY

def get_calendar(course_mnemonic):
    gehol_proxy = gehol.GeholProxy(host)
    try:
        return gehol_proxy.get_course_calendar(course_mnemonic, conf.ALL_YEAR_WEEKSPAN)
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
    return get_student_calendar(group_id, conf.Q1_WEEKSPAN)



def get_student_q2_calendar(group_id):
    return get_student_calendar(group_id, conf.Q2_WEEKSPAN)



def get_student_jan_calendar(group_id):
    return get_student_calendar(group_id, conf.JANUARY_EXAMS_WEEKSPAN)



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




def rebuild_studentset_gehol_url(group_id, weeks):
    return conf.GEHOL_STUDENTSET_URL_TEMPLATE % (groupd_id, weeks)



def rebuild_course_gehol_url(course_mnemo):
    return conf.GEHOL_COURSE_URL_TEMPLATE % course_mnemo
