"""
Name: Jeury Mejia
Class: CS370
Date: 13/12/216
Model: major.py
"""

from ferris import BasicModel
from google.appengine.ext import ndb


class Major(BasicModel):
    college      = ndb.StringProperty();
    department   = ndb.StringProperty();
    link         = ndb.StringProperty();
    degree_level = ndb.StringProperty();
    discipline   = ndb.StringProperty();
    major_description = ndb.JsonProperty() # The full metadata of the major in JSON format
    parsed = ndb.BooleanProperty()
  
    @classmethod
    def get_majors(cls):
        """
        Retrieves all majors, ordered by discipline
        """
        return cls.query().order(cls.discipline)
      
    
    @classmethod
    def get_major_for_discipline(cls, discipline):
        return cls.query(cls.discipline==discipline)
    

    @classmethod
    def add_new(cls, form_data):
    
        new_major = Major(
      					           college      = form_data['college'],
                           department   = form_data['department'],
                           link         = form_data['link'],
        				           degree_level = form_data['degree_level'],
                           discipline   = form_data['discipline'],
                           major_description = form_data['major_description'],
                           parsed       = form_data['parsed']
        	
      					)
        
        new_major.put()
        return new_major

      