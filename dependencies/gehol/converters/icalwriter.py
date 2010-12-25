from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
from utils import write_content_to_file

def to_ical(head,events,first_monday):
    '''export events into iCal format
    the file is returned as a string
    first_monday is the date of the monday in week 1 in Gehol (in the DD/MM/YYYY format)
    '''
    date_init = datetime.strptime(first_monday,'%d/%m/%Y')

    cal = Calendar()
    cal.add('prodid', 'https://bitbucket.org/odebeir/geholimport')
    cal.add('version', '2.0')
    cal.add('summary', head['title'])
    cal.add('x-wr-calname', "%s - %s"  % (head['mnemo'], head['title']))
    cal.add('x-wr-caldesc', "%s - %s (%s)" % (head['mnemo'], head['title'], head['tutor']))

    for event in events:
        n = len(event['weeks'])
        for (i,sub) in enumerate(event['weeks']):
            summary = '%s%s (%d/%d)'%(head['mnemo'],event['type'],i+1,n)
            #add offset corresponding to week numbers for each event repetition
            delta = timedelta(days=(sub-1)*7+(event['day']))
            dtstart = date_init+delta + timedelta(hours = event['start'].hour,
                                                  minutes = event['start'].minute)
            dtend = date_init+delta + timedelta(hours = event['end'].hour,
                                                minutes = event['end'].minute)

            organizer = head['title']+' titulaire : '+ head['tutor']
            location = event['location']

            cal_event = Event()

            cal_event.add('summary', summary)
            cal_event.add('dtstart', dtstart)
            cal_event.add('dtend', dtend)
            cal_event['location'] = vText(location)
            cal_event['organizer'] = vText(organizer)

            cal.add_component(cal_event)

    return cal.as_string()


def export_ical(head,events,dest_filename, first_monday):
    ical_string = to_ical(head,events,first_monday)
    write_content_to_file(ical_string, dest_filename)