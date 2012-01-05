from google.appengine.ext import db

class OGL(db.Model):
    book_page = db.StringProperty()
    lessor = db.StringProperty()
    lessee = db.StringProperty()