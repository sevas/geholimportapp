"""
This module replaces the iCalendar python module which can be found here: http://codespeak.net/icalendar/.
The main reason is that this module implements an old version of the iCalendar standard (rfc 2445).

We noticed that this version of the standard did not work well with several calendar applications. For example, we could
not add ics files generated with the old spec as live urls in Google Calendar.

This module implements a subset of the rfc 5545 standard. As we only need a flat list of events, we do not support features such as
- repeatable events
- rsvp
- probably many more

"""

__author__ = 'sevas'



from datetime import datetime, timedelta
from StringIO import StringIO


class Event(object):
    def __init__(self):
        self.summary = ""
        self.organizer = ""
        self.location = ""
        self.description = ""
        self.dtstart = None
        self.dtend = None
        self.dtstamp = None


class Calendar(object):
    def __init__(self):
        self.name = ""
        self.description = ""
        self.version = "2.0"
        self.provider = "https://bitbucket.org/odebeir/geholimport"
        self.start_date = datetime.today()
        self.events = []


    def add_event(self, event):
        self.events.append(event)


    def as_string(self):
        def write_line(out, line):
            out.write(line+'\r\n')

        out = StringIO()

        write_line(out, "BEGIN:VCALENDAR")
        write_line(out, "VERSION:%s" % self.version)
        write_line(out, "PRODID:%s" % self.provider)

        write_line(out, "X-WR-CALNAME:%s" % self.name)
        write_line(out, "X-WR-CALDESC:%s" % self.description)

        write_line(out, "BEGIN:VTIMEZONE")

        write_line(out, "TZID:Europe/Brussels")
        write_line(out, "X-LIC-LOCATION:Europe/Brussels")

        write_line(out, "BEGIN:DAYLIGHT")
        write_line(out, "TZOFFSETFROM:+0100")
        write_line(out, "TZOFFSETTO:+0200")
        write_line(out, "TZNAME:CEST")
        write_line(out, "DTSTART:19700329T020000")
        write_line(out, "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU")
        write_line(out, "END:DAYLIGHT")

        write_line(out, "BEGIN:STANDARD")
        write_line(out, "TZOFFSETFROM:+0200")
        write_line(out, "TZOFFSETTO:+0100")
        write_line(out, "TZNAME:CET")
        write_line(out, "DTSTART:19701025T030000")
        write_line(out, "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU")
        write_line(out, "END:STANDARD")

        write_line(out, "END:VTIMEZONE")

        for event in self.events:
            write_line(out, "BEGIN:VEVENT")
            write_line(out, "DTSTAMP:%s" %  event.dtstart.strftime("%Y%m%dT%H%M%S"))
            write_line(out, "DTSTART;TZID=Europe/Brussels:%s" % event.dtstart.strftime("%Y%m%dT%H%M%S"))
            write_line(out, "DTEND;TZID=Europe/Brussels:%s" % event.dtend.strftime("%Y%m%dT%H%M%S"))
            write_line(out, "SUMMARY:%s" % event.summary)
            write_line(out, "DESCRIPTION:%s" % event.description)
            write_line(out, "LOCATION:%s" % event.location)
            write_line(out, "ORGANIZER:%s" % event.organizer)
            #write_line(out, "GEO:5.092867;51.557655")
            write_line(out, "END:VEVENT")


        write_line(out, "END:VCALENDAR")
        ical_string = out.getvalue()
        out.close()

        return ical_string


def convert_geholcalendar_to_ical(gehol_calendar, first_monday):
    date_init = datetime.strptime(first_monday,'%d/%m/%Y')

    cal = Calendar()
    cal.description = gehol_calendar.description
    cal.name = gehol_calendar.name
    cal.start_date = date_init

    for event in gehol_calendar.events:
        ical_event = Event()
        # get some common values for the events we will generate next
        event_summary =  "%s (%s)" % (event['title'], event['type'])
        event_organizer = event['organizer']
        event_location = event['location']
        event_descr = "%s [%s]" % (event_summary, event_organizer)

        for (i, event_week) in enumerate(event['weeks']):
            delta = timedelta(days=(event_week-1)*7+(event['day']))
            dtstart = date_init+delta + timedelta(hours = event['start_time'].hour,
                                                  minutes = event['start_time'].minute)
            dtend = date_init+delta + timedelta(hours = event['stop_time'].hour,
                                                minutes = event['stop_time'].minute)

            ical_event = Event()
            ical_event.summary = event_summary
            ical_event.location = event_location
            ical_event.description = event_descr
            ical_event.organizer = event_organizer

            ical_event.dtstamp = dtstart
            ical_event.dtstart = dtstart
            ical_event.dtend = dtend

            cal.add_event(ical_event)

    return cal