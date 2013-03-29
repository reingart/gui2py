#!/usr/bin/python
# -*- coding: utf-8 -*-

"Sample gui2py application demo of sizer usage"

import datetime
import decimal
import wx
import os

app = wx.GetApp()
if app is None:
    app = wx.App(False)

# disable ubuntu unified menu
os.environ['UBUNTU_MENUPROXY'] = '0'

import gui

# --- gui2py designer generated code starts ---

gui.Window(name='mywin', title=u'gui2py sizers demo', resizable=True, 
           height='640px', left='180', top='24', width='355px', 
           bgcolor=u'#E0E0E0', image='', sizer=True, tiled=True, )
gui.Button(label=u'Button 1', name='button_109_132', width='45%', 
           parent='mywin', )
gui.Button(label=u'Button 2', name='button_172_226', width='45%', 
           parent='mywin', )
gui.Button(label=u'Button 3', name='button_240_368', parent='mywin', )
gui.Label(name='label_140_120', width='100px', parent='mywin', )

# --- gui2py designer generated code ends ---


mywin = gui.get("mywin")

if __name__ == "__main__":
    
    mywin.show()
    
    app.MainLoop()
