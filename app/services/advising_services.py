"""
Name: Jeury Mejia
Class: CS370
Date: 13/12/216
Services: advising_services.py
"""

from google.appengine.api import memcache, mail, users
from google.appengine.ext import deferred
from ferris import ndb, localize, settings
import httplib2, logging, json, time, math
from datetime import datetime, date, timedelta
from app.models.major import Major
from google.appengine.api import urlfetch
import requests
from bs4 import BeautifulSoup
import urllib, re, json, logging, mimetypes, base64

urlfetch.set_default_fetch_deadline(45)

def update_majors():
    try:
        ndb.delete_multi(Major.get_majors().iter(keys_only = True))
        all_majors = get_majors()

        logging.info("All majors extracted: "+str(len(all_majors)))

        for major in all_majors:
            logging.info(major['discipline']+" was created")
            deferred.defer(create_major, major)                               
	
    except Exception as e:
        logging.error(e)        
        raise deferred.PermanentTaskFailure()	

def create_major(obj):
    try:
        major_info = parse_url(obj['link'])
        parsed = True
        
        if (len(major_info['first_year']['first_semester']) == 0 and
           len(major_info['first_year']['second_semester']) == 0 and
           len(major_info['second_year']['first_semester']) == 0 and
           len(major_info['second_year']['second_semester']) == 0 and 
           len(major_info['third_year']['first_semester']) == 0 and
           len(major_info['third_year']['second_semester']) == 0 and
           len(major_info['fourth_year']['first_semester']) == 0 and
           len(major_info['fourth_year']['second_semester']) == 0):

           parsed = False

        obj['major_description'] = json.dumps(major_info)
        obj['parsed'] = parsed
        Major.add_new(obj)
    except Exception as e:
        logging.error(e)        
        raise deferred.PermanentTaskFailure()


def get_majors():
    url_subjects = "https://courseschedules.njit.edu/index.aspx?semester=2017s"

    url_majors = "http://www5.njit.edu/academics/degreeprograms/"

    page_content = urllib.urlopen(url_majors).read()

    #page = requests.get(url_majors)
    soup = BeautifulSoup(page_content, "html.parser")

    links = soup.find_all('tr')

    final_info_majors = []
    major_info = []
    for link in links:
        sub_info = link.find_all('td')

        major = {}
        if len(sub_info) > 0 :

            if str(sub_info[2].text) == "Bachelor's":

                link = ""

                if len(sub_info[3].find_all('a')) > 0:
                    link = str(sub_info[3].find_all('a')[0].get('href'))
                elif sub_info[4]:
                    if len(sub_info[4].find_all('a')):
                        link = str(sub_info[4].find_all('a')[0].get('href'))

                major = {
                    'college': str(sub_info[0].text),
                    'department':str(sub_info[1].text),
                    'degree_level':str(sub_info[2].text),
                    'link':link,
                    'discipline':str(sub_info[3].text)
                }
        
                final_info_majors.append(major)

    newlist = sorted(final_info_majors, key=lambda k: k['discipline']) 

    return newlist


def get_majors_description():
    all_majors = get_majors()

    major_descriptions = []
    
    for major in all_majors:
        if major['link'] != "":
            super_info = {
                'discipline':major['discipline'],
                'major_info':parse_url(str(major['link']))
            }
            major_descriptions.append(super_info)
    
    return major_descriptions   



def parse_url(url_major):
    
    major_info = {'first_year':{
                                'first_semester':[],
                                'second_semester':[]
                                },
                      'second_year':{
                                'first_semester':[],
                                'second_semester':[]
                          },
                      'third_year':{
                                'first_semester':[],
                                'second_semester':[]
                          },
                      'fourth_year':{
                                'first_semester':[],
                                'second_semester':[]
                          }
                    }
    try:
        page_content = urllib.urlopen(url_major).read()
        soup = BeautifulSoup(page_content, "html.parser")

        all_tables = soup.find_all('table')

        
        if len(all_tables) != 0:

            all_rows = all_tables[0].find_all('tr')

            if len(all_rows) < 10 and len(all_tables) > 1:
                all_rows = all_tables[1].find_all('tr')

            messages = []
            year_selected = ""
            semester_selected = ""

            for row in all_rows:
                classes = [str(class_) for class_ in row.get('class')]
                if "plangridyearhdr" in classes:
                    
                    if len(row.find_all('th'))!=0:

                        if str(row.find_all('th')[0].text) == "First Year":
                            year_selected = "first_year"
                        elif str(row.find_all('th')[0].text) == "Second Year":
                            year_selected = "second_year"
                        elif str(row.find_all('th')[0].text) == "Third Year":
                            year_selected = "third_year"
                        elif str(row.find_all('th')[0].text) == "Fourth Year":
                            year_selected = "fourth_year"
                    
                elif "plangridtermhdr" in classes:
                    if len(row.find_all('th'))!=0:
                        if str(row.find_all('th')[0].text) == "1st Semester":
                            semester_selected = "first_semester"
                        elif str(row.find_all('th')[0].text) == "2nd Semester":
                            semester_selected = "second_semester"

                elif "even" in classes or "odd" in classes:

                    course_information = row.find_all('td')
                        
                    if len(course_information) > 2:
                        course_info = {
                            'code':str(unicode(str(course_information[0].text.encode("utf-8")), errors='ignore')),
                            'title':str(unicode(str(course_information[1].text.encode("utf-8")), errors='ignore')),
                            'credits':str(unicode(str(course_information[2].text.encode("utf-8")), errors='ignore'))
                        }
                        
                        if course_info['code'] != '':
                            if course_info['credits'] == '':
                                course_info['credits'] = '0'
                            major_info[year_selected][semester_selected].append(course_info)

        return major_info
    except Exception as e:
        major_info['error'] = [str(e)]
        return major_info