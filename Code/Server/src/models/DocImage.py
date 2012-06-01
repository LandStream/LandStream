from google.appengine.ext import db
from models.OilGasLease import OilGasLease
from models.LandStreamModel import LandStreamModel
from google.appengine.ext import blobstore
import logging
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
            path = lease.state + '/' + lease.county + '/' + str(lease.filingDate.year)  + '/' + lease.fileName
        
            zipFile.writestr( path.encode('utf-8'), blobstore.BlobReader(image.key()).read() )
