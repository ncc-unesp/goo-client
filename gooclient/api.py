import slumber
import requests

class GooApi():
    def __init__(self, config=None):
        if config is None:
            return None

        self.config = config
        self.api = slumber.API(self.config.api_uri)
        print self.config.api_uri

    def request_token(self):
        try:
            url = self.config.api_uri
            api = slumber.API(url, auth=(self.config.username,
                                         self.config.password))
            token = api.auth.post({})
            self.set_token(token['token'])
        except:
            return None
        return self.token

    def set_token(self, token):
        self.token = token

    def get_apps(self):
        apps = self.api.apps.get(token=self.token)
        return apps['objects']
