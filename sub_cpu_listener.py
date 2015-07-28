import psutil
import argparse
import string

from collections import deque
from time import sleep

from pythonosc import osc_message_builder
from pythonosc import udp_client

def sendOSCMessage(mess, addr):
    msg = osc_message_builder.OscMessageBuilder(address = addr)
    msg.add_arg(mess)
    msg = msg.build()
    client.send(msg)

def cpu_usage_listener():
	print("called")
	cpList = deque([7, 7, 7, 7, 7, 7, 7, 7, 7, 7])
	while True:
		cpUse = psutil.cpu_percent(interval=.1)
		cpList.popleft()
		cpList.append(cpUse)
		averaged_cpu_usage = round(sum(cpList)/10, 1)
		print(averaged_cpu_usage)
		sendOSCMessage(averaged_cpu_usage, "/cpu_usage_sender")

if __name__ == "__main__":
	client = udp_client.UDPClient("127.0.0.1", 54321)
	cpu_usage_listener()
