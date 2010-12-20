
import logging
from google.appengine.ext import db

class GeholStatus(db.Model):
    is_down = db.BooleanProperty()
    last_checked = db.DateTimeProperty(auto_now=True)

def create_unique_entry():
    logging.info("Creating unique GeholStatus datastore entry")
    unique = GeholStatus(key_name='unique')
    unique.is_down = True
    unique.put()
    return unique


def get_unique_status_entry():
    logging.info("Getting Gehol status from datastore")
    status_entry = GeholStatus.get_by_key_name('unique')
    if not status_entry:
        status_entry = create_unique_entry()

    return status_entry

def is_status_down():
    status_entry = get_unique_status_entry()
    return status_entry.is_down


def get_last_status_update():
    status_entry = get_unique_status_entry()
    return status_entry.last_checked


def set_status_down(down=True):
    status_entry = get_unique_status_entry()
    logging.info("Setting Gehol's down status to %s" % down)
    status_entry.is_down = down
    status_entry.put()