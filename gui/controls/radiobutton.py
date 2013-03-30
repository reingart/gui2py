#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's RadioButton for mutual exclusive options (uses wx.RadioButton)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Note: Pythoncard didn't implemented this, so the code is almost completely new
#       BTW, pythoncard used RadioGroup that is not implemented at all in gui2py
#       if you need that functionality, just use RadioButtons inside a Panel

import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from .. import images


class RadioButton(Control):
    "A button which usually denotes one of several mutually exclusive options"
    
    _wx_class = wx.RadioButton
    _style = wx.CLIP_SIBLINGS | wx.NO_FULL_REPAINT_ON_RESIZE
    _image = images.radio_button
        
    group = StyleSpec(wx.RB_GROUP, default=False,
                      doc="Marks the beginning of a new group of radio buttons")
    single = StyleSpec(wx.RB_SINGLE, default=False,
                      doc="mark the button as not belonging to a group, "
                          "implement the mutually-exclusive behaviour yourself")
                            
    value = Spec(lambda self: self.wx_obj.GetValue(), 
                   lambda self, value: self.wx_obj.SetValue(value), 
                   default=False, type="boolean")
    label = InitSpec(lambda self: self.wx_obj.GetLabel(), 
                     lambda self, value: self.wx_obj.SetLabel(value),
                     type="string", default="Option")

    onclick = EventSpec('click', binding=wx.EVT_RADIOBUTTON, kind=FormEvent)


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    c1 = RadioButton(frame, name="opt1", label="Option 1", group=True)
    c2 = RadioButton(frame, name="opt2", label="Option 2", top=c1.size[1])
    c3 = RadioButton(frame, name="opt3", label="Option 3", top=c1.size[1]*2)
    assert c1.get_parent() is frame
    # assign some event handlers:
    c1.onclick = "print 'click:', event.target.name, event.target.value"
    c3.onclick = c2.onclick = c1.onclick
    frame.Show()
    app.MainLoop()
