import re
from datetime import datetime, timedelta

def convert_time(s):
    '''convert string time into datetime struct'''
    d = datetime.strptime(s,"%H:%M")
    return d


def split_weeks(weeks):
    '''split string containing weeks info into separated fields
    e.g. "1,5-7"  ---> [1,5,6,7]'''
    s = weeks.split(',')
    w = []
    for f in s:
        sf = f.split('-')
        if len(sf)>1:
            w.extend(range(int(sf[0]),int(sf[1])+1))
        else:
            w.append(int(f))
    return w


def convert_week_number_to_date(week_number, first_monday, weekday=0):
    """
    Returns a datetime object corresponding to the monday of the given week number.
    """
    assert(1 <= week_number <= 52)
    assert(0 <= weekday <= 6)
    first_gehol_year_day = datetime.strptime(first_monday, "%d/%m/%Y")
    num_days = (week_number-1) * 7 + weekday
    dt = timedelta(days = num_days)
    return first_gehol_year_day + dt
    


def convert_weekspan_to_dates(weekspan, first_monday):
    start, end = [int(i) for i in weekspan.split("-")]
    return (convert_week_number_to_date(start, first_monday),
            convert_week_number_to_date(end, first_monday, 5))



HOUR_MATCHER=re.compile("\d\d:\d\d")

def insert_halfhour_slots_and_convert_to_datetime(hour_cells):
    hours = []
    for h in hour_cells:
        if h.string and HOUR_MATCHER.match(h.string):
            hours.append(convert_time(h.string))
        else:
            last_added_hour = hours[-1]
            hours.append(datetime(last_added_hour.year,
                                       last_added_hour.month,
                                       last_added_hour.day,
                                       last_added_hour.hour, 30))
    return hours