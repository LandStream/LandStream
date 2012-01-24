from models.LandStreamModel import LandStreamModel
from google.appengine.ext import db
# The following choice lists are used for input restriction for certain properties of the OilGasLease
# class.  At some point it may be beneficial to move these values into the datastore and use a lookup
# instead, however this should work fine for the time being.

instrumentTypeChoices = ['Amendment','Correction','Extension','Lease','Memo','Option','Release']
activityChoices = ['Active','Drilling','Expired','Extended','Inactive','Option','Pending','Primary Term','Terminated','Unknown']
depthClauseChoices = ['Bore hole only','Deepest formation','Deepest producing formation','Depth penetrated','Producing formations']

# OilGasLease definition

class OilGasLease(LandStreamModel):
    
    # Basic lease info
    parentOGL = db.SelfReferenceProperty()
    instrumentType = db.StringProperty(default='Lease', multiline=False, choices=instrumentTypeChoices)
    activity = db.StringProperty(default='Unknown', multiline=False, choices=activityChoices)
    state = db.StringProperty(multiline=False)
    county = db.StringProperty(default='', multiline=False)
    book = db.StringProperty(default='', multiline=False)
    page = db.StringProperty(default='', multiline=False)
    lessor = db.StringProperty(multiline=True)
    lessee = db.StringProperty(multiline=True)
    
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
    
    def __str__(self):
        try:
            return self.county + ', ' + self.book + '/' + self.page + ', ' + self.instrumentType
        except:
            return 'unset OilGasLease'
    
     
        