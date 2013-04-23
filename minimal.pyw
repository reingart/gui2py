#!/usr/bin/python
# -*- coding: utf-8 -*-

"Minimal gui2py application (to be used as skeleton)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

import gui                                  

# --- here goes your event handlers ---

def greeting(evt):
    import wx, sys
    gui.alert('\n'.join([wx.version(), sys.version]), "gui2py hello world!")

# --- gui2py designer generated code starts ---

gui.Window(name='mywin', title='gui2py minimal app', resizable=True, )
gui.Button(label='Click me!', name='button', default=True, parent='mywin', )

# --- gui2py designer generated code ends ---

# get a reference to the Top Level Window:
mywin = gui.get("mywin")

# assign your event handlers:

mywin['button'].onclick = greeting

if __name__ == "__main__":
    mywin.show()    
    gui.main_loop()
