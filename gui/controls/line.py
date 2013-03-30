#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's line separator control (uses wx.StaticLine)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's StaticLine component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)

import wx
from ..component import Control, Spec, StyleSpec, InitSpec
from .. import images 


class Line(Control):
    "A simple line (vertical or horizontal) to visually separate controls"
    _wx_class = wx.StaticLine
    _image = images.line
    
    layout = StyleSpec({'vertical': wx.LI_VERTICAL, 
                        'horizontal': wx.LI_HORIZONTAL},  
                        default='horizontal', doc="Line layout")
    label = None

    
if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    b = Line(frame, name="line", layout='vertical')
    frame.Show()
    app.MainLoop()
