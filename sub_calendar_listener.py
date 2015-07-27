import httplib2
import os
import argparse

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from time import sleep

from pythonosc import osc_message_builder
from pythonosc import udp_client

import datetime

client = udp_client.UDPClient("127.0.0.1", 54321)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'PythonSonification'


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
                                   'calendar-quickstart.json')

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

def sendOSCMessage(mess, addr):
    msg = osc_message_builder.OscMessageBuilder(address = addr)
    msg.add_arg(mess)
    msg = msg.build()
    client.send(msg)

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the first upcoming event')
        eventsResult = service.events().list(
            calendarId='primary', timeMin=now, maxResults=1, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            print('No upcoming events found.')
            sendOSCMessage("None", "/calendar_sender")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # format returned string so that starting time lines up with datetime object
            start = str(start[:-6]) + ".0"
            start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%f")
            print(start)
            print(datetime.datetime.now())
            time_until_event = start - datetime.datetime.now()
            time_until_event = (time_until_event.days * 24 * 60) + time_until_event.seconds/60.
            print(time_until_event, "minutes until next event.")
            sendOSCMessage(round(time_until_event, 2), "/calendar_sender")
        sleep(30)

if __name__ == '__main__':
    main()