__author__ = 'sevas'

from BeautifulSoup import BeautifulSoup
from geholexceptions import *


TYPE_TO_DESCR = {
    'THE':u'Theorie',
    'EXE':u'Exercices',
    'EXC':u'Excursion',
    'GDC':u'Guidance',
    'STG':u'Stage',
    'TPR':u'Laboratoire',
    'AGD':u'Agenda',
    'GLB':u'Theorie ou Exercices',
    'PRS':u'Travaux personnels',
    'ACD':u'Activite academique'
}

def convert_type_to_description(type_mnemo):
    """
    Convert an activity type acronym into a human readable description.
    """
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
        the event will occur, as well as the organizer and location.

        The summary and description are dependent on the type of calendar
        you're handling, it is thus your responsability to subclass BaseEvent
        and override the associated object properties.

        """
        self.weeks = kwargs['weeks']
        self.day = kwargs['day']
        self.start_time = kwargs['start_time']
        self.stop_time = kwargs['stop_time']
        self.location = kwargs['location']
        self.organizer = kwargs['organizer']

    @property
    def summary(self):
        raise NotImplementedError


    @property
    def description(self):
        raise NotImplementedError


    def __repr__(self):
        return u"<%s object taking place on %s between %s and %s>" % ( self.__class__.__name__,
                                                                       convert_day_to_string(self.day),
                                                                       self.start_time.strftime('%H:%M'),
                                                                       self.stop_time.strftime('%H:%M'),
                                                                    )


class BaseCalendar(object):
    """
    Class defines the interface for a calendar that will be
    serialized by the rfc5545icalwriter module.


    The name and description properties need to be overridden
    in a subclass, as their content is different depending on the
    type of calendar you're handling.

    This class also contains a list of events, which should be subclasses
    of BaseEvent.
    """
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

