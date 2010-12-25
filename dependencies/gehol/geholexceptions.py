__author__ = 'sevas'


class GeholException(Exception):
    pass

class GeholPageNotFoundException(GeholException):
    pass

class UnknowErrorException(GeholException):
    pass
