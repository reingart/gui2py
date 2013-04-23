#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Button control (uses wx.Button and wx.BitmapButton)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's Button component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)

import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from .image import Image
from .. import images 


class Button(Image):
    "A simple push-button with a label (or image)"
    _wx_class = wx.Button
    _image = images.button
    
    def __init__(self, parent=None, **kwargs):
        if 'filename' in kwargs and kwargs['filename']:
            self._wx_class = wx_BitmapButton
            kwargs['label'] = ''
            ##if 'border' in kwargs and kwargs['border'] == 'default':
            ##  kwargs['border'] = 'none'
            ##  kwargs['auto_redraw'] = True # Windows specific ?!
                
        # TODO: refactor for Disabled, Focus, Hover, Selected bitmap support
        # Use the common image contructor (TODO: ImageMixin!)
        Image.__init__(self, parent, **kwargs)
    
    def _getDefault(self):
        #return self == self._parent.GetDefaultItem()
        # KEA 2002-03-26
        # for some reason wxDialog doesn't have a
        # GetDefaultItem and SetDefaultItem
        return self._default

    def _setDefault(self, aBoolean):
        self._default = aBoolean
        if aBoolean:
            self.wx_obj.SetDefault()

    default = Spec(_getDefault, _setDefault, default=False, type="boolean")
    label = InitSpec(lambda self: self.wx_obj.GetLabel(), 
                     lambda self, label: self.wx_obj.SetLabel(label),
                     optional=False, default='Button', type="string", 
                     doc="text to show as caption")
    auto_redraw = StyleSpec(wx.BU_AUTODRAW, default=False,
        doc="drawn automatically using bitmap only, providing a 3D-look border")
    exact_fit = StyleSpec(wx.BU_EXACTFIT, default=False,
        doc="small as possible instead of standard size (which is the default)")
    onclick = EventSpec('click', binding=wx.EVT_BUTTON, kind=FormEvent)

    
class wx_BitmapButton(wx.BitmapButton):

    def __init__(self, *args, **kwargs):
        # remove label as for bitmap button, it is a image (bitmap)
        if 'label' in kwargs:
            del kwargs['label']
        wx.BitmapButton.__init__(self, *args, **kwargs)
    
    # WORKAROUND: 2.8 has no SetBitmap: 
    if wx.VERSION < (2, 9):
        def SetBitmap(self, bitmap):
            self.SetBitmapLabel(bitmap)


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    b = Button(frame, name="btnTest", label="click me!", default=True)
    assert b.get_parent() is frame
    assert b.name == "btnTest"
    assert b.default == True
    assert b.label == "click me!"
    from pprint import pprint
    # assign some event handlers:
    b.onclick = "print event.timestamp; event.prevent_default()"
    b.onblur = b.onfocus = lambda event: pprint(event.name)
    # remove an event handler:
    b.onblur = None
    frame.Show()
    app.MainLoop()
