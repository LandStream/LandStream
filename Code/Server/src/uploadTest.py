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
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import files, images
from google.appengine.ext import blobstore, deferred
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db
from django.utils import simplejson as json
import re, urllib, logging, zipfile, StringIO

from models.OilGasLease import OilGasLease
from models.Tract import Tract

#WEBSITE = 'localhost:8081/'
WEBSITE = 'http://wenzeltech-landstream.appspot.com/'
MIN_FILE_SIZE = 1 # bytes
MAX_FILE_SIZE = 5000000 # bytes
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png|bmp|pdf)')
ACCEPT_FILE_TYPES = IMAGE_TYPES
THUMBNAIL_MODIFICATOR = '=s80' # max width / height
EXPIRATION_TIME = 300 # seconds

def cleanup(blob_keys):
    blobstore.delete(blob_keys)

class UploadHandler(webapp.RequestHandler):

    def initialize(self, request, response):
        logging.info("initialize")
        super(UploadHandler, self).initialize(request, response)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers[
            'Access-Control-Allow-Methods'
        ] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
    
    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'minFileSize'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'maxFileSize'
        elif not ACCEPT_FILE_TYPES.match(file['type']):
            file['error'] = 'acceptFileTypes'
        else:
            return True
        return False
    
    def get_file_size(self, file):
        file.seek(0, 2) # Seek to the end of the file
        size = file.tell() # Get the position of EOF
        file.seek(0) # Reset the file position to the beginning
        return size
    
    def write_blob(self, fieldStorage, info):
        logging.debug("write_blob")
        blob = files.blobstore.create(
            mime_type=info['type'],
            _blobinfo_uploaded_filename=info['name']
        )
        with files.open(blob, 'a') as f:
            fieldStorage.value = fieldStorage.file.read(65536)
            while fieldStorage.value:
                f.write(fieldStorage.value)
                fieldStorage.value = fieldStorage.file.read(65536)
        files.finalize(blob)
        return files.blobstore.get_blob_key(blob)
    
    def handle_upload(self):
        logging.debug("handle_upload")
        results = []
        blob_keys = []
        for name, fieldStorage in self.request.POST.items():
            if type(fieldStorage) is unicode:
                continue
            result = {}
            result['name'] = re.sub(r'^.*\\', '',
                fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                blob_key = str(
                    self.write_blob(fieldStorage, result)
                )
                blob_keys.append(blob_key)
                result['delete_type'] = 'DELETE'
                result['delete_url'] = self.request.host_url +\
                    '/?key=' + urllib.quote(blob_key, '')
                if (IMAGE_TYPES.match(result['type'])):
                    try:
                        result['url'] = images.get_serving_url(blob_key)
                        result['thumbnail_url'] = result['url'] +\
                            THUMBNAIL_MODIFICATOR
                    except: # Could not get an image serving url
                        pass
                if not 'url' in result:
                    result['url'] = self.request.host_url +\
                        '/' + blob_key + '/' + urllib.quote(
                            result['name'].encode('utf-8'), '')
            results.append(result)
        deferred.defer(
            cleanup,
            blob_keys,
            _countdown=EXPIRATION_TIME
        )
        return results
    
    def options(self):
        pass
        
    def head(self):
        pass
    
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url("/"))
            return
        logging.debug("GET")
        f = open( 'index.html' )
        self.response.out.write( f.read() )
    
    def post(self):
        logging.debug("POST")
        if (self.request.get('_method') == 'DELETE'):
            return self.delete()
        s = json.dumps(self.handle_upload(), separators=(',',':'))
        redirect = self.request.get('redirect')
        if redirect:
            return self.redirect(str(
                redirect.replace('%s', urllib.quote(s, ''), 1)
            ))
        if 'application/json' in self.request.headers.get('Accept'):
            self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(s)

    def delete(self):
        logging.debug("DELETE")
        blobstore.delete(self.request.get('key') or '')

#class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
class ImageDownloadHandler(webapp.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url("/"))
            return        
        stream = StringIO.StringIO()
        zipFile = zipfile.ZipFile( stream, 'w' )
        
        #get all the blobs in the blobstore and write them into the ZipFile
        all = blobstore.BlobInfo.all()
        
        filenameIndex = 0
        for blobInfo in all:
            logging.debug(blobInfo.filename)       
            #zipFile.writestr( "test" + str(filenameIndex), blobstore.BlobReader(blobInfo).read() )
            try:
                zipFile.writestr( blobInfo.filename, blobstore.BlobReader(blobInfo).read() )
            except Exception:
                self.response.headers['Content-Type'] = 'text/plain'
                self.response.out.write( blobInfo.filename)
                return

            filenameIndex += 1
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
        
class DataDownloadHandler(webapp.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url("/"))
            return        
        stream = StringIO.StringIO()
        zipFile = zipfile.ZipFile( stream, 'w' )
        
        #get all the OilGasLeases in the datastore
        leases = db.GqlQuery("SELECT * FROM OilGasLease")
        lease = leases.get()
        
        csvData = ''
        if lease != None:
            header = lease.CSVHeader()
            csvData += header
            
            for lease in leases:
                csvData += '\n' + lease.ToCSV()
           
        logging.debug( csvData )     
        zipFile.writestr( "OilGasLease.csv", csvData )
        zipFile.close()
        
        self.response.headers['Content-Type'] ='application/zip'
        self.response.headers['Content-Disposition'] = 'attachment; filename="data.zip"'
        
        stream.seek(0)
        while True:
            buf=stream.read(2048)
            if buf=="": 
                break
            self.response.out.write(buf)
        stream.close()
        
class DataUploadHandler(webapp.RequestHandler):
    def get_file_size(self, file):
        file.seek(0, 2) # Seek to the end of the file
        size = file.tell() # Get the position of EOF
        file.seek(0) # Reset the file position to the beginning
        return size
    
    def get(self):  
        self.response.out.write('<html><body>')
       
        self.response.out.write("""
                  <form action="/upload_data" enctype="multipart/form-data" method="post">
                    <div><label>OilGasLease:</label></div>
                    <div><input type="file" name="OilGasLease"/></div>
                    <div><label>Tracts:</label></div>
                    <div><input type="file" name="Tracts"/></div>
                    <div><label>DocImage:</label></div>
                    <div><input type="file" name="DocImage"/></div>
                    <div><input type="submit" value="Upload .CSV Files" /></div>
                  </form>
                </body>
              </html>""")    
        #wtf
    def post(self):
      
#        logging.debug("DataUploadHandler.post")
#        

        for name, fieldStorage in self.request.POST.items():
            
#            logging.debug( repr(type(fieldStorage)) )
            if type(fieldStorage) is unicode:
                continue
            result = {}
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            
            if name == "OilGasLease":
                if OilGasLease.ValidateCSVHeader(OilGasLease(), fieldStorage.file.readline()):
                    print repr(OilGasLease.Headers)
                    while 1:
                        line = fieldStorage.file.readline()
                        if not line:
                            break
                        lease = OilGasLease()
                        lease.FromCSV(line)
                
                #lease = OilGasLease()
                #print str(lease)
                #lease.FromCSV(fieldStorage.file)
#                logging.debug( str(lease))
                #logging.debug( lease.lessee + " " + lease.lessor )
            
            #header = fieldStorage.file.readline()
            
            
            #while fieldStorage.file:
            #    logging.debug( fieldStorage.file.readline())
                
            #logging.debug( name )
            
        
    
#    
#        
#        
       
            
            
#        self.send_blob(blobInfo.key(), save_as=blob.filename)
        
        
        
#        if not blobstore.get(key):
#            self.error(404)
#        else:
#            # Cache for the expiration time:
#            self.response.headers['Cache-Control'] =\
#                'public,max-age=%d' % EXPIRATION_TIME
#            self.send_blob(key, save_as=filename)

app = webapp.WSGIApplication(
    [
        ('/', UploadHandler),
        #('/([^/]+)/([^/]+)', DownloadHandler)
        ('/download_images', ImageDownloadHandler),
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
    

