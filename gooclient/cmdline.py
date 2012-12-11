import sys
import argparse

class GooCmdLine():
    def __init__(self, api):
        self.parser = argparse.ArgumentParser(prog='PROG',
                 description='goo client command line.')
        self.parser.add_argument('--version',
                            action='version',
                            version='%(prog)s 0.1.0')
        self.parser.add_argument('-v', '--verbose',
                            action='count',
                            help="run in verbose mode")

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

    def parse_args(self):
        self.args = self.parser.parse_args()

    def execute(self):
        self.args.func(self.args)
