from gooclientlib.api import API
from gooclientlib.exceptions import HttpClientError, HttpServerError
import tempfile
import argparse
import requests
import glob
import sys
import datetime
import zipfile
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
    def __init__(self, api_uri, debug=False):
        self.output = Output()
        self.api_uri = api_uri
        self.debug = debug

        if self.debug:
            self.set_debug()

    def _slugfy(self, text, separator='-'):
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
    def create_api(self):
        self.api = API(self.api_uri, format="json", debug=self.debug)

    @translate_gooapi_to_gooclient_exception
    def set_debug(self):
        self.debug = sys.stderr

    @translate_gooapi_to_gooclient_exception
    def _get_data_proxy(self):
        servers = self._get_dataproxy_servers()
        if len(servers) == 0:
            print "Error: No dataproxy servers found"
            print "Please contact NCC team"
            print "Aborting..."
            sys.exit()

        # TODO: write a better heuristic, now is the first server.
        server_url = servers[0]['url']
        server_uri = "%sapi/%s/" % (server_url, CURRENT_API_VERSION)
        return server_uri



    @translate_gooapi_to_gooclient_exception
    def request_token(self, username, password):
        api = API(self.api_uri, auth=(username, password), debug=self.debug)
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
                   {'_name': 30},
                   {'_multi_hosts': 15},
                   {'_multi_thread': 15}]

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

        server_uri = self._get_data_proxy()

        dps_api = API(server_uri, debug=self.debug)
        dps_api.dataproxy.dataobjects(object_id).delete(token=self.token)

        print "Object %s delete with success" % object_id

    @translate_gooapi_to_gooclient_exception
    def download_object(self, args):
        object_id = args.object_id

        # Get object info
        obj = self.api.dataobjects(object_id).get(token=self.token)
        server_uri = self._get_data_proxy()
        dps_api = API(server_uri, debug=self.debug)
        data = dps_api.dataproxy.dataobjects(object_id).get(token=self.token)
        f = open(obj['name'], "w+")
        f.write(data)
        f.close()

        print "Finish"

    @translate_gooapi_to_gooclient_exception
    def upload_object(self, args):
        filename = args.object
        object_name = os.path.basename(filename)

        if not os.path.exists(filename):
            print "Error: Failed to open %s" % filename
            print "Aborting..."
            sys.exit()

        server_uri = self._get_data_proxy()

        f = open(filename, 'rb')
        object_data = {'name': object_name,
                       'file': f}
        if args.public:
            object_data['public'] = 'true'

        dps_api = API(server_uri, debug=self.debug)
        result = dps_api.dataproxy.dataobjects.post(data=object_data, token=self.token)
        f.close()

        object_id = re.search(r'/api/v1/dataobjects/(\d+)/',
                                      result['resource_uri']).group(1)
        print "%s uploaded with success (#%s)" % (filename, object_id)

    @translate_gooapi_to_gooclient_exception
    def create_object(self, args):
        inputs = args.inputs
        object_name = "%s.zip" % args.name

        fd, filepath = tempfile.mkstemp('.zip', self._slugfy(args.name))

        # Create package
        print 'Creating object package...'
        for f in inputs:
            zf = zipfile.ZipFile(filepath, mode='a')
            try:
                print '  adding %s' % f
                zf.write(f)
            finally:
                zf.close()

        server_uri = self._get_data_proxy()
        f = open(filepath, 'rb')
        object_data = {'name': object_name,
                       'file': f}

        dps_api = API(server_uri, debug=self.debug)
        result = dps_api.dataproxy.dataobjects.post(data=object_data, token=self.token)
        f.close()

        object_id = re.search(r'/api/v1/dataobjects/(\d+)/',
                                      result['resource_uri']).group(1)
        print "%s uploaded with success (#%s)" % (object_name, object_id)

        # Force tempfile to be removed
        os.unlink(filepath)
        return result['resource_uri']

    @translate_gooapi_to_gooclient_exception
    def get_objects(self, args):
        objects = self.api.dataobjects.get(token=self.token)
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
        slug = self._slugfy(name,"-")
        app = self.api.apps(app_id).get(token=self.token)

        required_fields = app['_required_fields'].split(', ')
        constant_fields = app['_constant_fields'].split(', ')

        exclude = ('id', 'resource_uri')

        print "# Goo template file"
        print "# Generated by goo-client at %s" % datetime.datetime.utcnow()

        print ""*2
        print "# Required fields"
        print "name=%s" % name
        print "application=/api/%s/apps/%s/" % (CURRENT_API_VERSION, app_id)

        for f in required_fields:
            print "%s=%s" % (f, app[f])

        print ""*2
        print "# Optional fields"
        print "# Uncomment the follow lines if you want to change the"
        print "# default values"
        print ""

        for v, k in app.items():
            if v not in exclude and \
                 not v.startswith('_') and \
               v not in constant_fields and \
               v not in required_fields:
                print "#%s=%s" % (v, k)

        print "#slug=%s" % slug

    @translate_gooapi_to_gooclient_exception
    def show_job(self, args):
        job_id = args.job_id
        result = self.api.jobs(job_id).get(token=self.token)
        fields = ('id', 'name', 'app_name', 'priority', 'status', 'progress',
                  'restart', 'maxtime', 'create_time', 'modification_time', 'input_objs', 'output_objs')

        width = 52

        print "-" * width
        print "Job Detail".center(width)
        print "-" * width
        for f in fields:
            print "%20s: " % f,
            if f in ('input_objs', 'output_objs'):
                output = []
                for o in result[f]:
                    output.append(o['id'])
            else:
                output = result[f]
            print "%s" % output
        print "-" * width


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

        fields = ('name', 'application', 'hosts', 'cores_per_host', 'priority', 'restart',
                  'executable', 'args', 'inputs', 'outputs', 'checkpoints',
                  'input_objs', 'output_objs', 'checkpoint_objs', 'maxtime',
                  'diskspace', 'memory')

        values = {}
        inputs = None
        for field in fields:
            try:
                value = cp.get('template', field)
                if value is '':
                    print "Error: Syntax invalid"
                    print "%s has a empty value" % field
                    print "Aborting..."
                    sys.exit()

                if field in ('output_objs', 'input_objs', 'checkpoint_objs'):
                    values[field] = value.split(" ")
                elif field is 'inputs':
                    inputs = value.split(" ")
                else:
                    values[field] = value
            except:
                pass

        if inputs:
            obj_name = self._slugfy("%s-inputs" % values['name'])
            input_files = []
            for i in inputs:
                input_files.extend(glob.glob(i))
            args = argparse.Namespace(name=obj_name, inputs=input_files)
            values['input_objs'] = [self.create_object(args)]

        job = self.api.jobs.post(values, token=self.token)
        print "Job %s sent to queue (#%d)" % (job['name'], job['id'])
