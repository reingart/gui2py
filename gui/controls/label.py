#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's basic Label control (uses wx.StaticText)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's StaticText component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)

import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from .. import images 


class Label(Control):
    "An uneditable block of text"

    _wx_class = wx.StaticText
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.label

    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        if self.transparent and "__WXMSW__" in wx.Platform:
            # on windows, avoid solid background ("transparent")
            self.wx_obj.Bind(wx.EVT_PAINT, self.__on_paint)

    def _set_text(self, a_string):
        self.wx_obj.SetLabel(a_string)
        if self.size[0] <= 1:
            # adjust default width (to actually show the label)
            self.width = self.wx_obj.GetCharWidth() * len(a_string)
        self.wx_obj.Refresh()
        self.wx_obj.Update()

    def __on_paint(self, event):
        "Custom draws the label when transparent background is needed"
        # use a Device Context that supports anti-aliased drawing 
        # and semi-transparent colours on all platforms
        dc = wx.GCDC(wx.PaintDC(self.wx_obj))
        dc.SetFont(self.wx_obj.GetFont())
        dc.SetTextForeground(self.wx_obj.GetForegroundColour())
        dc.DrawText(self.wx_obj.GetLabel(), 0, 0)
        
    alignment = StyleSpec({'left': wx.ALIGN_LEFT, 
                           'center': wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE,
                           'right': wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE},
                           default='left')
    text = Spec(lambda self: self.wx_obj.GetLabel(), _set_text,
                     default="sample text label...", type="string")


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    t = Label(frame, name="lblTest", alignment="right", text="hello!")
    assert t.get_parent() is frame
    assert t.name == "lblTest"
    print "align", t.alignment
    print "text", t.text
    assert t.text == "hello!"
    from pprint import pprint
    # assign some event handlers:
    t.onmousemove = lambda event: pprint("%s %s %s" % (event.name, event.x, event.y))
    t.onmousedown = lambda event: pprint("click!")
    frame.Show()
    app.MainLoop()
