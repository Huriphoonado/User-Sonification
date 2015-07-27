# Willie Payne
# Monitors keypresses, stores words, and sends character information to
# a max patch via OSC

# Keypress monitoring code based on: https://gist.github.com/ljos/3019549
# License: http://ljos.mit-license.org/

import psutil
import argparse
import enchant
 
from AppKit import NSApplication, NSApp
from Foundation import NSObject, NSLog
from Cocoa import NSEvent, NSKeyDownMask
from PyObjCTools import AppHelper
from pythonosc import osc_message_builder
from pythonosc import udp_client

word_list = [] # store words
word_holder = "" # store characters that make up words

spell_dict = enchant.Dict("en_US")

client = udp_client.UDPClient("127.0.0.1", 54321)

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        mask = NSKeyDownMask
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, handler)

# Sends an OSC message via the included address
def sendOSCMessage(mess, addr):
    msg = osc_message_builder.OscMessageBuilder(address = addr)
    msg.add_arg(mess)
    msg = msg.build()
    client.send(msg)

# Sends an OSC message via the included address
def sendOSCMessage2(mess1, mess2, addr):
    msg = osc_message_builder.OscMessageBuilder(address = addr)
    msg.add_arg(mess1)
    msg.add_arg(mess2)
    msg = msg.build()
    client.send(msg)

# Handles typed characters
def doSomething(mess):
    global word_holder
    # if character is a letter: send it to Max, and add it to the current word
    if ord(mess) >= 65 and ord(mess) <= 122:
        sendOSCMessage(mess.lower(), "/char_sender")
        word_holder += mess
    # if it is delete: remove last character from our word
    # does not support highlight and delete
    elif ord(mess) >= 33 and ord(mess) <= 64:
        sendOSCMessage(mess, "/char_sender")
    elif ord(mess) in (8, 18, 127):
        print("Delete Pressed")
        word_holder = word_holder[:-1]
    # if character is space or enter: we have finished building our word
    elif ord(mess) in (32, 13):
        if ord(mess) == 32:
            sendOSCMessage("sp", "/char_sender")
        else:
            sendOSCMessage("ret", "/char_sender")
        if len(word_holder) > 0:
            if spell_dict.check(word_holder) == True:
                word_list.append(word_holder)
                sendOSCMessage(len(word_list), "/word_count_sender")
            sendOSCMessage2(word_holder, str(spell_dict.check(word_holder)), "/word_sender")
        #print(word_list)
        #print("The word was spelled correctly: " + (str(spell_dict.check(word_holder))))
        word_holder = ""

# Handles keyboard events
def handler(event):
    global word_holder
    try:
        typed_char = event.charactersIgnoringModifiers()
        doSomething(str(typed_char))
        #NSLog(u"%@", event.charactersIgnoringModifiers())
       
    except KeyboardInterrupt:
        AppHelper.stopEventLoop()
        print ("Finished")

def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    AppHelper.runEventLoop()
    
if __name__ == '__main__':
    main()