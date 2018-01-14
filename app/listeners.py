"""
Central place to store event listeners for your application,
automatically imported at run time.
"""
import logging
from ferris.core.events import on
from ferris import settings
from google.appengine.api import users
from ferris.core import routing


def domain_chain(controller):
    
    #Make sure the active user's email account falls within the accepted domains.
    if controller.route.prefix == 'cron':
        return True
    
    else:
        return True
    
# example

@on('controller_before_authorization')
def inject_authorization_chains(controller, authorizations):
    authorizations.insert(0, domain_chain)

@on('controller_before_render')
def before_render(controller):
    if controller.route.prefix != 'api':
        
        current_user = str(users.get_current_user())
        
        controller.context['rd_user'] = current_user
        
        controller.context['admins'] = ['jeurymejia@gmail.com', 'jeury.mejia@gmail.com', 'jeurymejia']
        controller.context['logout_url'] = users.create_logout_url('/')  
        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        