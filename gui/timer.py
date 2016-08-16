#!/usr/bin/python
# -*- coding: utf-8 -*-

"Timer support "

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2016- Mariano Reingart"
__license__ = "LGPL 3.0"

import wx

from .component import SubComponent, Spec
from . import images
from . import registry


class Timer(SubComponent):
    "A simple timer to execute code at specified intervals"
    _wx_class = wx.Timer
    #_image = images.statusbar
    _registry = registry.MISC
    
    def __init__(self, parent=None, **kwargs):
        "Custom constructor that just creates the wx.Timer instance"
        self.wx_obj = self._wx_class(None)
        self.set_parent(parent, init=True)

    def set_parent(self, new_parent, init=False):
        "Re-parent a child control with the new wx_obj parent (owner)"
        ##SubComponent.set_parent(self, new_parent, init)
        self.wx_obj.SetOwner(new_parent.wx_obj.GetEventHandler())

    def stop(self):
        self.wx_obj.Stop()
    
    def start(self, interval=-1):
        self.wx_obj.Start(interval)

    interval = Spec(lambda self: self.wx_obj.GetInterval(), 
                lambda self, value: self.wx_obj.Start(value),
                default=1000, type="integer",
                doc="current interval for the timer (in milliseconds)")


if __name__ == "__main__":
    from gui.windows import Window
    app = wx.App(redirect=False)

    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
    t = Timer(w)
    def timer(evt):
        print("timer!")
    w.ontimer = timer
    t.interval = 100
    w.show()
    app.MainLoop()


