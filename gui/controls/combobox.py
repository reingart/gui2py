#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's ComboBox control (uses wx.ComboBox - wx.Choice is not used by now)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's ComboBox component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)

import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from .listbox import ItemContainerControl
from .. import images 


class ComboBox(ItemContainerControl):
    "A combobox control (textbox + listbox)"

    _wx_class = wx.ComboBox
    _style = wx.CB_DROPDOWN | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.combobox
    
    multiselect = False    # required by ItemContainerControl
    
    text = InitSpec(lambda self: self.wx_obj.GetValue(), 
                lambda self, value: self.wx_obj.SetValue(value),
                default="", type="string", _name="_value")
    readonly = StyleSpec(wx.CB_READONLY, default=False)

    onclick = onselect = EventSpec('click', 
                                   binding=wx.EVT_COMBOBOX, kind=FormEvent)
    onchange = EventSpec('change', binding=wx.EVT_TEXT, kind=FormEvent)


if __name__ == "__main__":
    import sys
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    c = ComboBox(frame, name="cboTest",
                items={'datum1': 'a', 'datum2':'b', 'datum3':'c'},
                readonly='--readonly' in sys.argv,
                )
    c.append("d")
    c.append("e", "datum1")
    c.data_selection = "datum2"
    from pprint import pprint
    # assign some event handlers:
    c.onclick = lambda event: pprint("selection: %s" % str(event.target.selection))
    c.onchange = lambda event: pprint("text: %s" % event.target.text)
    print c.items
    frame.Show()
    app.MainLoop()


