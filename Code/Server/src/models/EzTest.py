from google.appengine.ext import db


class EzTest(db.Model):
    sprop = db.StringProperty()
    iprop = db.IntegerProperty()
    
    def __str__(self):
        try:
            return self.sprop + '-' + self.iprop
        except:
            return 'oh nos!' 
    