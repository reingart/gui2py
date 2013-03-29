
import wx
from ..event import FormEvent
from ..component import Control, Component, ImageBackgroundMixin, SizerMixin
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .. import registry
from .. import images


class wx_Panel(wx.Panel):
    "Fake/simple staticbox replacement to group controls" 
     
    def __init__(self, parent, **kwargs):
        if 'label' in kwargs:
            del kwargs['label']
        wx.Panel.__init__(self, parent, **kwargs)


class wx_StaticBoxPanel(wx.Panel):
    "A wx.Panel with an wx.StaticBox to easily group controls" 
     
    def __init__(self, parent, **kwargs):
        label =kwargs['label']
        del kwargs['label']
        wx.Panel.__init__(self, parent, **kwargs)
        # create the static box inside the panel so it is compatible with
        # older wxpython versions (where child controls have to be siblings)
        # and for handling TAB key navigation correctly on childrens
        self.staticbox = wx.StaticBox(self, label=label)
        # use a sizer so the StaticBox has the same size of the parent always
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.staticbox, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    
    def GetLabel(self):
        return self.staticbox.GetLabel()
    
    def SetLabel(self, new_label):
        self.staticbox.SetLabel(new_label)
    
    def Destroy(self):
        "Destroy the static box and panel"
        self.staticbox.Destroy()
        wx.Panel.Destroy(self)


class Panel(Control, ImageBackgroundMixin, SizerMixin):
    "A container to group controls (optionally with a rectangle and title)"
    
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS | wx.TAB_TRAVERSAL
    _image = images.panel
    
    def __init__(self, *args, **kwargs):
        # for the caption, create a static box with a rectangle around
        # (only in wx2.9, as previous version don't allow children):
        if 'label' in kwargs and kwargs['label']:
            self._wx_class = wx_StaticBoxPanel
        else:
            self._wx_class = wx_Panel
        Control.__init__(self, *args, **kwargs)
        # sane default for tab caption (in designer)

    def _get_label(self):
        return self.wx_obj.GetLabel()

    def _set_label(self, new_text):
        if new_text is not None:
            self.wx_obj.SetLabel(new_text)
    
    label = InitSpec(_get_label, _set_label, doc="Title", type='string')


# update metadata for the add context menu at the designer:

Panel._meta.valid_children = [ctr for ctr in registry.CONTROLS.values()
                                 if ctr._image]   # TODO: better filter
 

if __name__ == "__main__":
    import sys
    # basic test until unit_test
    import gui
    app = wx.App(redirect=False)    
    w = gui.Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))

    p = gui.Panel(w, name="panel", label="hello!")
    b = gui.Button(p, name="test", label="click me!")
    
    w.show()
    
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    print wx.version()
    app.MainLoop()

