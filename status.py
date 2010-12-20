

from google.appengine.ext import db

class GeholStatus(db.Model):
    is_down = db.BooleanProperty(False)
    last_checked = db.DateTimeProperty(auto_now=True)

def create_unique_entry():
    unique = GeholStatus(key_name='unique')
    unique.put()
    return unique


def get_unique_status_entry():
    #status_entry = db.GqlQuery("SELECT * FROM GeholStatus WHERE __key__ = 'unique'")
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
    status_entry.is_down = down
    status_entry.put()