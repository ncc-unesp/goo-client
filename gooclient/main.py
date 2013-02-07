import os
import sys
from gooclient.client import GooClient
from gooclient.config import GooConfig
from gooclient.cmdline import GooCmdLine

def main():

    config = GooConfig()
    client = GooClient(config)
    # Parse cmd line
    cmd = GooCmdLine(client)

    cmd.parse_args()

    # Load global section and token, if token is not found, ask for
    # credentials and get a new token
    token = config.read_token()
    if token is None:
        config.username, config.password = config.get_credentials()

        token = client.request_token()
        if token is None:
            print "Error: Could not get token."
            print "Aborting..."
            sys.exit()

        config.save_token(token=token)

    client.set_token(token)

    cmd.execute()
