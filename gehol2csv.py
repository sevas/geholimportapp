from coursecalendar import CourseCalendar
from csvwriter import to_csv


host = 'http://164.15.72.157:8080'
first_monday = '20/09/2010'

def gehol2csv(course):
    cal = CourseCalendar(host, course)
    cal.load_events()
#    csv_string = to_csv(cal.metadata, cal.events, first_monday)
#    return csv_string
    return '********'