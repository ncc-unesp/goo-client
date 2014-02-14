import ConfigParser
import os
import sys
import requests

class GooConfig():
    config = "~/.goorc"
    debug = False
    api_uri = None
    token = None

    def __init__(self):
        self.gooconfig = ConfigParser.ConfigParser()
        try:
            self.gooconfig.readfp(open(os.path.expanduser(self.config)))
        except IOError:
            print "Warning: Could not open config file."
            print "Creating a new one..."
            os.open(os.path.expanduser(self.config), os.O_WRONLY | os.O_CREAT, 0600)
            self.gooconfig.add_section("global")
            self.gooconfig.add_section("auth")
            self.save_config()

        self.load_global()
        self.load_token()

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

    def load_token(self):
        try:
            self.token = self.gooconfig.get("auth", "token")
        except ConfigParser.NoOptionError:
            pass

    def save_token(self, token):
        self.token = token
        self.gooconfig.set("auth", "token", token)
        self.save_config()

    def save_api_uri(self, api_uri):
        self.api_uri = api_uri
        self.gooconfig.set("global", "api_uri", api_uri)
        self.save_config()

    def save_config(self):
        f = open(os.path.expanduser(self.config), 'w')
        self.gooconfig.write(f)
        f.close()
