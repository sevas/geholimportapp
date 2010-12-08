from coursecalendar import CourseCalendar
from csvwriter import to_csv


host = 'http://164.15.72.157:8080'
first_monday = '20/09/2010'

def gehol2csv(course):
#    cal = CourseCalendar(host, course)
#    cal.load_events()
#    csv_string = to_csv(cal.metadata, cal.events, first_monday)
#    return csv_string
    test()
    return '----'


from google.appengine.api import urlfetch
import urllib

def test():
    url = 'http://164.15.72.157:8080/Reporting/Individual;Courses;name;INFOH500?days=1-6&height=0&width=0&periods=5-29&template=cours&weeks=1-31'
    enc_url = 'http://164.15.72.157:8080/Reporting/Individual%3BCourses%3Bname%3BINFOH500?days=1-6&height=0&width=0&periods=5-29&template=cours&weeks=1-31'
    enc_url = 'http://164.15.72.157:8080/Reporting/Individual;Courses;name;INFOH500'
    enc_url = 'http://164.15.72.157:8080/Reporting/Individual?name=INFOH500&days=1-6&height=0&width=0&periods=5-29&template=cours&weeks=1-31'
    html_page = urllib.urlopen(enc_url)
    html_content = html_page.read()
    print html_content

    result = urlfetch.fetch(enc_url)
    print result,result.status_code
    print result.content

    if result.status_code == 200:
        print 'CONTENT:' , result.content
    else:
        print 'problem with [%s]'%enc_url