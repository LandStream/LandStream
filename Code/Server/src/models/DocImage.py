from google.appengine.ext import db
from models.OilGasLease import OilGasLease
from models.LandStreamModel import LandStreamModel
from google.appengine.ext import blobstore
        
class DocImage(LandStreamModel):
    oilGasLease = db.ReferenceProperty(OilGasLease, collection_name='Images')

    image = blobstore.BlobReferenceProperty()
    
          
    def __str__(self):
        return self.oilGaseLease.Key().ID() + '-' + self.page
    
    
    @classmethod
    def WriteToZip(cls, items, zipFile):
        for docImage in items:
            image = docImage.image
            lease = docImage.oilGasLease                
            path = lease.state + '/' + lease.county + '/' + str(lease.filingDate.year)  + '/'

            try:
                zipFile.writestr( path + lease.fileName, blobstore.BlobReader(image.key()).read() )
            except Exception as detail:
                #log this
                pass