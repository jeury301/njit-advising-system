# njit-advising-system
CS370 Intro to AI Final Project - An smart system that allows students to get advised based off course history.

# Technologies

*	Google App Engine:
	*	The website is hosted on google infrastructure, and the system uses Google App Engine from the Google Cloud Platform Suite. It uses the GAE Standard Environment for Python.
	*	More info on GAE: https://cloud.google.com/appengine/
*	Ferris Framework:
	*	Ferris is web dev framework tailored specifically to GAE. More info: http://ferris-framework.appspot.com/docs/index.html

*	Python Libraries:
	* 	BeautifulSoup, used to scrape and parse some of NJIT websites to build up the database of majors and to perform the "Smart" advising.

# The System

The system is basically a database of all the courses of each major at NJIT, that acts as an expert system using historical data of the student (course & semester-wise), to provide a best estitame of the courses that needs to be taken next. The core of the system, is using the scraped data from NJIT's website and building a interal map(tree) of majors, semesters and courses.

# Check it out
http://njit-advising.appspot.com/home
