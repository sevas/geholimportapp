__author__ = 'sevas'

from BeautifulSoup import BeautifulSoup
from geholexceptions import *

class BaseCalendar(object):
    def __init__(self):
        pass


    @property
    def name(self):
        raise NotImplementedError


    @property
    def description(self):
        raise NotImplementedError


    @staticmethod
    def _is_file_type_object(f):
        return hasattr(f, 'read')


    def _guess_query_error(self, html_content):
        if self._find_error_400(html_content):
            raise GeholPageNotFoundException("Gehol returned Error 400. This can happen for non-existent pages")
        raise UnknowErrorException("The fetched data is not a course calendar page. Check your query URL")


    def _find_error_400(self, html_content):
        soup = BeautifulSoup(html_content)
        error_header = soup.findAll(name="h1")
        if error_header:
            h1_tag = error_header[0]
            return h1_tag.contents[0].replace(" ", "") == u'400BadRequest'
        return False

