
import wx
from .event import FormEvent
from .component import Component, Control, Spec, StyleSpec, InitSpec
from . import images
from . import registry


class StatusBar(Component):
    "A simple StatusBar with a single text field."
    _wx_class = wx.StatusBar
    _image = images.statusbar
    _registry = registry.CONTROLS
    
    def __init__(self, parent, **kwargs):        
        Component.__init__(self, parent, **kwargs)        
        
        if wx.Platform == '__WXMAC__':
            self.wx_obj.SetSize((self.wx_obj.GetSizeTuple()[0], 15))

        # only display the resizing grip if the window is resizable
        # the logic below is used because it appears different
        # default flags are used on different platforms

        #self.size_grip = self._parent.resizable
            
        if not self._parent.statusbar:
            self._parent.statusbar = self    # add the statusbar to the parent

    def set_parent(self, new_parent, init=False):
        "Re-parent a child control with the new wx_obj parent"
        Component.set_parent(self, new_parent, init)
        # if new_parent is rebuild, reparent (even to None) to avoid segv:
        if not init:
            wx_obj = new_parent and new_parent.wx_obj
            self.wx_obj.Reparent(wx_obj)
                
    grip = StyleSpec(wx.ST_SIZEGRIP, doc="resizing grip", default=False)
    text = Spec(lambda self: self.wx_obj.GetStatusText(), 
                lambda self, value: self.wx_obj.SetStatusText(value), 
                default="", type="string",
                doc="text displayed in the statusBar")
