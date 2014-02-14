import os
import sys
from client import GooClient
from config import GooConfig
from cmdline import GooCmdLine
import getpass

def main():
    config = GooConfig()

    if not config.api_uri:
        print "Warning: No server URL found."
        api_uri = raw_input("Enter the server address: ")
        config.save_api_uri(api_uri)

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
        print "You need inform your login and password, to get a new token"
        try:
            username = raw_input("username: ")
            password = getpass.getpass('password: ')
        except:
            print "You must insert a username and password."
            print "Aborting..."
            sys.exit()

        token = client.request_token(username, password)
        if token is None:
            print "Error: Could not get token."
            print "Aborting..."
            sys.exit()

        config.save_token(token)

    client.set_token(config.token)

    # Parse cmd line
    #cmd = GooCmdLine(client)
    #cmd.parse_args()
    cmd.execute()
