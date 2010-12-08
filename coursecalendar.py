import urllib
import re
from datetime import datetime, timedelta
from BeautifulSoup import BeautifulSoup
from utils import split_weeks, convert_time


class CourseCalendar(object):
    '''Loads events for a given course'''
    def __init__(self, host, mnemo):
        self.host = host
        self.mnemo = mnemo
        self.events = []
        self.url = self._build_query_url()
        self.metadata = {}


    def load_events(self):
        html_content = self._get_html_content()
        self.metadata = self._extract_header(html_content)
        self.events = self._extract_table(html_content)



    def _build_query_url(self):
        params = urllib.urlencode({'template': 'cours', 'weeks': '1-31',
                                   'days': '1-6', 'periods':'5-29',
                                   'width':0,'height':0})
        url = '%s/Reporting/Individual;Courses;name;%s?%s'%(self.host, self.mnemo, params)
        return url


    def _get_html_content(self):
        try:
            html_page = urllib.urlopen(self.url)
            html_content = html_page.read()
            return html_content
        except:
            raise ValueError('Could not get html content for course : %s [%s]' % (self.mnemo,self.url))
    

    def _extract_header(self, html):
        '''parse html page to find global informations'''
        soup = BeautifulSoup(html)
        bTag = soup.find('td',text=re.compile('Horaire'))
        head = {}
        head['mnemo'] = bTag.split(':')[1].split('-')[0].lstrip()
        head['title'] = bTag.split(':')[1].split('-')[1].lstrip()
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
            if n==0:
                n = n_rows[no_line]
                day = day + 1
                current_time = -1
            else:
                current_time = 0
            n = n-1
            slots = line.findAll(name='td',recursive=False)
            for s in slots:
                cell = s.findAll(name='table',recursive=False)
                # event found
                if len(cell)>1:
                    event = {}
                    event['no_line'] = no_line
                    event['day'] = day
                    event['start'] = hours[current_time]
                    #duration in hours is extract from the colspan
                    event['duration'] = int(s['colspan'])
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
                    current_time = current_time + 1
        #now event are ready for export
        return event_list


