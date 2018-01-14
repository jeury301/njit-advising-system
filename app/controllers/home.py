"""
Name: Jeury Mejia
Class: CS370
Date: 13/12/216
Controller: home.py
"""

from ferris import Controller, scaffold, route, localize, route_with
from ferris.components.flash_messages import FlashMessages
from datetime import datetime, timedelta
from ferris import BasicModel
from google.appengine.api import users, memcache, mail, search
from lxml import html, etree
import requests
from bs4 import BeautifulSoup
import urllib, re
from google.appengine.api import urlfetch
import logging
import sys
from app.services import advising_services
from app.models.major import Major
import httplib2, logging, json, time, math, urllib

urlfetch.set_default_fetch_deadline(45)

class Home(Controller):
    
    class Meta:
        components = (scaffold.Scaffolding,FlashMessages,)
        Model = (BasicModel)
    
    @route
    def list(self):
        pass	
    	

    @route
    def scrape(self):
        self.meta.change_view('JSON')
        self.context['data'] = advising_services.get_majors_description()


    @route_with('/<location_slug>')
    def njit_copy(self, location_slug):
        #page = requests.get(')
        #tree = html.fromstring(page.content)
        url_majors = "https://www.nypl.org/locations/%s"%location_slug

        page_content = urllib.urlopen(url_majors).read()

        #page = requests.get(url_majors)
        #soup = BeautifulSoup(page_content, "html.parser")
        pretty = BeautifulSoup(page_content).prettify()

        return pretty


    @route
    def advisement(self):
        self.context['info'] = "Getting Advised!"



    @route
    def advance_advisement(self):
        FlashMessages(self).flash('If you are seeing this message, this guy did not finish his AI project!!!! -_-', level='danger')
        return self.redirect(self.uri(action='advisement'))



    @route
    def express_advisement(self, value):
        cache_key = "advisement"
        suggestions_key = "suggestion_key"

        standing_map = {
                    'Lower Freshman':['first_year', 'first_semester', None],
                    'Upper Freshman':['first_year', 'second_semester', 0],
                    'Lower Sophomore':['second_year', 'first_semester', 1],
                    'Upper Sophomore':['second_year', 'second_semester', 2],
                    'Lower Junior':['third_year', 'first_semester', 3],
                    'Upper Junior':['third_year', 'second_semester', 4],
                    'Lower Senior':['fourth_year', 'first_semester', 5],
                    'Upper Senior':['fourth_year', 'second_semester', 6]}

        sts =   [['first_year', 'first_semester'], 
                ['first_year', 'second_semester'],
                ['second_year', 'first_semester'],
                ['second_year', 'second_semester'],
                ['third_year', 'first_semester'],
                ['third_year', 'second_semester'],
                ['fourth_year', 'first_semester'],
                ['fourth_year', 'second_semester']]

        if int(value) == 0:
            majors = [str(major.discipline) for major in Major.get_majors()]

            left_over = memcache.get(cache_key)

            if memcache.get(suggestions_key):
                memcache.delete(suggestions_key)

            if left_over:
                memcache.delete(cache_key)

            self.context['first'] = value
            self.context['majors'] = majors
            self.context['value'] = int(value)

            if self.request.method == 'POST':
                
                container = {
                             'credits' :self.request.params['credits'], 
                             'standing':self.request.params['current_standing'],
                             'major'   :self.request.params['major']
                            }
                
                #Validation: if number of error messages >=1, this happens.
                
                validating = self.validate(container, majors)

                if len(validating)>=1:
            
                    self.context['container'] = container
                    self.context['error_messages'] = validating

                #When validation is passed, this happens.
                
                else:
                    memcache.add(key=cache_key, value=container, time=3600)
                    return self.redirect(self.uri(action='express_advisement', value=1))
        elif int(value) == 1:
            self.context['second'] = value
            self.context['value'] = int(value)

            advising_info = memcache.get(cache_key)

            if str(advising_info['standing']) == 'Lower Freshman':
                self.context['advising'] = True

                limit = 100

                if advising_info['credits']:
                    limit = int(advising_info['credits'])
                total_credits = 0

                major_description = json.loads([major for major in Major.get_major_for_discipline(str(advising_info['major']))][0].major_description)

                courses = major_description[standing_map[str(advising_info['standing'])][0]][standing_map[str(advising_info['standing'])][1]]

                final_courses = []
                
                for course in courses:
                    if (total_credits + int(course['credits'][0])) <= limit:
                        final_courses.append(course)
                        total_credits = total_credits + int(course['credits'][0])

                self.context['courses'] = final_courses
                self.context['total_credits'] = total_credits
                self.context['advising_message'] = [select.replace('_', ' ').title() if isinstance(select, str) is True else '' for select in standing_map[str(advising_info['standing'])]]

                if memcache.get(cache_key):
                    memcache.delete(cache_key)

            else:
                suggestions = memcache.get(suggestions_key)

                if suggestions:
                    memcache.delete(suggestions_key)

                major_description = json.loads([major for major in Major.get_major_for_discipline(str(advising_info['major']))][0].major_description)


                suggested_courses = major_description[sts[standing_map[str(advising_info['standing'])][2]][0]][sts[standing_map[str(advising_info['standing'])][2]][1]]

                memcache.add(key=suggestions_key, value=suggested_courses, time=3600)
                self.context['suggested_courses'] = suggested_courses

        else:
            self.context['second'] = value
            self.context['advising'] = True
            self.context['value'] = int(value)

            suggested_courses = memcache.get(suggestions_key)

            advising_info = memcache.get(cache_key)
            
            major_description = json.loads([major for major in Major.get_major_for_discipline(str(advising_info['major']))][0].major_description)

            courses = major_description[standing_map[str(advising_info['standing'])][0]][standing_map[str(advising_info['standing'])][1]]

            limit = 100

            if advising_info['credits']:
                limit = int(advising_info['credits'])
            
            total_credits = 0

            final_courses = []
            
            for course in suggested_courses:
                if str(course['title']) in self.request.params.keys():
                    if (total_credits + int(course['credits'][0])) <= limit and self.request.params[str(course['title'])] == 'no':
                        final_courses.append(course)
                        total_credits = total_credits + int(course['credits'][0])
            
            for course in courses:
                if (total_credits + int(course['credits'][0])) <= limit:
                    final_courses.append(course)
                    total_credits = total_credits + int(course['credits'][0])
            
            self.context['courses'] = final_courses
            self.context['total_credits'] = total_credits
            self.context['advising_message'] = [select.replace('_', ' ').title() if isinstance(select, str) is True else '' for select in standing_map[str(advising_info['standing'])]]
            
            if memcache.get(suggestions_key):
                memcache.delete(suggestions_key)
            

    @route
    def validate(self, container, majors):
        """
        This is the validation function for 'add' and 'edit'
        """
        error_messages = []
      
        if container['standing']=='':
            error_message = 'You must enter your current standing.'
            error_messages.append(error_message)
          
        if container['major']=='':
            error_message = 'You must enter your major.'
            error_messages.append(error_message)
        else:
            if container['major'] not in majors:
                error_message = 'Major entered was not found.'
                error_messages.append(error_message)
        
        if container['credits']:
            if int(container['credits']) < 3 or int(container['credits']) > 21:
                error_message = 'Enter number of credits between 3 and 21.'
                error_messages.append(error_message)

        return error_messages


    @route
    def advise_me(self):
        pass


        
    