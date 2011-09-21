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
    assert(1 <= week_number <= 36)
    assert(0 <= weekday <= 6)
    first_gehol_year_day = datetime.strptime(first_monday, "%d/%m/%Y")
    num_days = (week_number-1) * 7 + weekday
    dt = timedelta(days = num_days)
    return first_gehol_year_day + dt
    


def convert_weekspan_to_dates(weekspan, first_monday):
    start, end = [int(i) for i in weekspan.split("-")]
    return (convert_week_number_to_date(start, first_monday),
            convert_week_number_to_date(end, first_monday, 5))



def capitalize_word(word):
    if not word:
        return ""
    elif len(word) == 1:
        return word[0].upper()
    else:
        return word[:1].upper() + word[1:]

def capitalize_hyphenated_name(name):
    fragments = name.split("-")
    return u"-".join([capitalize_word(w) for w in fragments])



def capitalize_name(name):
    pass



def as_readable_name(lecturers):
    fragments = lecturers.split(',')
    pairs = [fragments[2*i, 2*i+1] for i in len(fragments) / 2]
    for (first, last) in pairs:
        capitalized_last_name = last_name.lower()
        readable_name = u"%s %s" % (first_name, last_name)