#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py application example using a resource"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"


import gui


def on_load(evt):
    print "initializing!"
    window['mypanel']['mybutton'].label = "Click ME!!!!"
    window.show()

def on_menu_file_about_click(event):
    pass

def on_menu_file_exit_click(evt):
    window.close()
    
def on_field1_change(evt):
    print "Changed, new text: ", window['field1'].value

def on_field1_keypress(evt):
    print "Keypress: ", evt.key
    if evt.key == 13:
        gui.alert(window['field1'].value, "hello world!")
    
def on_mypanel_mybutton_click(etv):
    gui.alert("btn clicked!!!!")
        

if __name__ == '__main__':
    window = gui.load()
    gui.main_loop()

