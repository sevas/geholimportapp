from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
from StringIO import StringIO


def to_ical(head,events,first_monday):
    '''export events into iCal format
    the file is returned as a string
    first_monday corresponds to the monday date of week 1 in Gehol
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

    #        cal_event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=UTC))
    #        cal_event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC))
    #        event['uid'] = '20050115T101010/27346262376@mxm.dk'
    #        event.add('priority', 5)

            cal.add_component(cal_event)

    return cal.as_string()



class IcalWriter(object):
    """
    Simple ical writer, compatible with rfc 5545 (although not extensively)
    """

    provider = 'https://bitbucket.org/odebeir/geholimport'
    version = '2.0'

    def __init__(self):
        self.name = ""
        self.description = ""
        self.summary = ""
        self.start_date = ""
        self.events = []



    def to_string(self):
        out = StringIO()
        out.write("BEGIN:VCALENDAR")
        out.write("VERSION:%s" % self.version)
        out.write("PRODID:%s" % self.provider)

        out.write("X-WR-CALNAME:%s" % self.name)
        out.write("X-WR-CALDESC:%s" % self.description)


        out.write("BEGIN:VTIMEZONE")
        out.write("TZID:Europe/Brussels")
        out.write("BEGIN:STANDARD")
        out.write("TZOFFSETFROM:+0100")
        out.write("TZOFFSETTO:+0100")
        out.write("DTSTART:%s" % self.start_date)
        out.write("END:STANDARD")
        out.write("END:VTIMEZONE")


        for event in self.events:
            out.write("BEGIN:VEVENT")
            out.write("DTSTAMP:20101229T213000")
            out.write("DTSTART;TZID=Europe/Brussels:20101229T213000")
            out.write("DTEND;TZID=Europe/Brussels:20101229T235900")
            out.write("SUMMARY:%s")
            out.write("DESCRIPTION:%s")
            out.write("LOCATION:%s" % event['location'])
            #out.write("GEO:5.092867;51.557655")
            out.write("END:VEVENT")

        out.write("END:VCALENDAR")



def convert_student_calendar_to_ical(student_calendar, first_monday):
    date_init = datetime.strptime(first_monday,'%d/%m/%Y')

    ical = Calendar()
    ical.add('prodid', 'https://bitbucket.org/odebeir/geholimport')
    ical.add('version', '2.0')
    ical.add('summary', student_calendar.description)
    ical.add('x-wr-calname', student_calendar.profile)
    ical.add('x-wr-caldesc', student_calendar.description)

    print "adding : %d events" % len(student_calendar.events)


    for event in student_calendar.events:
        # get some common data for all generated events
        event_summary =  "%s (%s)" % (event['title'], event['type'])
        event_organizer = event['organizer']
        event_location = event['location']
        #print 'expanding events for %s' % event_summary.encode('iso-8859-2')

        #expand to ical events
        for (i, event_week) in enumerate(event['weeks']):
            delta = timedelta(days=(event_week-1)*7+(event['day']))
            dtstart = date_init+delta + timedelta(hours = event['start_time'].hour,
                                                    minutes = event['start_time'].minute)
            dtend = date_init+delta + timedelta(hours = event['stop_time'].hour,
                                            minutes = event['stop_time'].minute)
            ical_event = Event()

            ical_event.add('summary', event_summary)
            ical_event.add('location', event_location)
            ical_event.add('dtstart', dtstart)
            ical_event.add('dtend', dtend)
            ical_event.add('description', event_organizer)

            ical.add_component(ical_event)

    return ical.as_string()



def convert_student_calendar_to_ics_rfc5545(student_calendar, first_monday):
    date_init = datetime.strptime(first_monday,'%d/%m/%Y')

    def write_line(out, line):
        out.write(line+'\r\n')


    out = StringIO()
    write_line(out, "BEGIN:VCALENDAR")
    write_line(out, "VERSION:%s" % "2.0")
    write_line(out, "PRODID:%s" % 'https://bitbucket.org/odebeir/geholimport')

    write_line(out, "X-WR-CALNAME:%s" % student_calendar.profile)
    write_line(out, "X-WR-CALDESC:%s" % student_calendar.description)

    write_line(out, "BEGIN:VTIMEZONE")
    write_line(out, "TZID:Europe/Brussels")
    write_line(out, "BEGIN:STANDARD")
    write_line(out, "TZOFFSETFROM:+0100")
    write_line(out, "TZOFFSETTO:+0100")
    write_line(out, "DTSTART:%s" % date_init.strftime("%Y%m%dT%H%M%S"))
    write_line(out, "END:STANDARD")
    write_line(out, "END:VTIMEZONE")


    for event in student_calendar.events:
        event_summary =  "%s (%s)" % (event['title'], event['type'])
        event_organizer = event['organizer']
        event_location = event['location']
        event_description = "%s [%s]" % (event_summary, event_organizer)

        for (i, event_week) in enumerate(event['weeks']):
            delta = timedelta(days=(event_week-1)*7+(event['day']))
            dtstart = date_init+delta + timedelta(hours = event['start_time'].hour,
                                                    minutes = event['start_time'].minute)
            dtend = date_init+delta + timedelta(hours = event['stop_time'].hour,
                                            minutes = event['stop_time'].minute)

            write_line(out, "BEGIN:VEVENT")
            write_line(out, "DTSTAMP:%s" %  dtstart.strftime("%Y%m%dT%H%M%S"))
            write_line(out, "DTSTART;TZID=Europe/Brussels:%s" % dtstart.strftime("%Y%m%dT%H%M%S"))
            write_line(out, "DTEND;TZID=Europe/Brussels:%s" % dtend.strftime("%Y%m%dT%H%M%S"))
            write_line(out, "SUMMARY:%s" % event_summary)
            write_line(out, "DESCRIPTION:%s" % event_description)
            write_line(out, "LOCATION:%s" % event_location)
            #write_line(out, "GEO:5.092867;51.557655")
            write_line(out, "END:VEVENT")

    write_line(out, "END:VCALENDAR")
    ical_string = out.getvalue()
    out.close()

    return ical_string.encode('utf-8')


def export_ical(head,events,dest_filename, first_monday):
    ical_string = to_ical(head,events,first_monday)
    fd = open(dest_filename,'w')
    fd.write(ical_string)


def write_ical_to_file(ical_data, dest_filename):
    fd = open(dest_filename,'w')
    fd.write(ical_data)