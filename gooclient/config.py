import ConfigParser
import os
import sys
import requests
import getpass

class GooConfig():
    config = "~/.goorc"

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

    def load_global(self):
        # Try to read global section
        try:
            self.debug = self.gooconfig.get("global", "debug")
        except ConfigParser.NoOptionError:
            self.debug = False

        try:
            self.api_uri = self.gooconfig.get("global", "api_uri")
        except ConfigParser.NoOptionError:
            print "Warning: No server URL found."
            self.api_uri = raw_input("URL: ")
            self.gooconfig.set("global", "api_uri", self.api_uri)
            self.save_config()

    def read_token(self):
        try:
            token = self.gooconfig.get("auth", "token")
        except ConfigParser.NoOptionError:
            return None

        return token

    def get_credentials(self):
        print "Token not found in your %s" % self.config
        print "You need inform your login and password, to get a new token"
        try:
            username = raw_input("username: ")
            password = getpass.getpass('password: ')
        except:
            print "You must insert a username and password."
            print "Aborting..."
            sys.exit()

        return username, password

    def save_token(self, token):
        self.gooconfig.set("auth", "token", token)
        self.save_config()

    def save_config(self):
        f = open(os.path.expanduser(self.config), 'w')
        self.gooconfig.write(f)
        f.close()
