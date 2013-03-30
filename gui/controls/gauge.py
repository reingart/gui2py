#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Gauge (a.k.a. progress bar) control (uses wx.Gauge)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's Gauge component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)

import wx
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from .. import images


class Gauge(Control):
    "A gauge component (progress bar which shows a quantity (often time)"

    _wx_class = wx.Gauge
    _style = (wx.GA_SMOOTH | 
                wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS)
    _image = images.gauge
    

    layout = StyleSpec({'horizontal': wx.GA_HORIZONTAL, 
                        'vertical': wx.GA_VERTICAL},
                        default="horizontal",
                        doc="appareance")
    max = Spec(lambda self: self.wx_obj.GetRange(), 
               lambda self, value: self.wx_obj.SetRange(value),
               default=100, type="integer",
               doc="Range of the gauge")
    value = Spec(lambda self: self.wx_obj.GetValue(), 
                 lambda self, value: self.wx_obj.SetValue(value),
                 default=0, type="integer",
                 doc="Current value (position of the gauge)")

