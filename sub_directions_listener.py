# Recieves directions from Google Directions API and returns in minutes the amount of 
# time a user has until he/she should leve to walk to the first bus stop

import googlemaps
import json
import argparse
import sys
from datetime import datetime
from datetime import timedelta
from pythonosc import osc_message_builder
from pythonosc import udp_client
from time import sleep

# Client key - unique, found on Google Developers Console
gmaps = googlemaps.Client(key='AIzaSyDqdBUvQzqfgLJPdfQUqiWGEWK-UIucyo0')
client = udp_client.UDPClient("127.0.0.1", 54321)

def sendOSCMessage(mess, addr):
    msg = osc_message_builder.OscMessageBuilder(address = addr)
    msg.add_arg(mess)
    msg = msg.build()
    client.send(msg)

def directions_listener(start, end):
	while 1:
		# Request directions via public transit
		starting_dest = start # "1942 Canyon Blvd, Boulder, CO"
		goal_dest = end # "Department of Computer Science, 1111 Engineering Drive, Boulder, CO"
		now = datetime.now()
		directions_result = gmaps.directions(starting_dest,
		                                     goal_dest,
		                                     mode="transit",
		                                     departure_time=now)

		# Receives the departure time from Google Directions API
		time_result = (directions_result[0]['legs'][0]['departure_time']['text'])

		# Parses the departure time string into total minutes of the day
		hours_result, time_result = time_result.split(":", 1)
		minutes_result, time_result = time_result[:len(time_result)//2], time_result[len(time_result)//2:]
		if time_result == "pm" and int(hours_result) != 12:
		    hours_result = int(hours_result)+ 12
		else:
		    hours_result = int(hours_result)
		time_I_should_leave = hours_result*60 + int(minutes_result)

		# Calculate current time in minutes using the now datetime object
		time_it_is = now.hour*60 + now.minute
		time_left = time_I_should_leave - time_it_is
		sendOSCMessage(time_left, "/directions_sender")

		print(time_left, "minutes till I should leave for the bus")
		sleep(30)

if __name__ == "__main__":
	client = udp_client.UDPClient("127.0.0.1", 54321)
	if len(sys.argv) != 3:
		print("wrong parameters")
	else:
		directions_listener(sys.argv[1], sys.argv[2])
