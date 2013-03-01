
import wx
from ..event import FormEvent
from ..component import Control, Component
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .. import registry
from .. import images


class wx_Panel(wx.Panel):
    "Fake/simple staticbox replacement to group controls" 
     
    def __init__(self, parent, **kwargs):
        if 'label' in kwargs:
            del kwargs['label']
        wx.Panel.__init__(self, parent, **kwargs)


class Panel(Control):
    
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.panel
    
    def __init__(self, *args, **kwargs):
        # for the caption, create a static box with a rectangle around
        # (only in wx2.9, as previous version don't allow children):
        if 'label' in kwargs and kwargs['label'] and wx.VERSION >= (2, 9):
            self._wx_class = wx.StaticBox
        else:
            self._wx_class = wx_Panel
        Control.__init__(self, *args, **kwargs)
        # sane default for tab caption (in designer)

    def rebuild(self, recreate=True, **kwargs):
        "Recreate (if needed) the wx_obj and apply new properties"
        # check if we have children controls, if so, avoid recreating it
        if list(self):
            # just change the spec, this may not affect the visual wx_obj 
            # TODO: proper handle init and style specs
            for spec_name, value in kwargs.items():
                setattr(self, spec_name, value)
        else:
            # warning: the wx_obj will be destroyed
            Control.rebuild(self, recreate, **kwargs)

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

