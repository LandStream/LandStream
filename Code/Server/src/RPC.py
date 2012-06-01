from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from protorpc import messages
from protorpc import remote
from protorpc.webapp import service_handlers

from models.OilGasLease import OilGasLease
from models.DocImage import DocImage
from models.Tract import Tract

class GetImageRequest(messages.Message):
  id = messages.StringField(1, required=True)

class GetImageResponse(messages.Message):
  ogl = messages.StringField(1, required=True)

class RPCService(remote.Service):
    
  @remote.method(GetOGLRequest, GetOGLResponse)
  def GetImage(self, request):
      
      lease = OilGasLease.get_by_key_name( request.id )
      if lease:
          lease.toCSV()
          
      
    return GetOGLResponse(hello='Hello there, %s!' %
                         request.my_name)

service_mappings = service_handlers.service_mapping(
    [('/rpc', RPCService),
    ])

application = webapp.WSGIApplication(service_mappings)

def main():
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()