#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's HTML Top Level Window (uses wx.Frame and gui.HtmlBox)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

# This is an experimental approach to show rich internet applications
# There is no PythonCard equivalent, so code is almost completely new


import wx

from ..component import Component, Spec, InitSpec, EventSpec, StyleSpec
from ..controls import HtmlBox
from ..windows import Window
from ..event import UIEvent


class HtmlWindow(Window):
    "A window that contains a html document (including embedded controls)" 

    def __init__(self, parent=None, **kwargs):
        Window.__init__(self, parent=parent, **kwargs)
        self.html = HtmlBox(self, name="document", scrollbars=True, 
                            left="0", top="0", bgcolor="black", resizable=False,
                            width="auto", height="auto")
        self.html.visible = True
    
    def open(self, location=None):
        if not location:
            print "none!"
            pass
        elif location.startswith(("http://", "https://", "file://")):
            print "loading page", location
            self.html.load_page(location)
        else:
            print "loading file", location
            self.html.load_file(location)
        print "done!"

    def write(self, text):
        self.html.write(text)
        self.html.redraw()
 

if __name__ == "__main__":
    # basic test until proper unit_test
    from ..controls import Button
    app = wx.App(redirect=False)
    w = HtmlWindow(title="hello world", name="frmTest", resizable=True, 
                   visible=False)
    #w.open("http://www.google.com/")
    w.write("<a href='hola'>hello</a")
    w.show()
    app.MainLoop()
