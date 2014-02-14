import sys
import argparse

class GooCmdLine():
    def __init__(self, api):
        self.parser = argparse.ArgumentParser(prog='PROG',
                 description='goo client command line.')
        self.parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s 0.1.0')

        self.parser.add_argument('-d', '--debug',
                                 action='store_true',
                                 help="Run in debug mode")

        subparsers = self.parser.add_subparsers(title='subcommands',
                            description='valid subcommands',
                            help='additional help')

        # apps
        apps = subparsers.add_parser('apps', help='apps help')
        apps_subparsers = apps.add_subparsers(title='apps subcommands',
                          description='valid subcommands',
                          help='additional help')


        # apps list
        apps_list = apps_subparsers.add_parser('list')
        apps_list.set_defaults(func=api.get_apps)

        # Jobs
        jobs = subparsers.add_parser('jobs', help='jobs help')
        jobs_subparsers = jobs.add_subparsers(title='jobs subcommands')

        # Jobs list
        jobs_list = jobs_subparsers.add_parser('list', help="list all jobs")
        jobs_list.set_defaults(func=api.get_jobs)

        # Job show info
        jobs_show = jobs_subparsers.add_parser('show', help="show info about a job")
        jobs_show.add_argument('-j', '--job-id',
                                 help='job id get info',
                                 required=True)
        jobs_show.set_defaults(func=api.show_job)


        # Jobs template
        jobs_template = jobs_subparsers.add_parser('template', help="download a job template")
        jobs_template.add_argument('-n', '--name',
                                   help='job name',
                                   required=True)
        jobs_template.add_argument('-t', '--app-type-id',
                                   help='app type id',
                                   required=True)
        jobs_template.set_defaults(func=api.get_job_template)

        # Jobs submit
        jobs_submit = jobs_subparsers.add_parser('submit', help="submit a new job")
        jobs_submit.add_argument('-t', '--template',
                                 help='template file name',
                                 required=True)
        jobs_submit.set_defaults(func=api.submit_job)

        # Job remove
        jobs_remove = jobs_subparsers.add_parser('remove', help="remove a job")
        jobs_remove.add_argument('-j', '--job-id',
                                 help='job id to remove',
                                 required=True)
        jobs_remove.set_defaults(func=api.remove_job)

        # Objects
        objects = subparsers.add_parser('objects', help='objects help')
        objects_subparsers = objects.add_subparsers(title='objects subcommands')
        # Objects list
        objects_list = objects_subparsers.add_parser('list', help="list all objects")
        objects_list.set_defaults(func=api.get_objects)
        # Objects download
        objects_download = objects_subparsers.add_parser('download', help="download an object")
        objects_download.add_argument('-i', '--object-id',
                                    help='object id',
                                    required=True)
        objects_download.set_defaults(func=api.download_object)

        # Objects upload
        objects_upload = objects_subparsers.add_parser('upload', help="upload an object")
        objects_upload.add_argument('-p', '--public',
                                    help='if this object is public. Default is false.',
                                    action='store_true')
        objects_upload.add_argument('-o', '--object',
                                    help='object to upload',
                                    required=True)
        objects_upload.set_defaults(func=api.upload_object)

        # Objects Create
        objects_create = objects_subparsers.add_parser('create', help="create a object and upload")
        objects_create.add_argument('-n', '--name',
                                    help='name of object to create',
                                    required=True)
        objects_create.add_argument('-i', '--inputs', nargs="+",
                                    help='files to pack into object and upload',
                                    required=True)
        objects_create.set_defaults(func=api.create_object)

        # Object delete
        objects_delete = objects_subparsers.add_parser('delete', help="delete an object")
        objects_delete.add_argument('-i', '--object-id',
                                    help='object id',
                                    required=True)
        objects_delete.set_defaults(func=api.delete_object)

        # Data Proxy Servers
        dps = subparsers.add_parser('dps', help='Data Proxy Servers help')
        dps_subparsers = dps.add_subparsers(title='Data Proxy Servers subcommands')
        # DPS list
        dps_list = dps_subparsers.add_parser('list', help="list all availables DPS")
        dps_list.set_defaults(func=api.show_dataproxy_servers)



    def parse_args(self):
        self.args = self.parser.parse_args()

    def execute(self):
        self.args.func(self.args)
