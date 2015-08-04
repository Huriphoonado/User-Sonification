# Willie Payne
# sub_facebook_listener.py

# Monitors whether the user's browser is actively displaying a tab on Facebook
# and sends via OSC the state True or False representing if the user is on Facebook

# Currently supports Safari and Chrome. (Firefox has limited Applescript support)
# Could be modified to support other time wasting sites

from subprocess import Popen, PIPE

import psutil

from time import sleep

from pythonosc import osc_message_builder
from pythonosc import udp_client

def sendOSCMessage(mess, addr):
    msg = osc_message_builder.OscMessageBuilder(address = addr)
    msg.add_arg(mess)
    msg = msg.build()
    client.send(msg)

# Returns what browsers are currently open
def check_what_is_open():
	safari_open = 0
	chrome_open = 0

	safari_cmd = "/usr/bin/osascript -e 'tell application \"Safari\"' -e 'count URL of every tab of every window' -e 'end tell'"
	chrome_cmd = "/usr/bin/osascript -e 'tell application \"Google Chrome\"' -e 'count URL of every tab of every window' -e 'end tell'"

	for proc in psutil.process_iter():
	    try:
	        pinfo = proc.as_dict(attrs=['pid', 'name'])
	    except psutil.NoSuchProcess:
	        pass
	    else:
	    	if pinfo['name'] == 'Safari':
	    		safari_pipe = Popen(safari_cmd, shell=True, stdout=PIPE).stdout.readlines()
	    		# prevents an error occuring when application is open without any windows
	    		if int(safari_pipe[0].decode("utf-8")) > 0:
	    			safari_open = 1
	    			#print('Safari is open.')
	    	if pinfo['name'] == 'Google Chrome':
	    		chrome_pipe = Popen(chrome_cmd, shell=True, stdout=PIPE).stdout.readlines()
	    		if int(chrome_pipe[0].decode("utf-8")) > 0:
	    			chrome_open = 1
	    			#print('Google Chrome is open.')
	return(safari_open, chrome_open)

# Will check if either has Facebook on as the open tab (does not trigger if the tab is not being viewed)
# Uses the return of check_what_is_open() so that it does not incorrectly open a closed browser
def check_on_facebook(safari_open, chrome_open):
	safari_cmd = "/usr/bin/osascript -e 'tell application \"Safari\"' -e 'get URL of current tab of front window' -e 'end tell'"
	chrome_cmd = "/usr/bin/osascript -e 'tell application \"Google Chrome\"' -e 'get URL of active tab of front window' -e 'end tell'"
	url_string = "https://www.facebook.com"

	if safari_open and chrome_open:
		safari_pipe = str(Popen(safari_cmd, shell=True, stdout=PIPE).stdout.readlines())
		chrome_pipe = str(Popen(chrome_cmd, shell=True, stdout=PIPE).stdout.readlines())
		return (url_string in safari_pipe or url_string in chrome_pipe)
	elif safari_open:
		safari_pipe = str(Popen(safari_cmd, shell=True, stdout=PIPE).stdout.readlines())
		return (url_string in safari_pipe)
	elif chrome_open:
		chrome_pipe = str(Popen(chrome_cmd, shell=True, stdout=PIPE).stdout.readlines())
		return (url_string in chrome_pipe)
	else:
		return False

# Will run every second
def continuously_check_on_facebook():
	while True:
		mess  = check_on_facebook(*check_what_is_open())
		sendOSCMessage(mess, "/facebook_sender")
		#print(mess)
		sleep(1)

if __name__ == "__main__":
	client = udp_client.UDPClient("127.0.0.1", 54321)
	continuously_check_on_facebook()