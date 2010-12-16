import httplib
import re
from datetime import datetime, timedelta
from BeautifulSoup import BeautifulSoup
from utils import split_weeks, convert_time

class CourseNotFoundException(Exception):
    pass

class UnknowErrorException(Exception):
    pass

class CourseCalendar(object):
    '''Loads events for a given course'''

    def __init__(self, markup):
        if self._is_file_type_object(markup):
            markup = markup.read()
        self.html_content = markup
        self.events = []
        self.metadata = {}

        self._load_events()


    @staticmethod
    def _is_file_type_object(f):
        return hasattr(f, 'read')

    def __repr__(self):
        return "{Mnemo : %s   Title : %s   Tutor : %s   Type : %s    (%d events)}" % (self.metadata['mnemo'],
               self.metadata['title'],
               self.metadata['tutor'],
               self.metadata['type'],
               len(self.events))


    def _load_events(self):
        try:
            self.metadata = self._extract_header(self.html_content)
            self.events = self._extract_table(self.html_content)
        except AttributeError:
            self._guess_query_error(self.html_content)

            conn.request("GET", self.url, headers = headers)
            response = conn.getresponse()

            print response.status, response.reason
            html_content = response.read()

            print html_content
            conn.close()


    def _extract_header(self, html):
        '''parse html page to find global informations'''
        soup = BeautifulSoup(html)
        bTag = soup.find('td',text=re.compile('Horaire'))
        head = {'mnemo': bTag.split(':')[1].split('-')[0].lstrip(),
                'title': bTag.split(':')[1].split('-')[1].lstrip(),
                'tuto': None,
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
        hours_line = lines[0].findAll(name='td',recursive=False)
        hours = []
        for h in hours_line[1:]:
            hours.append(convert_time(h.string))
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
                day = day + 1
                current_time = -1
            else:
                current_time = 0
            n -= 1
            slots = line.findAll(name='td',recursive=False)
            for s in slots:
                cell = s.findAll(name='table',recursive=False)
                # event found
                if len(cell)>1:
                    event = {'no_line': no_line,
                             'day': day,
                             'start': hours[current_time],
                             'duration': int(s['colspan'])
                    }
                    #duration in hours is extract from the colspan
                    #compute end time (1 colspan=1/2 hour)
                    delta = timedelta(hours=event['duration']/2)
                    event['end'] = hours[current_time]+delta
                    td = cell[0].tr.findAll(name='td',recursive=False)
                    # Gehol weeks when the event occurs
                    event['weeks'] = split_weeks(td[0].contents[0].string)
                    # location
                    event['location'] = td[1].contents[0].string
                    if event['location'] is None:
                        event['location'] = ''
                    # activity
                    event['type'] = cell[1].tr.td.contents[0].string
                    current_time = current_time + event['duration']
                    event_list.append(event)
                else:
                    current_time += 1
        #now event are ready for export
        return event_list

    
    def _guess_query_error(self, html_content):
        if self._find_error_400(html_content):
            raise CourseNotFoundException("Gehol returned Error 400. This can happen for non-existent courses")
        raise UnknowErrorException("The fetched data is not a course calendar page. Check your query URL")

    
    def _find_error_400(self, html_content):
        soup = BeautifulSoup(html_content)
        error_header = soup.findAll(name="h1")
        if error_header:
            h1_tag = error_header[0]
            return h1_tag.contents[0].replace(" ", "") == u'400BadRequest'
        return False

    
