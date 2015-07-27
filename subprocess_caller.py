import atexit
import subprocess

from pythonosc import dispatcher
from pythonosc import osc_server

procs = ['', '', '', '', '', '']

def listen_to_cpu(unused_addr, args, val):
	print(val)
	if int(val) >= 1:
		procs[1] = subprocess.Popen(["python3", "sub_cpu_listener.py"])
	else:
		procs[1].kill()
		print("exited cpu")

def listen_to_weather(unused_addr, args, val, zip_code):
	print(val, zip_code)
	if int(val) >= 1:
		procs[2] = subprocess.Popen(["python3", "sub_weather_listener.py", str(zip_code)])
	else:
		procs[2].kill()
		print("exited weather")

def listen_to_calendar(unused_addr, args, val):
	print(val)
	if int(val) >= 1:
		procs[3] = subprocess.Popen(["python3", "sub_calendar_listener.py"])
	else:
		procs[3].kill()
		print("exited calendar")

def listen_to_gmail(unused_addr, args, val):
	print(val)
	if int(val) >= 1:
		procs[4] = subprocess.Popen(["python3", "sub_gmail_listener.py"])
	else:
		procs[4].kill()
		print("exited calendar")

def listen_to_directions(unused_addr, args, val, start, end):
	print(val)
	if int(val) >= 1:
		print(str(start))
		print(str(end))
		procs[5] = subprocess.Popen(["python3", "sub_directions_listener.py", str(start), str(end)])
	else:
		procs[5].kill()
		print("exited directions")

# Debug - tests whether script recieves messages from Max through OSC
def db_handler(unused_addr, args, val):
	print(val)
	sendOSCMessage(val * 2, "/pyDebug")

if __name__ == "__main__":
	dispatcher = dispatcher.Dispatcher()

	procs[0] = subprocess.Popen(["python3", "sub_type_monitor.py"])

	dispatcher.map("/listen_to_cpu", listen_to_cpu, "val")
	dispatcher.map("/listen_to_weather", listen_to_weather, "val")
	dispatcher.map("/listen_to_calendar", listen_to_calendar, "val")
	dispatcher.map("/listen_to_gmail", listen_to_gmail, "val")
	dispatcher.map("/listen_to_directions", listen_to_directions, "val")
	dispatcher.map("/debug", db_handler, "val")
	
	server = osc_server.ThreadingOSCUDPServer(
      ("127.0.0.1", 54322), dispatcher)
	server.serve_forever()

# Once the program is finished, make sure to kill all remaining subprocesses
@atexit.register
def kill_subprocesses():
	for proc in procs:
		if proc != '':
			proc.kill()