from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError, HttpServerError
import requests
import sys
import datetime
import htmlentitydefs, re
import os
import ConfigParser
import json
from output import Output

CURRENT_API_VERSION = "v1"

def translate_gooapi_to_gooclient_exception(f):
    def _f(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HttpClientError as e:
            print e.code, e.content
            sys.exit()
        except HttpServerError as e:
            print e.content
            sys.exit()
    return _f

class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[template]\n'
    def readline(self):
        if self.sechead:
            try: return self.sechead
            finally: self.sechead = None
        else: return self.fp.readline()

class GooClient():
    def __init__(self, config=None):
        if config is None:
            return None

        self.output = Output()
        self.config = config
        self.api = API(self.config.api_uri, format="json", debug=self.config.debug)

    def slugfy(self, text, separator):
        ret = ""
        for c in text.lower():
            try:
                ret += htmlentitydefs.codepoint2name[ord(c)]
            except:
                ret += c
        ret = re.sub("([a-zA-Z])(uml|acute|grave|circ|tilde|cedil)", r"\1", ret)
        ret = re.sub("\W", " ", ret)
        ret = re.sub(" +", separator, ret)

        return ret.strip()

    @translate_gooapi_to_gooclient_exception
    def request_token(self):
        url = self.config.api_uri
        api = API(url, auth=(self.config.username,
                                self.config.password),
                     debug=self.config.debug)
        token = api.auth.post({})
        self.set_token(token['token'])
        return token['token']

    def set_token(self, token):
        self.token = token

    @translate_gooapi_to_gooclient_exception
    def get_apps(self, args):
        apps = self.api.apps.get(token=self.token)
        apps = apps['objects']

        # Field name and size in cols
        fields = [ {'id': 5},
                   {'name': 30},
                   {'multi_hosts': 15},
                   {'multi_thread': 15}]

        self.output.show(fields, apps)
        return apps

    @translate_gooapi_to_gooclient_exception
    def get_jobs(self, args):
        jobs = self.api.jobs.get(token=self.token)
        jobs = jobs['objects']

        # Field name and size in cols
        fields = [ {'id': 5},
                   {'name': 30},
                   {'status': 7},
                   {'priority': 10},
                   {'progress': 10}]

        self.output.show(fields, jobs)
        return jobs

    @translate_gooapi_to_gooclient_exception
    def delete_object(self, args):
        object_id = args.object_id

        servers = self._get_dataproxy_servers()
        if len(servers) == 0:
            print "Error: No dataproxy servers found"
            print "Please contact NCC team"
            print "Aborting..."
            sys.exit()

        # TODO: write a better heuristic, now is the first server.
        server_uri = servers[0]['url']

        dps_api = API(server_uri, debug=self.config.debug)
        dps_api.dataproxy.objects(object_id).delete(token=self.token)

        print "Object %s delete with success" % object_id

    @translate_gooapi_to_gooclient_exception
    def download_object(self, args):
        object_id = args.object_id

        servers = self._get_dataproxy_servers()
        if len(servers) == 0:
            print "Error: No dataproxy servers found"
            print "Please contact NCC team"
            print "Aborting..."
            sys.exit()

        # TODO: write a better heuristic, now is the first server.
        server_url = servers[0]['url']
        server_uri = "%sapi/%s/" % (server_url, CURRENT_API_VERSION)
        dps_api = API(server_uri, debug=self.config.debug)
        data = dps_api.dataproxy.objects(object_id).get(token=self.token)
        f = open("object-%s.zip" % object_id, "w+")
        f.write(data)
        f.close()

        print "Finish"

    @translate_gooapi_to_gooclient_exception
    def upload_object(self, args):
        filename = args.object
        object_name = args.name

        if not os.path.exists(filename):
            print "Error: Failed to open %s" % filename
            print "Aborting..."
            sys.exit()

        servers = self._get_dataproxy_servers()
        if len(servers) == 0:
            print "Error: No dataproxy servers found"
            print "Please contact NCC team"
            print "Aborting..."
            sys.exit()

        # TODO: write a better heuristic, now is the first server.
        server_url = servers[0]['url']
        f = open(filename, 'r')
        object_data = {'name': "%s" % object_name,
                       'file': f}
        server_uri = "%sapi/%s/" % (server_url, CURRENT_API_VERSION)

        dps_api = API(server_uri, debug=self.config.debug)
        result = dps_api.dataproxy.objects.post(data=object_data, token=self.token)
        f.close()

        print "%s uploaded with success" % filename

    @translate_gooapi_to_gooclient_exception
    def get_objects(self, args):
        objects = self.api.objects.get(token=self.token)
        objects = objects['objects']

        # Field name and size in cols
        fields = [ {'id': 5},
                   {'name': 30},
                   {'size': 7},
                   {'create_time': 10}]

        self.output.show(fields, objects)
        return objects


    @translate_gooapi_to_gooclient_exception
    def _get_dataproxy_servers(self):
        servers = self.api.dataproxyserver.get(token=self.token)
        servers = servers['objects']
        return servers

    def show_dataproxy_servers(self, args):
        servers = self._get_dataproxy_servers()
        fields = [ {'id': 5},
                   {'name': 30},
                   {'url': 30}]

        self.output.show(fields, servers)

    @translate_gooapi_to_gooclient_exception
    def get_job_template(self, args):
        app_id = args.app_type_id
        name = args.name
        slug = self.slugfy(name,"-")
        app = self.api.apps(app_id).get(token=self.token)

        exclude = {'id', 'executable', 'name', 'resource_uri'}
        print "# Goo template file"
        print "# Generated by goo-client at %s" % datetime.datetime.utcnow()
        print "name='%s'" % name
        print "slug=%s" % slug
        print "app_id=%s" % app_id
        for v, k in app.items():
            if v not in exclude:
                print "%s=%s" % (v, k)

    @translate_gooapi_to_gooclient_exception
    def remove_job(self, args):
        job_id = args.job_id
        result = self.api.jobs(job_id).delete(token=self.token)

        print "Job %s removed" % job_id

    @translate_gooapi_to_gooclient_exception
    def submit_job(self, args):
        template = args.template
        if not os.path.exists(template):
            print "Error: Failed to open %s" % template
            print "Aborting..."
            sys.exit()
        cp = ConfigParser.ConfigParser()
        cp.readfp(FakeSecHead(open(template)))

        fields = {'name', 'app', 'hosts', 'pph', 'priority', 'restart',
                  'executable', 'args', 'inputs', 'outputs', 'checkpoints',
                  'app_objs', 'input_objs', 'checkpoint_objs', 'ttl',
                  'disk_requirement', 'memory_requirement'}

        values = {}
        for field in fields:
            try:
                value = cp.get('template', field)
                if value is '':
                    print "Error: Syntax invalid"
                    print "%s has a empty value" % field
                    print "Aborting..."
                    break
                    sys.exit()

                if field in ('app_objs', 'input_objs', 'checkpoint_objs'):
                    values[field] = value.split(",")
                else:
                    values[field] = value

            except:
                pass

        job = self.api.jobs.post(values, token=self.token)
        print "Job %s sent to queue" % job['id']
