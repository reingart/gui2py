#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Event Model (encapsulates wx.Event)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

# Initial implementation was inspired on PythonCard's event module, altought
# it was almost completely discarded and re-written from scratch to make it
# simpler and mimic web (html/javascript) event models

# References
# https://developer.mozilla.org/en-US/docs/Mozilla_event_reference
# http://wxpython.org/docs/api/wx.Event-class.html

import time


class Event:
    "Generic Event Object: holds actual event data (created by EventHandler)"
    
    cancel_default = False # flag to avoid default (generic) handlers
        
    def __init__(self, name="", wx_event=None):
        self.wx_event = wx_event
        # retrieve wxPython event properties:
        wx_obj = self.wx_event.GetEventObject()
        self.target = wx_obj.obj if wx_obj else None
        self.timestamp = wx_event.GetTimestamp()
        # check if timestamp (wx report it only for mouse or keyboard)
        if not self.timestamp:
            self.timestamp = time.time()  # create a new timestamp if not given
        self.name = name                  # name (type), i.e.: "click"

    def prevent_default(self, cancel=True):
        self.wx_event.Skip(not cancel)
        self.cancel_default = cancel

    def stop_propagation(self):
        self.wx_event.StopPropagation()


class UIEvent(Event):
    "General -window- related events (detail can hold additional data)"   
    names = ["load", "resize", "scroll", "paint", "unload"]

    def __init__(self, name, detail=None, wx_event=None):
        Event.__init__(self, name, wx_event)
        self.detail = detail

    def prevent_default(self):
        if self.name == 'unload':
            if self.wx_event.CanVeto():
                self.wx_event.Veto()
            else:
                raise RuntimeError("Cannot Veto!")
        else:
            Event.prevent_default(self)     # call default implementation


class FocusEvent(Event):
    "Focus related events"
    
    names = ["focus", "blur"]


class FormEvent(Event):
    "Form HTML-like events "
    
    names = ["select", "change", "reset", "submit", "invalid"]
    cancel_default = True # command events should not escalate
    

class SubmitEvent(FormEvent):
    "Form submission handler (includes HTML form data and field contents)"
    def __init__(self, name, wx_event=None):
        Event.__init__(self, name, wx_event)
        self.form = wx_event.form
        self.data = wx_event.data


class MouseEvent(Event):
    "Mouse related events (wrapper for wx.MouseEvent)"
    
    names = ["click", "dblclick", "mousedown", "mousemove",
            "mouseout", "mouseover", "mouseup", "mousewheel"]

    def __init__(self, name, wx_event=None):
        Event.__init__(self, name, wx_event)
        self.x = wx_event.GetX()
        self.y = wx_event.GetY()
        self.alt_key = wx_event.AltDown()
        self.ctrl_key = wx_event.ControlDown()
        self.shift_key = wx_event.ShiftDown()
        self.meta_key = wx_event.MetaDown()
        self.left_button = wx_event.LeftIsDown()
        self.right_button = wx_event.RightIsDown()
        self.middle_button = wx_event.MiddleIsDown()
        if name=="mousewheel":
            self.wheel_delta = wx_event.GetWheelDelta()

class KeyEvent(Event):
    "Keyboard related event (wrapper for wx.KeyEvent)"
    # only sent to the widget that currently has the keyboard focus
    
    names = "onkeypress", "onkeydown", "onkeyup",
    
    def __init__(self, name, wx_event=None):
        Event.__init__(self, name, wx_event)
        self.ctrl_key = wx_event.ControlDown()
        self.shift_key = wx_event.ShiftDown()
        self.alt_key = wx_event.AltDown()
        self.meta_key = wx_event.MetaDown()
        self.key = wx_event.KeyCode                   # virtual key code value
        self.char = unichr(wx_event.GetUnicodeKey())  # Unicode character

        
class TimingEvent(Event):
    "Time interval events"   
    names = ["idle", "timer"]

    def __init__(self, interval=None, wx_event=None):
        Event.__init__(self, wx_event)
        self.interval = interval

    def request_more(self):
        pass        #wx.RequestMore(needMore=True)


class HtmlLinkEvent(UIEvent):
    "Html hyperlink click event (href and target)"
    
    def __init__(self, name, detail=None, wx_event=None):
        UIEvent.__init__(self, name, wx_event=wx_event, 
                         detail=wx_event.GetLinkInfo().GetHtmlCell())
        self.href = wx_event.GetLinkInfo().GetHref()
        self.target = wx_event.GetLinkInfo().GetTarget()

        
class HtmlCellEvent(MouseEvent):
    "Html Cell click / hover events"
    
    def __init__(self, name, detail=None, wx_event=None):
        MouseEvent.__init__(self, name, wx_event.GetMouseEvent())
        self.detail = wx_event.GetCell()
        self.point = wx_event.GetPoint()


class HtmlCtrlClickEvent(UIEvent):
    "Html Control click "
    
    def __init__(self, name, detail=None, wx_event=None):
        UIEvent.__init__(self, name, wx_event=wx_event, 
                         detail=wx_event.ctrl)


class TreeEvent(UIEvent):
    "Tree Control events (detail has the selected/extended/collapsed item)"
    
    def __init__(self, name, detail=None, wx_event=None):
        wx_tree = wx_event.GetEventObject()
        model = wx_tree.obj.items
        wx_item = wx_event.GetItem()
        if not wx_item.IsOk():
            wx_item = wx_tree.GetSelection()
        UIEvent.__init__(self, name, wx_event=wx_event, 
                         detail=model(wx_item))


class GridEvent(UIEvent):
    "Grid Control events (mouse, size, edit, etc.)"
    
    def __init__(self, name, detail=None, wx_event=None):
        wx_tree = wx_event.GetEventObject()
        ##model = wx_tree.obj.items
        try:
            self.row = wx_event.GetRow()
            self.column = wx_event.GetCol()
            self.position = wx_event.GetPosition()
        except:
            pass
        UIEvent.__init__(self, name, wx_event=wx_event, 
                         detail=model(wx_item))


WIDGET_EVENTS = MouseEvent, FocusEvent, TimingEvent
