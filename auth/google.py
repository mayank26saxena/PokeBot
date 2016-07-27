from gpsoauth import perform_master_login, perform_oauth

ANDROID_ID = '9774d56d682e549c'
SERVICE = 'audience:server:client_id:848232511240-7so421jotr2609rmqakceuu1luuq0ptb.apps.googleusercontent.com'
APP = 'com.nianticlabs.pokemongo'
CLIENT_SIG = '321187995bc7cdc2b5fc91b11a96e2baa8602c62'


class Google():
    '''
    Allows for Google login
    '''

    def get_auth_provider(self):
        return 'google'

    def get_access_token(self, username, password):
        r1 = perform_master_login(username, password, ANDROID_ID)
        r2 = perform_oauth(username, r1.get('Token', ''), ANDROID_ID, SERVICE, APP, CLIENT_SIG)
        return r2.get('Auth')
