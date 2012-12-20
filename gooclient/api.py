import slumber
import requests
import sys
import datetime
import htmlentitydefs, re
import os
import ConfigParser
import json
from gooclient.output import Output

class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[template]\n'
    def readline(self):
        if self.sechead:
            try: return self.sechead
            finally: self.sechead = None
        else: return self.fp.readline()

class GooApi():
    def __init__(self, config=None):
        if config is None:
            return None

        self.output = Output()
        self.config = config
        self.api = slumber.API(self.config.api_uri, format="json")

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

    def request_token(self):
        try:
            url = self.config.api_uri
            api = slumber.API(url, auth=(self.config.username,
                                         self.config.password))
            token = api.auth.post({})
            self.set_token(token['token'])
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()
        return token['token']

    def set_token(self, token):
        self.token = token

    def get_apps(self, args):
        try:
            apps = self.api.apps.get(token=self.token)
            apps = apps['objects']

            # Field name and size in cols
            fields = [ {'id': 5},
                       {'name': 30},
                       {'multi_hosts': 15},
                       {'multi_thread': 15}]

            self.output.show(fields, apps)
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()
        return apps

    def get_jobs(self, args):
        try:
            jobs = self.api.jobs.get(token=self.token)
            jobs = jobs['objects']

            # Field name and size in cols
            fields = [ {'id': 5},
                       {'name': 30},
                       {'status': 7},
                       {'priority': 10},
                       {'progress': 10}]

            self.output.show(fields, jobs)
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()

        return jobs

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

        try:
            dps_api = slumber.API(server_uri)
            dps_api.dataproxy.objects(object_id).delete(token=self.token)
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()

        print "Object %s delete with success" % object_id

    def download_object(self, args):
        object_id = args.object_id

        servers = self._get_dataproxy_servers()
        if len(servers) == 0:
            print "Error: No dataproxy servers found"
            print "Please contact NCC team"
            print "Aborting..."
            sys.exit()

        # TODO: write a better heuristic, now is the first server.
        server_uri = servers[0]['url']

        try:
            dps_api = slumber.API(server_uri)
            data = dps_api.dataproxy.objects(object_id).get(token=self.token)
            file = open("object-%s.zip" % object_id, "w+")
            file.write(data)
            file.close()
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()

        print "Finish"

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
        server_uri = servers[0]['url']

        object_data = {'name': "%s" % object_name,
                       'file': open(filename)}
        try:
            dps_api = slumber.API(server_uri)
            file = open(filename)
            dps_api.dataproxy.objects.post(object_data, token=self.token)
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()

        print "%s uploaded with success" % filename

    def get_objects(self, args):
        try:
            objects = self.api.objects.get(token=self.token)
            objects = objects['objects']

            # Field name and size in cols
            fields = [ {'id': 5},
                       {'name': 30},
                       {'size': 7},
                       {'create_time': 10}]

            self.output.show(fields, objects)
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()

        return objects


    def get_app(self, app_id):
        try:
            app = self.api.apps(app_id).get(token=self.token)
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()
        return app

    def _get_dataproxy_servers(self):
        try:
            servers = self.api.dataproxyserver.get(token=self.token)
            servers = servers['objects']

        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()
        return servers

    def show_dataproxy_servers(self, args):
        servers = self._get_dataproxy_servers()
        fields = [ {'id': 5},
                   {'name': 30},
                   {'url': 30}]

        self.output.show(fields, servers)

    def get_job_template(self, args):
        app_id = args.app_type_id
        name = args.name
        slug = self.slugfy(name,"-")
        app = self.get_app(app_id)

        exclude = {'id', 'executable', 'name', 'resource_uri'}
        print "# Goo template file"
        print "# Generated by goo-client at %s" % datetime.datetime.utcnow()
        print "# user token: %s" % self.token
        print "name='%s'" % name
        print "slug=%s" % slug
        print "app_id=%s" % app_id
        for v, k in app.items():
            if v not in exclude:
                print "%s=%s" % (v, k)

    def remove_job(self, args):
        try:
            job_id = args.job_id
            result = self.api.jobs(job_id).delete(token=self.token)
        except Exception as e:
            print "%s" % e
            print "Aborting..."
            sys.exit()

        print "Job %s removed" % job_id

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
                  'app_obj_id', 'input_obj_id', 'checkpoint_obj_id', 'ttl',
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

                values[field] = value
            except:
                pass

        job = self.api.jobs.post(values, token=self.token)
        print "Job %s sent to queue" % job['id']
