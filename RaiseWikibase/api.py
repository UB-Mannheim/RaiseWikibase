import requests
from RaiseWikibase.raiser import create_bot
from RaiseWikibase.settings import Settings

"""
A simple wrapper of the Wikibase API. Just for testing.
"""

create_bot('bot')
config = Settings()
user = config.username
pwd = config.password
URL = config.mediawiki_api_url


class Session:

    def __init__(self):
        self.csrftoken, self.s = self.get_csrftoken()

    def get_csrftoken(self):
        # 1. Create session
        s = requests.Session()
        headers = {'User-Agent': 'RaiseWikibase'}
        s.headers.update(headers)
        # 2. Get logintoken
        params = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"}
        r = s.get(url=URL, params=params)
        logintoken = r.json()['query']['tokens']['logintoken']
        # 3. Login with username, password and logintoken
        data = {
            "action": "login",
            "lgname": user,
            "lgpassword": pwd,
            "lgtoken": logintoken,
            "format": "json"}
        r = s.post(URL, data=data)
        if r.json()['login']['result'] != 'Success':
            print(r.json())
            raise Exception('Logging in to MW api failed for: ' + user)
        # 4. Get csrftoken
        params = {
            "action": "query",
            "meta": "tokens",
            "format": "json"}
        r = s.get(url=URL, params=params)
        csrftoken = r.json()['query']['tokens']['csrftoken']
        return csrftoken, s

    def create_text(self, title, text):
        data = {
            "action": "edit",
            "title": title,
            "text": text,
            "token": self.csrftoken,
            "format": "json"}
        r = self.s.post(URL, data=data)
        if r.json()['edit']['result'] != 'Success':
            raise Exception('Failed for: ' + title)

    def create_entity(self, entity='', maxlag=5, etype=''):
        data = {
            'action': 'wbeditentity',
            'data': entity,
            'format': 'json',
            'token': self.csrftoken,
            'maxlag': maxlag,
            'new': etype}
        r = self.s.post(URL, data=data)
        if not r.json().get('success'):
            raise Exception('Failed for: ' + str(r.json()))

