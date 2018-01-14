"""
Name: Jeury Mejia
Class: CS370
Date: 13/12/216
Controller: majors.py
"""

from ferris import Controller, scaffold, route, localize
from app.models.major import Major
from ferris.components.flash_messages import FlashMessages
from datetime import datetime, timedelta
from google.appengine.ext import deferred
from app.services import advising_services
import httplib2, logging, json, time, math

class Majors(Controller):
  
    class Meta:
        prefixes = ('cron',)
        components = (scaffold.Scaffolding,FlashMessages,)
        
    
    @route
    def list(self):
        self.context['majors'] = Major.get_majors()



    @route
    def view_major(self, major_key):
        major = self.util.decode_key(major_key).get()
        #self.meta.change_view('JSON')
        self.context['major_description'] = json.loads(major.major_description)
        self.context['discipline'] = major.discipline




    @route
    def cron_update_majors(self):
        deferred.defer(advising_services.update_majors)
        return 200

