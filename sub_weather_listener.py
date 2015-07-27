import pywapi
import string
import sys

from time import sleep

from pythonosc import osc_message_builder
from pythonosc import udp_client

def sendOSCMessage(mess, addr):
    msg = osc_message_builder.OscMessageBuilder(address = addr)
    msg.add_arg(mess)
    msg = msg.build()
    client.send(msg)

def weather_listener(zip_code):
	print("called")
	while 1:
		msg = osc_message_builder.OscMessageBuilder(address = "/filter")
		yahoo_result = pywapi.get_weather_from_yahoo(zip_code)
		tempVal = round(int(yahoo_result['condition']['temp'])*9/5 + 32, 1)
		sendOSCMessage(tempVal, "/weather_sender")
		print (tempVal)
		sleep(60)

if __name__ == "__main__":
	client = udp_client.UDPClient("127.0.0.1", 54321)
	if len(sys.argv) != 2 or str(sys.argv[1]) == "Zip Code":
		print("Zip Code not entered")
	else:
		zip_code = str(sys.argv[1])
		print(zip_code)
		weather_listener(zip_code)