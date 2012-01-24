from google.appengine.ext import db

class LandStreamModel(db.Model):
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
    