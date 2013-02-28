
import wx
from ..event import FormEvent
from ..component import Control, Component
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .. import registry
from .. import images


class Panel(Control):
    
    _wx_class = wx.Panel
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.panel
    
    def __init__(self, *args, **kwargs):
        # caption is handled specially:
        if 'text' in kwargs:
            text = kwargs['text']
            del kwargs['text']
        else:
            text = None
        Control.__init__(self, *args, **kwargs)
        # sane default for tab caption (in designer)

    def _get_label(self):
        return self._parent.wx_obj.GetPageText(self.index)

    def _set_label(self, new_text):
        if self.index and new_text:
            self._parent.wx_obj.SetPageText(self.index, new_text)
    
    #label = Spec(_get_label, _set_label, doc="Title", type='string')


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

    p = Panel(w, name="panel")
    
    w.show()
    
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    app.MainLoop()

