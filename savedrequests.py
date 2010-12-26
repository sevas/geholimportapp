from google.appengine.ext import db


class PreviousRequest(db.Model):
    author = db.UserProperty()
    content = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)


class PreviousStudentSetRequests(db.Model):
    title = db.StringProperty(multiline=False)
    url = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)
