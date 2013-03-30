#!/usr/bin/python
# -*- coding: utf-8 -*-

"Experimental sample gui2py application demo of sizer usage"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

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
           height='585px', left='180', top='24', width='327px', 
           bgcolor=u'#E0E0E0', image='', sizer=True, tiled=True, )
gui.Button(label=u'Button 1', name='button_109_132', sizer_border=4, 
           width='45%', parent='mywin', )
gui.Button(label=u'Button 2', name='button_172_226', sizer_border=4, 
           width='45%', parent='mywin', )
gui.Button(label=u'Button 3', name='button_240_368', sizer_border=4, 
           parent='mywin', )
gui.Label(name='label_140_120', sizer_align='center', sizer_border=4, 
          width='100px', parent='mywin', )

# --- gui2py designer generated code ends ---


mywin = gui.get("mywin")

if __name__ == "__main__":
    
    mywin.show()
    
    app.MainLoop()
