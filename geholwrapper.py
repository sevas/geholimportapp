import sys
sys.path.append('./dependencies')
import logging
from gehol.converters.rfc5545icalwriter import convert_geholcalendar_to_ical
import gehol
import conf

def get_calendar(course_mnemonic, weekspan):
    gehol_proxy = gehol.GeholProxy(conf.SCIENTIA_BACKEND_HOST)
    try:
        return gehol_proxy.get_course_calendar(course_mnemonic, weekspan)
    except gehol.GeholException:
        return None




def convert_course_calendar_to_ical(cal):
    ical = convert_geholcalendar_to_ical(cal, conf.FIRST_MONDAY)
    return ical.as_string()



def get_student_q1_calendar(group_id):
    return get_student_calendar(group_id, conf.Q1_WEEKSPAN)



def get_student_q2_calendar(group_id):
    return get_student_calendar(group_id, conf.Q2_WEEKSPAN)



def get_student_exam_calendar(group_id, weeks):
    return get_student_calendar(group_id, weeks)


def get_student_jan_calendar(group_id):
    return get_student_calendar(group_id, conf.JANUARY_EXAMS_WEEKSPAN)


def get_student_june_calendar(group_id):
    return get_student_calendar(group_id, conf.JUNE_EXAMS_WEEKSPAN)


def get_student_sept_calendar(group_id):
    return get_student_calendar(group_id, conf.SEPTEMBER_EXAMS_WEEKSPAN)


def get_student_calendar(group_id, weeks):
    try:
        gehol_proxy = gehol.GeholProxy(conf.SCIENTIA_BACKEND_HOST)
        cal = gehol_proxy.get_studentset_calendar(group_id, weeks)
        return cal
    except gehol.GeholException:
        return None



def convert_student_calendar_to_ical_string(cal):
    try:
        ical_data = convert_geholcalendar_to_ical(cal, conf.FIRST_MONDAY)
        return ical_data.as_string()
    except Exception,e:
        return None



def get_professor_q1_calendar(staff_member_id):
    return get_professor_calendar(staff_member_id, conf.Q1_WEEKSPAN)



def get_professor_q2_calendar(staff_member_id):
    return get_professor_calendar(staff_member_id, conf.Q2_WEEKSPAN)



def get_professor_calendar(staff_member_id, weeks):
    try:
        gehol_proxy = gehol.GeholProxy(conf.SCIENTIA_BACKEND_HOST)
        cal = gehol_proxy.get_professor_calendar(staff_member_id, weeks)
        return cal
    except gehol.GeholException:
        return None


def convert_professor_calendar_to_ical_string(cal):
    try:
        ical_data = convert_geholcalendar_to_ical(cal, conf.FIRST_MONDAY)
        return ical_data.as_string()
    except Exception,e:
        return None



def make_studentset_gehol_url(group_id, weeks):
    host = conf.SCIENTIA_BACKEND_HOST
    template_url = "http://%s/Reporting/Individual;Student%%20Set%%20Groups;id;%s?&template=Ann%%E9e%%20d%%27%%E9tude&weeks=%s&days=1-6&periods=5-33&width=0&height=0"
    return template_url % (host, group_id, weeks)



def make_course_gehol_url(course_mnemo, weeks=conf.Q1_WEEKSPAN):
    host = conf.SCIENTIA_BACKEND_HOST
    template_url =  "http://%s/Reporting/Individual;Courses;name;%s?&days=1-6&height=0&width=0&periods=5-29&template=cours&weeks=%s"
    return template_url % (host, course_mnemo, conf.Q1_WEEKSPAN)



def make_professor_gehol_url(staff_member_id, weeks):
    host = conf.SCIENTIA_BACKEND_HOST
    template_url = "http://%s/Reporting/Individual;Staff;id;%s?&template=Professeur&weeks=%s&days=1-6&periods=1-30&width=0&height=0"
    return template_url % (host, staff_member_id, weeks)