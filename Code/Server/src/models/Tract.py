from google.appengine.ext import db
from models.OilGasLease import OilGasLease
from models.LandStreamModel import CSVLandStreamModel

# Validation methods
# Note that validation methods that are used by properties in the Tract class must be
# defined prior to the definition of the Tract class itself.

def validateQuarter(quarter):
        
    if (quarter == None):
        return
    allowed = ['NE', 'NW', 'SE', 'SW']
    for s in str(quarter).upper().split(','):
        s = s.strip()
        if (not s in allowed):
            raise db.BadValueError('quarter must be a comma separated list of the following: {NE|NW|SE|SW}:' + s)

def validateSec(sec):
    
    try:
        val = int(sec)
        if val < 1 or val > 36:
            db.BadValueError('sec must be between 1-36, sec = ' + str(val) )
    except:
        raise db.BadValueError('sec must be a number, sec = ' + str(sec) )
        
    return
    
#    if (sec == None):
#        return    
#    if (len(sec) != 2):    
#        raise db.BadValueError('sec must be two characters long (e.g. 02)')    
#    if (not str(sec).isdigit()):
#        raise db.BadValueError('sec must be a number')
    
def validateTwn(twn):
    if (twn == None):
        return    
    if (len(twn) != 3):
        raise db.BadValueError('twn must be three characters long (e.g. 02N)')
    
    head = str(twn[0:2])
    tail = str(twn[2]).upper()
        
    if (not head.isdigit()):
        raise db.BadValueError('the first 2 characters of twn must be a number (e.g. 02N)')
    if (not tail in ['N', 'S']):
        raise db.BadValueError('the last character of twn must be either N or S (e.g. 02N)')

def validateRng(rng):
    if (rng == None):
        return    
    if (len(rng) != 3):
        raise db.BadValueError('rng must be three characters long (e.g. 02E)')
    
    head = str(rng[0:2])
    tail = str(rng[2]).upper()
        
    if (not head.isdigit()):
        raise db.BadValueError('the first 2 characters of rng must be a number (e.g. 02E)')
    if (not tail in ['E', 'W']):
        raise db.BadValueError('the last character of rng must be either E or W (e.g. 02E)')

# Tract class definition

class Tract(CSVLandStreamModel):
    oilGasLease = db.ReferenceProperty(OilGasLease, collection_name="Tracts")
    
    #turning off validation of quarter for now
    #quarter = db.StringProperty(multiline=False, validator=validateQuarter)
    quarter = db.StringProperty(multiline=False)
    legal = db.StringProperty(multiline=True)
    sec = db.StringProperty(multiline=False, validator=validateSec)
    sec = db.StringProperty(multiline=False)
    twn = db.StringProperty(multiline=False, validator=validateTwn)
    rng = db.StringProperty(multiline=False, validator=validateRng)
    county = db.StringProperty(multiline=False)
    meridian = db.StringProperty(multiline=False)
    
    def __str__(self):
        try:
            return self.county + ' county, ' + self.secTwnRng() + ': ' + self.legal
        except:
            return 'unset Tract' 
    
    def secTwnRng(self):
        try:
            return self.sec + '-' + self.twn + '-' + self.rng
        except:
            return 'unset Tract'
        