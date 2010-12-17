from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText



def export_ical(head,events,filename,first_monday):
    '''export events into iCal format
    the file is returned as a string
    first_monday corresponds to the monday date of week 1 in Gehol
    '''
    date_init = datetime.strptime(first_monday,'%d/%m/%Y')

    cal = Calendar()
    cal.add('prodid', 'https://bitbucket.org/odebeir/ulbcalendar2cvs')
    cal.add('version', '2.0')

    for event in events:
        n = len(event['weeks'])
        for (i,sub) in enumerate(event['weeks']):
            summary = '%s%s (%d/%d)'%(head['mnemo'],event['type'],i+1,n)
            #add offset corresponding to week numbers for each event repetition
            delta = timedelta(days=(sub-1)*7+(event['day']))
            dtstart = date_init+delta + timedelta(hours = event['start'].hour, minutes = event['start'].minute)
            dtend = date_init+delta + timedelta(hours = event['end'].hour, minutes = event['end'].minute)

            organizer = head['title']+' titulaire : '+ head['tutor']
            location = event['location']

            cal_event = Event()

            cal_event.add('summary', summary)
            cal_event.add('dtstart', dtstart)
            cal_event.add('dtend', dtend)
            cal_event['location'] = vText(location)
            cal_event['organizer'] = vText(organizer)

    #        cal_event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=UTC))
    #        cal_event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC))
    #        event['uid'] = '20050115T101010/27346262376@mxm.dk'
    #        event.add('priority', 5)

            cal.add_component(cal_event)

    return cal.as_string()
