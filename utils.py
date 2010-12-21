from datetime import datetime

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



def is_course_mnemo_valid(course_mnemo):
    return course_mnemo.isalnum() and len(course_mnemo) == 8



def render_resource_notfound_page(request_handler, course_mnemo, resource_type):
    template_values = {'gehol_is_down': is_status_down(),
                       'last_status_update': get_last_status_update(),
                       'mnemo':course_mnemo,
                       'resource_type':resource_type
    }

    path = os.path.join(os.path.dirname(__file__), 'templates/resource_notfound.html')
    request_handler.response.out.write(template.render(path, template_values))