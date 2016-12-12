#!/usr/bin/python
# -*- coding: utf-8 -*-

"Minimal gui2py CHAT application (to be used as skeleton)"

from __future__ import with_statement   # for python 2.5 compatibility

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2016 Mariano Reingart"
__license__ = "LGPL 3.0"

import gui                                  

# --- here goes your event handlers ---

def send(evt):
    "Process an outgoing communication"
    # get the text written by the user (input textbox control)
    msg = ctrl_input.value
    # send the message (replace with socket/queue/etc.)
    gui.alert(msg, "Message")
    # record the message (update the UI)
    log(msg)
    ctrl_input.value = ""
    ctrl_input.set_focus()

def recv(evt=None):
    "Process an incoming communication"
    # receive the message (replace with socket/queue/etc.)
    msg = ""
    # record the message (update the UI)
    log(msg)

def log(msg):
    "Append the message to the output text box control"
    ctrl_output.value += msg + "\n"

# --- gui2py designer generated code starts ---

with gui.Window(name='mywin', title=u'gui2py chat', resizable=True, 
                height='461px', left='168', top='79', width='400px', ):
    gui.TextBox(name=u'output', multiline=True, height='403', left='8', 
                top='10', width='379')
    gui.TextBox(name=u'input', height='30', left='11', top='417', width='323')
    gui.Button(label=u'\u2192', name=u'send', left='348', top='419', 
               width='40', default=True, )

# --- gui2py designer generated code ends ---

mywin = gui.get("mywin")
ctrl_input = mywin["input"]
ctrl_output = mywin["output"]

# assign your event handlers:

mywin['send'].onclick = send

if __name__ == "__main__":
    # example to call a GUI function (i.e. from other thread):
    gui.call_after(log, "Welcome!")
    # basic startup: show windows, activate control and start GUI
    mywin.show()
    ctrl_input.set_focus()
    gui.main_loop()

