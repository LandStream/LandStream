from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.ext.db import Key

from models.OilGasLease import OilGasLease
from models.Tract import Tract
#from models.EzTest import EzTest

class MainPage(webapp.RequestHandler):
    
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        
        ogl = OilGasLease()
        ogl.bookPage = '12/345'
        ogl.county = 'Custer'
        
        t = Tract()
        t.sec = '01'
        t.twn = '02N'
        t.rng = '03W'
        
        #ez = EzTest(id=1)        
        #ez.sprop = 'a string'
        #ez.iprop = 1
        #ez.put()
        
        ogl.put()
        t.oilGasLease = ogl
        t.put()
        
        outputString = 'a tract: ' + t.secTwnRng() + '\n' + 'a lease: ' + str(ogl)
        
        self.response.out.write(outputString)

application = webapp.WSGIApplication([('/', MainPage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
