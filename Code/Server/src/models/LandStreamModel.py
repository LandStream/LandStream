from google.appengine.ext import db

import logging, re, datetime, sys, csv, StringIO
from django.utils import simplejson as json




    
class InvalidCSVFileError(Exception):       
    def __str__(self):
        return "CSV file header is invalid"
    
class InvalidJSONError(Exception):
    def __init__(self, cls, json):
        self.cls = cls
        self.json = json
    def __str__(self):
        return 'Trying to load an object of type  from invalid JSON: '
    
    def __repr__(self):
        return 'Trying to load an object of type {0}s from invalid JSON: {1}s'.format( repr(self.cls), repr(self.json)) 
        
    

    

class LandStreamModel(db.Model):
    
    date  = db.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def Count(cls):
        count = 0
        query = cls.all()
        batchCount = query.count()
        while batchCount > 0:
            count += batchCount
            batchCount = query.with_cursor(query.cursor()).count()
        
        return count

    @classmethod
    def to_dict(cls):
        return dict([(p, unicode(getattr(cls, p))) for p in cls.properties()])
     
    def GetPropertyTypeInstance(self, propName):
        for name, property in self.properties().items():
            if name==propName:
                return property
        return None
    
    def GetType(self, propName):
        t = self.GetPropertyTypeInstance(propName)
        return LandStreamModel.__DB_PROPERTY_INFO[type(t)]

    __DB_PROPERTY_INFO = {

        db.StringProperty           :"String",
        db.ByteStringProperty       :"ByteString",
        db.BooleanProperty          :"Boolean",
        db.IntegerProperty          :"Integer",
        db.FloatProperty            :"Float",
        db.DateTimeProperty         :"DateTime",
        db.DateProperty             :"Date",
        db.TimeProperty             :"Time",
        db.ListProperty             :"List",
        db.StringListProperty       :"StringList",
        db.ReferenceProperty        :"Reference",
        db.SelfReferenceProperty    :"SelfReference",
        db.UserProperty             :"User",
        db.BlobProperty             :"Blob",
        db.TextProperty             :"Text",
        db.CategoryProperty         :"Category",
        db.LinkProperty             :"Link",
        db.EmailProperty            :"Email",
        db.GeoPtProperty            :"GeoPt",
        db.IMProperty               :"IM",
        db.PhoneNumberProperty      :"PhoneNumber",
        db.PostalAddressProperty    :"PostalAddress",
        db.RatingProperty           :"Rating"
    }

class CSVLandStreamModel(LandStreamModel):
    
        
    Headers = None
    
    @classmethod
    def ValidCSVFile(cls, file):
           
        for row in csv.reader([file.readline()]):
            header = set(row)
            break
        
        file.seek(0)
        
        header.remove('ID')
        
        dictionary = cls.to_dict()
        
        return len(header.difference(set(dictionary))) == 0
           
    @classmethod
    def FromCSVFile(cls, file):
        
        items = list()
        
        if cls.ValidCSVFile(file):
            reader = csv.DictReader( file )
        else:
            raise InvalidCSVFileError()
            
        for row in reader:
            
            try:
                newItem = cls( key_name=row['ID'] )
                del row['ID']
                
                for key, value in row.items():
                    newItem.setAttr( key, value )
                items.append(newItem)
            except:
                print row
                raise
        return items           
    
    def toDict(self):
        return dict([(p, unicode(getattr(self, p)).encode('utf-8')) for p in self.properties()])
    
        #return dict([(p, unicode(getattr(self, p))) for p in self.properties()])
    
    @classmethod
    def FromJSON(cls, jsonObj):
        
        jsonDict = json.loads( jsonObj )
        classDict = cls.to_dict()
        
        jsonSet = set(jsonDict)
        jsonSet.remove('ID')
        diff = jsonSet.difference(set(classDict))
        if len(diff) > 0:
            raise InvalidJSONError(cls, jsonObj)
        
        try:
            newItem = cls( key_name=str(jsonDict['ID']) )
            del jsonDict['ID']
                
            for key, value in jsonDict.items():
                newItem.setAttr( key, value )
            return newItem
        except:
            print jsonObj
            raise 
                

    @classmethod
    def ToCsv(cls, items):
        
        header = cls.to_dict()
        header['ID'] = 0
        header = header.keys()
        
        stream = StringIO.StringIO()
        
        writer = csv.DictWriter(stream, fieldnames=header)
        #write the header
        writer.writerow(dict((fieldName,fieldName) for fieldName in header))
        
        #write all the items
        for item in items:
            itemDict = item.toDict()
            itemDict['ID'] = item.key().name()
            writer.writerow(itemDict)

        return stream
        
    @classmethod
    def CSVHeader(cls, stream):
        header = cls.to_dict()
        header['ID'] = 0
        header = header.keys()
                
        writer = csv.DictWriter(stream, fieldnames=header)
  
        #write the header
        writer.writerow(dict((fieldName,fieldName) for fieldName in header))  
        
        return writer     
        
        
    
    def toCSV(self, writer):
        
        itemDict = self.toDict()
        itemDict['ID'] = self.key().name()
        writer.writerow(itemDict)
        
        

                
    def setAttr( self, name, val ):
        
        #first try to load the value straight...this works when loading stuff from a valid python representation (i.e. from deserialized JSON)
        try:
            #if type(val) == type(str):
            #    val = val.strip()
                
            setattr(self, name, val )
        
        #if that doesn't work, try all the special case bidness.
        except:
        
            type = self.GetType(name)
            
            try:
                if val == "" or val == None:
                    setattr(self,name,None)
                    return
                
                if type == 'Boolean':
                    if val == "TRUE" or val == '1':
                        setattr(self, name, True)
                    elif val == "FALSE" or val == '0':
                        setattr(self, name, False)
                 
                elif type == 'Integer':
                    setattr(self, name, int(val))
                  
                
                elif type == 'String':          
                    val = val.decode('Windows-1252').strip()   
                    setattr(self, name, val)
                  
                    
                elif type == 'Float':            
                    setattr(self, name, float(val))
                                   
                elif type == 'Date':
                    try:
                        temp = datetime.datetime.strptime( val, "%m/%d/%Y %H:%M:%S")
                    except ValueError:
                        temp = datetime.datetime.strptime( val, '%Y-%m-%d' )
                    d = datetime.date(temp.year, temp.month, temp.day)
                    setattr(self, name, d)
                    return True
                
                           
            except Exception , detail:
                print 'Name: ', name
                print 'Type: ', type
                print "Error: ", sys.exc_info()[0]
                print "Detail: ", detail
                raise
        
            #raise SetAttrError( self, name, val )
                
                
class SetAttrError(Exception):
    def __init__(self, obj, name, value):
        self.obj = obj
        self.name = name
        self.value = value
    def __str__(self):
        return "Failed to set attribute: %s with value: %s on object: %s " % (str(self.name), str(self.value), str(self.obj))                 
        
        

        
        