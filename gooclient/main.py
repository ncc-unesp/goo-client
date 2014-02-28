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
from client import GooClient
from config import GooConfig
from cmdline import GooCmdLine
import getpass
import sys

def main():
    config = GooConfig()
    if config.api_uri is None:
        config.save_api_uri(raw_input("Enter the server address: "))

    if config.user is None:
        config.save_user(raw_input("Enter the username: "))

    if config.password is None and config.token is None:
        config.password = getpass.getpass("Enter the password for %s: " % config.user)

    if not config.api_uri or not config.user or (not config.password and not config.token):
        print "Missing information necessary to connect to server."
        print "goo-client uses theses variables:"
        print ""
        print "GOO_API_URI    = Server API endpoing"
        print "USER           = User to authenticate"
        print "GOO_PASSWORD   = Password used only to get API token"
        print ""
        print "Use it or configure your config file."
        print "Aborting..."
        sys.exit()

    client = GooClient(config.api_uri, config.debug)
    cmd = GooCmdLine(client)
    cmd.parse_args()

    if cmd.args.debug:
        client.set_debug()

    client.create_api()

    # Load global section and token, if token is not found, ask for
    # credentials and get a new token
    if config.token is None:
        print "Token not found in your %s" % config.config
        print "Creating a new one..."
        token = client.request_token(config.user, config.password)
        if token is None:
            print "Error: Could not get token."
            print "Aborting..."
            sys.exit()

        config.save_token(token)

    client.set_token(config.token)
    cmd.execute()
