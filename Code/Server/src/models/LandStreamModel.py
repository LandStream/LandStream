from google.appengine.ext import db

import logging, re

def ParseCSVLine( line ):
    
    values = list()
    pattern = re.compile(r'(^|,)"(?P<value>.*?)"(,|$)')

    result = re.search(pattern, line)
    while result:
        if result.start(0):
            values.extend( line[:result.start(0)].split(',') )
        values.append( result.group('value') )
        line = line[result.end(0):]
        result = re.search(pattern, line)
    values.extend( line.split(',') )
    
    return values

class LandStreamModel(db.Model):
    
    #def __init__(self):
        #self.Headers = list()
        
    Headers = None
    
    @staticmethod
    def ValidateCSVHeader(instance, header):
        dictionary = instance.to_dict()

        headers = list()
        header = header.strip().split(',')
           
        i = 0
        for token in header:
            headers.append(token)
            
            if token != "ID" and not dictionary.has_key(token):
                print ("NOT VALID -- dictionary doesn't have: ", token)
                return False
            i += 1
        
        LandStreamModel.Headers = headers
        return True
       
  
    def to_dict(self):
        return dict([(p, unicode(getattr(self, p))) for p in self.properties()])
    
    def CSVHeader(self):
        dictionary = self.to_dict()
        header = 'ID,'
        for key in dictionary:
            header += key + ','
        return header
        
        
    def ToCSV(self):
        dictionary = self.to_dict()
        
        csv = str(self.key().id()) + ','
        for key in dictionary:
            csv += str(dictionary[key]) + ','   
        return csv         
    
    def ValidateCSVHeader1(self, header):
        dictionary = self.to_dict()

        headers = list()
        header = header.strip().split(',')
        
        #logging.debug ("keys: ",repr(dictionary.keys()))
        #logging.debug ("header: ", repr(header))
        
        i = 0
        for token in header:
            headers.append(token)
            
            if token != "ID" and not dictionary.has_key(token):
                print ("NOT VALID -- dictionary doesn't have: ", token)
                return None
            i += 1
 
        #self.Headers = headers
        return headers
    
    #instance is just a hax...hopefully there is a better way to do this in python
    #@staticmethod
#    def FromCSV(instance, csvFile):
#        if LandStreamModel.ValidateCSVHeader(instance, csvFile.readline()):
#            while 1:
#                line = csvFile.readline()
#                if not line:
#                    break
                
        
        
#    def FromCSV(self, csvFile):
#        logging.debug("FROMCSV")
#        headers = self.ValidateCSVHeader(csvFile.readline())
#        #logging.debug(headers)
# 
#        if headers is None: 
#            return False
#        
#        while 1:
#            line = csvFile.readline()
#            logging.debug( line )
#            if not line:
#                break
#            values = line.split(",")
#            i = 0
#            for val in values:
#                if headers[i] != "ID":
#                    print headers[i], val, type(getattr(self,headers[i]))
#                    setAttr(getattr(self,headers[i]), val )
#                i += 1
#                
#        return True
    
    def FromCSV(self, line):
        print line, '\n'
        values = ParseCSVLine( line )
        print repr(values), '\n'
        i = 0
        for val in values:
            print i
            if LandStreamModel.Headers[i] != "ID":
                print LandStreamModel.Headers[i], val, type(getattr(self,LandStreamModel.Headers[i]))
                setAttr(getattr(self,LandStreamModel.Headers[i]), val )
            i += 1
        print '\n'

                
def setAttr( attr, val ):
    if val == "":
        val = None
    try:
        attr=val
    except ValueError:
        try:
            attr=int(val)
        except ValueError:
            try:
                attr=float(val)
            except:
                return False
    return True
                
                
                
        
        
                
            
        
        
        