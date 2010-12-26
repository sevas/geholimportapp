from datetime import datetime, timedelta
import codecs


def to_csv(head, events, first_monday):
    '''export events into csv format
    the file is saved under filename .csv extension must be provided
    Google calendar import format:
    Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location,Private
    Final Exam,05/12/08,07:10:00 PM,05/12/08,10:00:00 PM,False,Two essay questions that will cover topics covered throughout the semester,"Columbia, Schermerhorn 614",True
    first_monday corresponds to the monday date of week 1 in Gehol

    returns unicode
    '''

    date_init = datetime.strptime(first_monday,'%d/%m/%Y')
    header = [u'Subject',u'Start Date',u'Start Time',u'End Date',u'End Time',u'All Day Event',
                     u'Description',u'Location',u'Private']
    buffer = ','.join('"%s"'%d for d in header)
    buffer += '\n'
    for event in events:
        n = len(event['weeks'])
        for (i,sub) in enumerate(event['weeks']):
            subject = '%s%s (%d/%d)'%(head['mnemo'],event['type'],i+1,n)
            #add offset corresponding to week numbers for each event repetition
            delta = timedelta(days=(sub-1)*7+(event['day']))
            start_date = unicode((date_init+delta).strftime("%d/%m/%y"),'utf-8')
            start_time = unicode(event['start_time'].strftime("%I:%M:%S %p"),'utf-8')
            end_date = start_date
            end_time = unicode(event['stop_time'].strftime("%I:%M:%S %p"),'utf-8')
            all_day_event = u'False'
            description = head['title']+' titulaire : '+ head['tutor']
            location = event['location']
            private = u'False'
            data = [subject,start_date,start_time,end_date,end_time,all_day_event,description,location,private]
            line = ','.join('"%s"'%d for d in data)
            buffer += line
            buffer += '\n'
    return buffer

def export_csv(head,events,dest_filename, first_monday):
    '''write the events in a csv utf-8 encoded file'''
    csv_string = to_csv(head,events,first_monday)
    fd = codecs.open(dest_filename,mode='w',encoding='utf-8')
    fd.write(csv_string)

