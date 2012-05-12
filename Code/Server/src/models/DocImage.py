from google.appengine.ext import db
from models.OilGasLease import OilGasLease
from models.LandStreamModel import LandStreamModel

        
class DocumentImage(LandStreamModel):
    oilGasLease = db.ReferenceProperty(OilGasLease)
    #page = db.IntegerProperty(required=True)
    #fileName
    image = db.BlobProperty()
    
    #imageHash = db.IntegerProperty()
    date  = db.DateTimeProperty(auto_now_add=True)
        
    def __str__(self):
        return self.oilGaseLease.Key().ID() + '-' + self.page