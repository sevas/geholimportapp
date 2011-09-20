__author__ = 'sevas'

from BeautifulSoup import BeautifulSoup
from geholexceptions import *


TYPE_TO_DESCR = {
    'THE':u'Theorie',
    'EXE':u'Exercices'
}

def convert_type_to_description(type_mnemo):
    if type_mnemo in TYPE_TO_DESCR:
        return TYPE_TO_DESCR[type_mnemo]
    else:
        return type_mnemo


DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
def convert_day_to_string(day_index):
    assert day_index < 7
    return DAYS[day_index]

    
class BaseEvent(object):
    def __init__(self, **kwargs):
        """
        BaseEvent defines the interface for an event that will
        be serialized in an iCal file.

        We only keep here the data relating to the time at which
        the event will occur.

        The summary, organizer, location and description are
        dependent on the type of calendar you're handling, it is thus
        your responsability to subclass BaseEvent and override the properties.

        """
        self.weeks = kwargs['weeks']
        self.day = kwargs['day']
        self.start_time = kwargs['start_time']
        self.stop_time = kwargs['stop_time']
        self.location = kwargs['location']
        self.organizer = kwargs['organizer']

    @property
    def summary(self):
        return NotImplementedError


    @property
    def description(self):
        return NotImplementedError


    def __repr__(self):
        return u"<%s object taking place on %s between %s and %s>" % ( self.__class__.__name__,
                                                                       convert_day_to_string(self.day),
                                                                       self.start_time.strftime('%H:%M'),
                                                                       self.stop_time.strftime('%H:%M'),
                                                                    )


class BaseCalendar(object):
    def __init__(self):
        self.events = []
        
    @property
    def name(self):
        raise NotImplementedError


    @property
    def description(self):
        raise NotImplementedError


    @staticmethod
    def _is_file_type_object(f):
        return hasattr(f, 'read')


    def has_events(self):
        return len(self.events)


    def _guess_query_error(self, html_content):
        if self._find_error_400(html_content):
            raise GeholPageNotFoundException(u"Gehol returned Error 400. This can happen for non-existent pages")
        raise UnknowErrorException(u"The fetched data is not a course calendar page. Check your query URL")


    def _find_error_400(self, html_content):
        soup = BeautifulSoup(html_content)
        error_header = soup.findAll(name="h1")
        if error_header:
            h1_tag = error_header[0]
            return h1_tag.contents[0].replace(" ", "") == u'400BadRequest'
        return False

