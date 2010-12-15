from gehol.coursecalendar import CourseCalendar
from gehol.csvwriter import to_csv


host = '164.15.72.157:8080'
first_monday = '20/09/2010'

def gehol2csv(course):
    cal = CourseCalendar(host, 'infoh500')
    cal.load_events()
#    csv_string = to_csv(cal.metadata, cal.events, first_monday)
##    return csv_string
#    print csv_string
    return course

#    cal = CourseCalendar(host, course)
#    cal.load_events()
#    csv_string = to_csv(cal.metadata, cal.events, first_monday)
#    print csv_string
