#!/usr/bin/python
# -*- coding: utf-8 -*-

"Minimal gui2py application (to be used as skeleton)"

from __future__ import with_statement   # for python 2.5 compatibility

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

import gui                                  

# --- here goes your event handlers ---

def greeting(evt):
    import wx, sys
    gui.alert('\n'.join([wx.version(), sys.version]), "gui2py hello world!")

# --- gui2py designer generated code starts ---

with gui.Window(title=u'gui2py minimal app', resizable=True, height='496px', 
                width='400px', image='', name='mywin'):
    b = gui.Button(label=u'Click me!', name='button', default=True, )

# --- gui2py designer generated code ends ---

mywin = gui.get("mywin")

# assign your event handlers:

mywin['button'].onclick = greeting

if __name__ == "__main__":
    mywin.show()    
    gui.main_loop()
