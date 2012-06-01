from __future__ import with_statement
from models.LandStreamModel import CSVLandStreamModel
from google.appengine.ext import db
# The following choice lists are used for input restriction for certain properties of the OilGasLease
# class.  At some point it may be beneficial to move these values into the datastore and use a lookup
# instead, however this should work fine for the time being.

instrumentTypeChoices = ['Amendment','Correction','Extension','Lease','Memo','Option','Release']
activityChoices = ['Active','Drilling','Expired','Extended','Inactive','Option','Pending','Primary Term','Terminated','Unknown']
depthClauseChoices = ['Bore hole only','Deepest formation','Deepest producing formation','Depth penetrated','Producing formations']

# OilGasLease definition

def FromCSV( csvFile ):
    if OilGasLease.ValidateCSVHeader(OilGasLease(), csvFile.readline()):
        while 1:
            line = csvFile.readline()
            if not line:
                break
            lease = OilGasLease()
            try:
                lease.FromCSV(line)
            except:
                print "Unable to create a OilGasLease from: ", line, " Error: ", sys.exc_info()[0]
            else:
                lease.put()
    
class OilGasLease(CSVLandStreamModel):
    
    # Basic lease info
    parentOGL = db.SelfReferenceProperty()
    instrumentID   = db.StringProperty(multiline=False)
    instrumentType = db.StringProperty(default='Lease', multiline=False, choices=instrumentTypeChoices)
    activity = db.StringProperty(default='Unknown', multiline=False, choices=activityChoices)
    state = db.StringProperty(multiline=False)
    county = db.StringProperty(default='', multiline=False)
    book = db.StringProperty(default='', multiline=False)
    page = db.StringProperty(default='', multiline=False)
    lessor = db.StringProperty(multiline=True)
    lessee = db.StringProperty(multiline=True)
    filePath = db.StringProperty(default='', multiline=False)
    fileName = db.StringProperty(default='', multiline=False)
    
    # Gross acres are stored here, but all other tract info is in separate entity
    gross_ac = db.FloatProperty()
    
    # Lease details
    royalty = db.FloatProperty()
    documentDate = db.DateProperty()
    effectiveDate = db.DateProperty()
    filingDate = db.DateProperty()
    termMonths = db.IntegerProperty()
    termOptionMonths = db.IntegerProperty(default=0)
    extensionMonths = db.IntegerProperty(default=0)
    extensionBonus = db.FloatProperty()
    
    # Clauses    
    depthClauseType = db.StringProperty(multiline=False, choices=depthClauseChoices)
    depthClauseAdjustment = db.IntegerProperty(default=0)
    pughClause = db.BooleanProperty(default=False)
    depthLimitation = db.BooleanProperty(default=False)
    subjectToPooling = db.BooleanProperty(default=False)
    subjectToPoolingOrderNo = db.StringProperty(multiline=False)
    cessationOfProduction = db.BooleanProperty(default=False)
    cessationDays = db.IntegerProperty(default=0)
    shutInRoyalties = db.BooleanProperty(default=False)
    shutInRoyaltiesMonths = db.IntegerProperty(default=0)
    prefRights = db.BooleanProperty(default=False)
    prefRightsDaysPastTerm = db.IntegerProperty(default=0)
    favoredNations = db.BooleanProperty(default=False)
    grossProceeds = db.BooleanProperty(default=False)
    noSaltWaterDisposal = db.BooleanProperty(default=False)
    surfaceProvisions = db.BooleanProperty(default=False)
    otherProvisions = db.BooleanProperty(default=False) 
    
    #lessor address
    lessorAddress = db.StringProperty(multiline=True)
    lessorCity    = db.StringProperty(multiline=False)
    lessorState   = db.StringProperty(multiline=False)
    lessorZip     = db.StringProperty(multiline=False)
    lessorCountry = db.StringProperty(multiline=False)
    
    
    def __str__(self):
        return self.key().name()
        #try:
        #    return self.county + ', ' + self.book + '/' + self.page + ', ' + self.instrumentType
        #except:
        #    return 'unset OilGasLease'

from models.DocImage import DocImage
from models.Tract import Tract
from models.ZipFileModel import ZipFileModel
from google.appengine.ext import blobstore
from google.appengine.api import files

import zipfile, zlib, StringIO



#def 

def WriteTempImageFile( stream ):
    blob = files.blobstore.create( _blobinfo_uploaded_filename='ImageTemp' )
    with files.open(blob, 'a') as f:
        f.write(stream.getvalue())
                
    files.finalize(blob)
    return files.blobstore.get_blob_key(blob) 
    

def StitchTempFiles( zipFileModel, blobKeys ):
    
    
    blob = files.blobstore.create( mime_type='application/zip', _blobinfo_uploaded_filename='LandStreamData.zip')
        
    
    with files.open(blob, 'a') as f:
        for blobKey in blobKeys: 
            key = blobstore.BlobKey(blobKey)
            
            tempZipFile = zipfile.ZipFile(  )
            
            f.write()
            blobstore.BlobInfo(key ).delete()
                
    files.finalize(blob)
    zipFileModel.blob = files.blobstore.get_blob_key(blob) 
    
    
    
    
def CreateZipFile( date, zipFileKey ):
                        
    #leases = OilGasLease.all().filter("date >", date)
    try:
        zipFileModel = ZipFileModel.get( db.Key(zipFileKey) )
        zipFileModel.status = 'running'
        zipFileModel.put()
        
        stream = StringIO.StringIO() 
        zipFile = zipfile.ZipFile( stream, 'w', compression=zipfile.ZIP_DEFLATED )
        
        leases = OilGasLease.all()
        
        if date:
            leases = leases.filter('date >', date)
    
        s = OilGasLease.ToCsv(leases)
        zipFile.writestr( "OilGasLease.csv", s.getvalue() )
       
        tracts = list()
        tempFiles = list()
        count = 0
        try:
            for lease in leases:
                tracts.extend( lease.Tracts )
                if count % 100 == 0:
                    zipFileModel.status = str(count)
                    zipFileModel.put()    
                count += 1
                
        except db.Timeout:
            leases = OilGasLease.all()
            if date:
                leases = leases.filter('date >', date)
                
            for lease in leases.run( offset=count ):
                tracts.extend( lease.Tracts )
                if csvOnly == False:
                    DocImage.WriteToZip(lease.Images, zipFile)
                
                if count % 100 == 0:
                    zipFileModel.status = str(count)
                    zipFileModel.put()
                count += 1
                

        zipFileModel.status = 'writing Tract data to zipfile'
        zipFileModel.put()
        s = Tract.ToCsv(tracts)
        zipFile.writestr( "Tracts.csv", s.getvalue())
        zipFile.close()
        
        blob = files.blobstore.create( mime_type='application/zip', _blobinfo_uploaded_filename='LandStreamData.zip')
        
        zipFileModel.status = 'writing zip file to blobstore'
        zipFileModel.put()
        with files.open(blob, 'a') as f:
            stream.seek(0)
            while True:
                buf=stream.read(2048)
                if buf=="": 
                    break
                f.write(buf)
                
        files.finalize(blob)
        zipFileModel.blob = files.blobstore.get_blob_key(blob) 
        zipFileModel.status = 'done'
        zipFileModel.put()
    except Exception, detail:
        zipFileModel.status = repr(detail)
        zipFileModel.put()
        
            
        