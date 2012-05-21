# -*- coding: utf-8 -*-
#
# jQuery File Upload Plugin GAE Python Example 1.1.3
# https://github.com/blueimp/jQuery-File-Upload
#
# Copyright 2011, Sebastian Tschan
# https://blueimp.net
#
# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT
#

from __future__ import with_statement
from google.appengine.api import users
#import webapp2 as webapp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import files, images
from google.appengine.ext import blobstore, deferred
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db
from django.utils import simplejson as json
import logging, zipfile, StringIO, sys, datetime

from models.OilGasLease import OilGasLease
from models.DocImage import DocImage
from models.Tract import Tract
import dateutil.parser

##WEBSITE = 'localhost:8081/'
#WEBSITE = 'http://wenzeltech-landstream.appspot.com/'
#MIN_FILE_SIZE = 1 # bytes
#MAX_FILE_SIZE = 5000000 # bytes
#IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png|bmp|pdf)')
#ACCEPT_FILE_TYPES = IMAGE_TYPES
#THUMBNAIL_MODIFICATOR = '=s80' # max width / height
#EXPIRATION_TIME = 300 # seconds
#
#def cleanup(blob_keys):
#    blobstore.delete(blob_keys)
#
#class UploadHandler(webapp.RequestHandler):
#
#    def initialize(self, request, response):
#        logging.info("initialize")
#        super(UploadHandler, self).initialize(request, response)
#        self.response.headers['Access-Control-Allow-Origin'] = '*'
#        self.response.headers[
#            'Access-Control-Allow-Methods'
#        ] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
#    
#    def validate(self, file):
#        if file['size'] < MIN_FILE_SIZE:
#            file['error'] = 'minFileSize'
#        elif file['size'] > MAX_FILE_SIZE:
#            file['error'] = 'maxFileSize'
#        elif not ACCEPT_FILE_TYPES.match(file['type']):
#            file['error'] = 'acceptFileTypes'
#        else:
#            return True
#        return False
#    
#    def get_file_size(self, file):
#        file.seek(0, 2) # Seek to the end of the file
#        size = file.tell() # Get the position of EOF
#        file.seek(0) # Reset the file position to the beginning
#        return size
#    
#    def write_blob(self, fieldStorage, info):
#        logging.debug("write_blob")
#        blob = files.blobstore.create(
#            mime_type=info['type'],
#            _blobinfo_uploaded_filename=info['name']
#        )
#        with files.open(blob, 'a') as f:
#            fieldStorage.value = fieldStorage.file.read(65536)
#            while fieldStorage.value:
#                f.write(fieldStorage.value)
#                fieldStorage.value = fieldStorage.file.read(65536)
#        files.finalize(blob)
#        return files.blobstore.get_blob_key(blob)
#    
#    def handle_upload(self):
#        logging.debug("handle_upload")
#        results = []
#        blob_keys = []
#        for name, fieldStorage in self.request.POST.items():
#            if type(fieldStorage) is unicode:
#                continue
#            result = {}
#            result['name'] = re.sub(r'^.*\\', '',
#                fieldStorage.filename)
#            result['type'] = fieldStorage.type
#            result['size'] = self.get_file_size(fieldStorage.file)
#            if self.validate(result):
#                blob_key = str(
#                    self.write_blob(fieldStorage, result)
#                )
#                blob_keys.append(blob_key)
#                result['delete_type'] = 'DELETE'
#                result['delete_url'] = self.request.host_url +\
#                    '/?key=' + urllib.quote(blob_key, '')
#                if (IMAGE_TYPES.match(result['type'])):
#                    try:
#                        result['url'] = images.get_serving_url(blob_key)
#                        result['thumbnail_url'] = result['url'] +\
#                            THUMBNAIL_MODIFICATOR
#                    except: # Could not get an image serving url
#                        pass
#                if not 'url' in result:
#                    result['url'] = self.request.host_url +\
#                        '/' + blob_key + '/' + urllib.quote(
#                            result['name'].encode('utf-8'), '')
#            results.append(result)
#        deferred.defer(
#            cleanup,
#            blob_keys,
#            _countdown=EXPIRATION_TIME
#        )
#        return results
#    
#    def options(self):
#        pass
#        
#    def head(self):
#        pass
#    
#    def get(self):
#        if not users.get_current_user():
#            self.redirect(users.create_login_url("/"))
#            return
#        logging.debug("GET")
#        f = open( 'index.html' )
#        self.response.out.write( f.read() )
#    
#    def post(self):
#        logging.debug("POST")
#        if (self.request.get('_method') == 'DELETE'):
#            return self.delete()
#        s = json.dumps(self.handle_upload(), separators=(',',':'))
#        redirect = self.request.get('redirect')
#        if redirect:
#            return self.redirect(str(
#                redirect.replace('%s', urllib.quote(s, ''), 1)
#            ))
#        if 'application/json' in self.request.headers.get('Accept'):
#            self.response.headers['Content-Type'] = 'application/json'
#        self.response.out.write(s)
#
#    def delete(self):
#        logging.debug("DELETE")
#        blobstore.delete(self.request.get('key') or '')


class RPC:
    def DeleteAll(self):
        print "DELETED!"
        db.delete(OilGasLease.all())
        db.delete(DocImage.all())
        db.delete(Tract.all())
            
        query = blobstore.BlobInfo.all()
        blobs = query.fetch(400)
        if len(blobs) > 0:
            for blob in blobs:
                blob.delete()
                
                
    def LoadOGL(self, data, type):
        if type == 'csv':
            if data != None:
                leases = OilGasLease.FromCSVFile(data.file)
                for lease in leases:
                    lease.put()
                #from JSON
        elif type == 'json':
            if data != None:
                lease = OilGasLease.FromJSON(data)
                if lease:
                    lease.put()
    
    def LoadTract(self, data, request):
        type = request.get('datatype')
        oglID = request.get('oglID')
        if type == 'csv':
            if data != None:
                tracts = Tract.FromCSVFile(data.file)
                for tract in tracts:
                    tract.put()
        elif type == 'json':
            if data != None:
                lease = OilGasLease.get_by_key_name( oglID )
                if lease:   
                    tract = Tract.FromJSON(data)
                    tract.oilGasLease = lease
                    if tract:
                        tract.put()
                else:
                    raise LeaseMissingLoadError(oglID)
        
    def LoadImage(self, data, request):
        oglID = request.get('oglID')
        lease = OilGasLease.get_by_key_name( oglID )
        if lease:                       
            blob = files.blobstore.create( mime_type='application/pdf',
                _blobinfo_uploaded_filename=lease.fileName,
                        
            )
            with files.open(blob, 'a') as f:
                data.value = data.file.read(65536)
                while data.value:
                    f.write(data.value)
                    data.value = data.file.read(65536)
            files.finalize(blob)
            key = files.blobstore.get_blob_key(blob) 
                    
            image = DocImage( oilGasLease = lease, image=key )
            image.put()        
        else:
            raise LeaseMissingLoadError(oglID)
        
#class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
class ImageDownloadHandler(webapp.RequestHandler):
    def get(self):
        
        if GhettoAuth(self.request) == False:
            self.error(404)
            
        if not users.get_current_user():
            self.redirect(users.create_login_url("/"))
            return        
        stream = StringIO.StringIO()
        zipFile = zipfile.ZipFile( stream, 'w' )
        
        #get all the blobs in the blobstore and write them into the ZipFile
        all = DocImage.all()
        
        DocImage.WriteToZip(all, zipFile)

        zipFile.close()
        
        self.response.headers['Content-Type'] ='application/zip'
        self.response.headers['Content-Disposition'] = 'attachment; filename="images.zip"'

        stream.seek(0)
        
        while True:
            buf=stream.read(2048)
            if buf=="": 
                break
            self.response.out.write(buf)
        stream.close()

def GhettoAuth(request):
    if request.get('user') != 'oseberg' or request.get('pwd') != 'int1sci':
        return False
    return True   
        
class DataDownloadHandler(webapp.RequestHandler):
    def post(self):
        
        if GhettoAuth(self.request) == False:
            self.error(404)
            return
 
        
        date = dateutil.parser.parse(self.request.get('date'))
                        
        leases = OilGasLease.all().filter("date >", date)
        stream = StringIO.StringIO()
        s = OilGasLease.ToCsv(leases)
        zipFile = zipfile.ZipFile( stream, 'w' )
            
        zipFile.writestr( "OilGasLease.csv", s.getvalue() )
        
        tracts = list()
        images = list()
        for lease in leases:
            tracts.extend( lease.Tracts )
            images.extend( lease.Images )
        
        s = Tract.ToCsv(tracts)
        zipFile.writestr("Tracts.csv", s.getvalue())
        DocImage.WriteToZip(images, zipFile)
        
        zipFile.close()
            
        self.response.headers['Content-Type'] ='application/zip'
        self.response.headers['Content-Disposition'] = 'attachment; filename="LandStreamData.zip"'
            
        stream.seek(0)
        while True:
            buf=stream.read(2048)
            if buf=="": 
                break
            self.response.out.write(buf)
        stream.close()
                
            
            
            
            
       
            
class LeaseMissingLoadError(Exception):
    def __init__(self, leaseID):
        self.leaseID = leaseID
    
    def __str__(self):
        return "Trying to load an object that depends on missing lease ID:", self.leaseID

 
#    def get(self):
#        if not users.get_current_user():
#            self.redirect(users.create_login_url("/"))
#            return        
#        stream = StringIO.StringIO()
#        zipFile = zipfile.ZipFile( stream, 'w' )
#        
#        #get all the OilGasLeases in the datastore
#        leases = db.GqlQuery("SELECT * FROM OilGasLease")
#        lease = leases.get()
#        
#        csvData = ''
#        if lease != None:
#            header = lease.CSVHeader()
#            csvData += header
#            
#            for lease in leases:
#                csvData += '\n' + lease.ToCSV()
#
#        logging.debug( csvData )     
#        zipFile.writestr( "OilGasLease.csv", csvData )
#        zipFile.close()
#        
#        self.response.headers['Content-Type'] ='application/zip'
#        self.response.headers['Content-Disposition'] = 'attachment; filename="data.zip"'
#        
#        stream.seek(0)
#        while True:
#            buf=stream.read(2048)
#            if buf=="": 
#                break
#            self.response.out.write(buf)
#        stream.close()


        
                
        
class DataUploadHandler(webapp.RequestHandler):
    
    def __init__(self):
        
        self.RPC = RPC()
        
    def get_file_size(self, file):
        file.seek(0, 2) # Seek to the end of the file
        size = file.tell() # Get the position of EOF
        file.seek(0) # Reset the file position to the beginning
        return size
    
    def post(self):
        
        if GhettoAuth(self.request) == False:
            self.error(404)
            
            return
              
        data = None
        #there must be a better way??
        for name, value in self.request.POST.items():
            if name == 'data':
                data = value       
        
        method = self.request.get('action')

        if method == 'delete':
            self.RPC.DeleteAll()
            self.response.headers['Content-Type'] = 'application/json'
            result = { 'success' : True, 'msg' : '' }
            self.response.out.write( json.dumps( result ) )
            return
            
        elif method == 'load':
            
            try:
                if self.request.get('type') == 'ogl':
                    self.RPC.LoadOGL(data, self.request.get('datatype'))
                    
                elif self.request.get('type') == 'tract':
                    self.RPC.LoadTract(data, self.request )                
                    
                elif self.request.get('type') == 'image':
                    self.RPC.LoadImage(data, self.request )
            except Exception as detail:
                
                logging.debug( "FAILED:" + repr(detail))
                self.response.headers['Content-Type'] = 'application/json'
                result = { 'success' : False, 'msg' : repr(detail) }
                self.response.out.write(json.dumps( result ))
                return
                
        
        self.response.headers['Content-Type'] = 'application/json'
        result = { 'success' : True, 'msg' : '' }
        self.response.out.write(json.dumps( result ))
        return
        
            #
            #self.response.out.write( 'oh hi!')
                
            #print dir(data)
            #self.get_file_size( data.FieldStorage.file )
                #logging.debug( type(value) )
            #logging.debug( 'FILE SIZE: ' + self.get_file_size(self.request.get('data').file) )

app = webapp.WSGIApplication(
    [

        ('/download_data', DataDownloadHandler),
        ('/upload_data', DataUploadHandler)
    ],
    debug=True
)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(app)

if __name__ == "__main__":
    main()
    

