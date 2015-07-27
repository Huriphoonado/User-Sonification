import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from time import sleep

from pythonosc import osc_message_builder
from pythonosc import udp_client

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

client = udp_client.UDPClient("127.0.0.1", 54321)

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'PythonSonification'

def sendOSCMessage(mess, addr):
    msg = osc_message_builder.OscMessageBuilder(address = addr)
    msg.add_arg(mess)
    msg = msg.build()
    client.send(msg)

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """
    Creates a Gmail API service object 
    """
    while(1):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)

        results = service.users().messages().list(userId='me', q="is:unread", fields="resultSizeEstimate").execute()
        estimate = results.get("resultSizeEstimate", [])
        sendOSCMessage(estimate, "/gmail_sender")
        print(estimate) 
        sleep(30)

if __name__ == '__main__':
    main()