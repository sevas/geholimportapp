import csv, codecs, cStringIO
from datetime import datetime, timedelta
from utils import write_content_to_file

class Buffer(object):
    """Buufer claas enable to write result of the CSV class to a in memory string"""
    def __init__(self):
        self.data = ''
    def write(self,s):
        self.data = self.data + s

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def to_csv(head, events, first_monday):
    '''export events into csv format
    the file is saved under filename .csv extension must be provided 
    Google calendar import format:
    Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location,Private
    Final Exam,05/12/08,07:10:00 PM,05/12/08,10:00:00 PM,False,Two essay questions that will cover topics covered throughout the semester,"Columbia, Schermerhorn 614",True
    first_monday corresponds to the monday date of week 1 in Gehol 
    '''
    
    date_init = datetime.strptime(first_monday,'%d/%m/%Y')
    buffer = Buffer()
    writer = UnicodeWriter(buffer, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    #write header line see google help http://www.google.com/support/calendar/bin/answer.py?answer=45656
    writer.writerow(['Subject','Start Date','Start Time','End Date','End Time','All Day Event','Description','Location','Private'])
    for event in events:
        n = len(event['weeks'])
        for (i,sub) in enumerate(event['weeks']):
            subject = '%s%s (%d/%d)'%(head['mnemo'],event['type'],i+1,n)
            #add offset corresponding to week numbers for each event repetition
            delta = timedelta(days=(sub-1)*7+(event['day']))
            start_date = (date_init+delta).strftime("%d/%m/%y")
            start_time = event['start'].strftime("%I:%M:%S %p")
            end_date = start_date
            end_time = event['end'].strftime("%I:%M:%S %p")
            all_day_event = 'False'
            description = head['title']+' titulaire : '+ head['tutor']
            location = event['location']
            private = 'False'
            writer.writerow([subject,start_date,start_time,end_date,end_time,
                         all_day_event,description,location,private])

    return buffer.data

def export_csv(head,events,dest_filename, first_monday):
    csv_string = to_csv(head,events,first_monday)
    write_content_to_file(csv_string, dest_filename)