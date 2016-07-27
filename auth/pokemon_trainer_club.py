import json
import re
import time

from utils.general import get_requests_session

LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
PTC_CLIENT_SECRET = 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR'


class PokemonTrainerClub(object):
    '''
    Allows for Pokemon Trainer Club (PTC) login
    '''

    def get_auth_provider(self):
        return 'ptc'

    def get_access_token(self, username, password):
        requests_session = get_requests_session('niantic')

        # Get LOGIN_URL page
        r = requests_session.get(LOGIN_URL)
        if r is None: raise Exception('failed to get login_url')

        # Response should be in json
        try:
            login_data = json.loads(r.content)
        except Exception as e:
            print 'response from get login_url unexpected, retrying'
            time.sleep(1)
            return self.login_ptc(username, password)

        # Attempt to log in
        data = {
            'lt': login_data['lt'],
            'execution': login_data['execution'],
            '_eventId': 'submit',
            'username': username,
            'password': password,
        }
        r1 = requests_session.post(LOGIN_URL, data=data)

        # If log in was successful, we should get ticket
        ticket = None
        try:
            ticket = re.sub('.*ticket=', '', r1.history[0].headers['Location'])
        except:
            raise Exception('failed to get ticket, ' + r1.json().get('errors', ''))

        # Exchange the ticket for an access_token
        data1 = {
            'client_id': 'mobile-app_pokemon-go',
            'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
            'client_secret': PTC_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'code': ticket,
        }
        r2 = requests_session.post(LOGIN_OAUTH, data=data1)
        access_token = re.sub('&expires.*', '', r2.content)
        access_token = re.sub('.*access_token=', '', access_token)

        return access_token