import ConfigParser
import os
import sys
import requests

class GooConfig():
    def __init__(self):
        self.config = "~/.goorc"
        self.debug = False
        self.api_uri = os.environ.get('GOO_API_URI')
        self.user = os.environ.get('USER')
        self.password = os.environ.get('GOO_PASSWORD')
        self.token = os.environ.get('GOO_TOKEN')

        self.gooconfig = ConfigParser.ConfigParser()

        self.parse()

    def parse(self):
        try:
            self.gooconfig.readfp(open(os.path.expanduser(self.config)))
        except IOError, e:
            print "Config file not found."
            print "Creating new config file."
            print "For more information please run:"
            print " $ goo-client --help"
            self.create()
            self.save_user(self.user)
            self.save_api_uri(self.api_uri)
            self.save_token(self.token)

        self.load_global()
        self.load_auth()

    def load_global(self):
        # Try to read global section
        try:
            self.debug = self.gooconfig.getboolean("global", "debug")
        except ConfigParser.NoOptionError:
            pass

        try:
            self.api_uri = self.gooconfig.get("global", "api_uri")
        except ConfigParser.NoOptionError:
            pass

    def load_auth(self):
        try:
            self.user = self.gooconfig.get("auth", "user")
        except ConfigParser.NoOptionError:
            pass

        try:
            self.token = self.gooconfig.get("auth", "token")
        except ConfigParser.NoOptionError:
            pass

    def save_api_uri(self, api_uri):
        self.api_uri = api_uri
        if self.api_uri:
           self.gooconfig.set("global", "api_uri", api_uri)
           self.save()

    def save_user(self, user):
        self.user = user
        if self.user:
            self.gooconfig.set("auth", "user", user)
            self.save()

    def save_token(self, token):
        self.token = token
        if self.token:
            self.gooconfig.set("auth", "token", token)
            self.save()

    def create(self):
        """ Creates a empty config file."""
        self.gooconfig.add_section("global")
        self.gooconfig.add_section("auth")

    def save(self):
        f = open(os.path.expanduser(self.config), 'w')
        self.gooconfig.write(f)
        f.close()
