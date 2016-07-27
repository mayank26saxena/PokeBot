import base64
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_requests_session(user_agent=None):
    session = requests.session()
    session.verify = False
    if user_agent: session.headers.update({'User-Agent': user_agent})
    return session