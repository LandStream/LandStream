from google.appengine.ext import db
from google.appengine.ext import blobstore

class ZipFileModel(db.Model):
    
    blob = blobstore.BlobReferenceProperty()
    date  = db.DateTimeProperty(auto_now_add=True)
    status = db.StringProperty()
    