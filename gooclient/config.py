from ConfigParser import ConfigParser
import os
import sys
import requests
import getpass

class GooConfig():
    gooconfig = None
    config = "~/.goorc"

    debug = False
    api_uri = None

    # Only used when no token is valid
    username = None
    password = None

    def __init__(self):
        self.gooconfig = ConfigParser()
        try:
            self.gooconfig.readfp(open(os.path.expanduser(self.config)))
        except IOError:
            print "Error: Could not open config file."
            print "Create a %s file with 600 permissions." % self.config
            print "Aborting..."
            sys.exit()


        self.load_global()

    def load_global(self):
        # Try to read global section
        try:
            self.debug = self.gooconfig.get("global", "debug")
        except:
            pass

        try:
            self.api_uri = self.gooconfig.get("global", "api_uri")
        except:
            print "Error: Could not read api_uri."
            print "Please check global section."
            print "Aborting..."
            sys.exit()

    def read_token(self):
        try:
            token = self.gooconfig.get("auth", "token")
        except:
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

        f = open(os.path.expanduser(self.config), 'w')
        self.gooconfig.write(f)
        f.close()
