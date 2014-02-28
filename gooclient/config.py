# This file is part of goo-client.
#
# Copyright (c) 2103-2014 by Núcleo de Computação Científica, UNESP
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#    Gabriel von. Winckler <winckler AT ncc DOT unesp DOT br>
#
# goo-client is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# goo-client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
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
