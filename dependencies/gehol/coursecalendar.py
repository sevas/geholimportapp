import httplib
import re
from datetime import datetime, timedelta, time
from BeautifulSoup import BeautifulSoup
from utils import split_weeks, insert_halfhour_slots_and_convert_to_datetime
from basecalendar import BaseCalendar, BaseEvent, convert_type_to_description

class CourseEvent(BaseEvent):
    def __init__(self, **kwargs):
        super(CourseEvent, self).__init__(**kwargs)
        self.type = kwargs['type']
        self.title = kwargs['title']

    @property
    def summary(self):
        event_type_description = convert_type_to_description(self.type)
        event_summary =  "%s (%s)" % (self.title, event_type_description)
        return event_summary


    @property
    def description(self):
        return "%s [%s]" % (self.summary, self.organizer)


    
class CourseCalendar(BaseCalendar):
    '''Loads events for a given course'''
    def __init__(self, markup):
        super(CourseCalendar, self).__init__()
        if self._is_file_type_object(markup):
            markup = markup.read()
        self.html_content = markup
        self.metadata = {}
        self._load_events()

        
    @property
    def name(self):
        return "%s - %s" % (self.metadata['mnemo'], self.metadata['title'])


    @property
    def description(self):
        return "%s - %s (%s) [%s]" % tuple([self.metadata[k] for k in ('mnemo', 'title', 'type', 'tutor')])


    def __repr__(self):
        return u"{Mnemo : %s   Title : %s   Tutor : %s   Type : %s    (%d events)}" % (self.metadata['mnemo'],
               self.metadata['title'],
               self.metadata['tutor'],
               self.metadata['type'],
               len(self.events))


    def _load_events(self):
        try:
            self.metadata = self._extract_header(self.html_content)
            self.events = self._extract_table(self.html_content)
        except AttributeError, e:
            self._guess_query_error(self.html_content)



    def _extract_header(self, html):
        '''parse html page to find global informations'''
        soup = BeautifulSoup(html)
        bTag = soup.find('td',text=re.compile('Horaire'))
        head = {'mnemo': bTag.split(':')[1].split('-')[0].lstrip(),
                'title': bTag.split(':')[1].split('-')[1].lstrip(),
                'tutor': None,
                'type': None
        }
        bTag = soup.find('td',text=re.compile('Titulaire'))
        head['tutor'] = bTag.split(':')[1].lstrip()
        head['type'] = 'course'
        return head

    
    def _extract_table(self, html):
        '''parse html page and process the calendar table
        intermediate python structure (event list) is returned'''
        soup = BeautifulSoup(html)
        tables = soup.html.body.findAll(name='table',recursive=False)
        #jump to the calendar table
        cal = tables[1]
        lines = cal.findAll(name='tr',recursive=False)
        #isolate first tab line with hours
        hours_line = lines[0].findChildren(name='td',recursive=False)[1:]
        hours = insert_halfhour_slots_and_convert_to_datetime(hours_line)
        #process all lines
        #search the number of row for that day
        n_rows = []
        for (no_line,line) in enumerate(lines[1:]):
            slots = line.findAll(name='td',recursive=False)
            #search the number of row for that day
            if slots[0].has_key('rowspan'):
                n_rows.append(int(slots[0]['rowspan']))
            else:
                n_rows.append(0)
        event_list = []
        day = -1
        n = 0
        for (no_line,line) in enumerate(lines[1:]):
            if not n:
                n = n_rows[no_line]
                day += 1
                current_time = -1
            else:
                current_time = 0
            n -= 1
            slots = line.findAll(name='td',recursive=False)
            for s in slots:
                cell = s.findAll(name='table',recursive=False)
                # event found
                if len(cell)>1:
                    event_data = { 'day': day,
                                    'start_time': hours[current_time],
                                    'duration': int(s['colspan'])
                    }
                    #duration in hours is extract from the colspan
                    #compute end time (1 colspan=1/2 hour)
                    delta = timedelta(hours=event_data['duration']/2)
                    event_data['stop_time'] = hours[current_time]+delta
                    td = cell[0].tr.findAll(name='td',recursive=False)
                    # Gehol weeks when the event occurs
                    event_data['weeks'] = split_weeks(td[0].contents[0].string)
                    # location
                    event_data['location'] = td[1].contents[0].string
                    if not event_data['location']:
                        event_data['location'] = ''
                    # activity
                    event_data['type'] = cell[1].tr.td.contents[0].string
                    current_time = current_time + event_data['duration']
                    event_data['organizer'] = ""
                    event_data['title'] = "%s - %s" % (self.metadata['mnemo'], self.metadata['title'])

                    course_event = CourseEvent(**event_data)
                    event_list.append(course_event)
                else:
                    current_time += 1
        return event_list


