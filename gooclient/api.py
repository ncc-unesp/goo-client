import slumber
import requests
from gooclient.output import Output

class GooApi():
    def __init__(self, config=None):
        if config is None:
            return None

        self.output = Output()
        self.config = config
        self.api = slumber.API(self.config.api_uri)

    def request_token(self):
        try:
            url = self.config.api_uri
            api = slumber.API(url, auth=(self.config.username,
                                         self.config.password))
            token = api.auth.post({})
            self.set_token(token['token'])
        except:
            return None
        return token['token']

    def set_token(self, token):
        self.token = token

    def get_apps(self, args):
        apps = self.api.apps.get(token=self.token)
        apps = apps['objects']

        fields = [ {'id': 5},
                   {'name': 30},
                   {'multi_hosts': 15},
                   {'multi_thread': 15}]

        self.output.show(fields, apps)
        return apps

    def get_jobs(self, args):
        jobs = self.api.jobs.get(token=self.token)
        jobs = jobs['objects']

        fields = [ {'id': 5},
                   {'name': 30},
                   {'priority': 15},
                   {'progress': 15}]

        self.output.show(fields, jobs)
        return jobs

    def submit_job(self, args):
        pass
