import wx
from ..event import FormEvent
from ..components import Control, Spec, EventSpec, new_id


class CheckBox(Control):
    "A check box."
    
    _wx_class = wx.CheckBox
    _style = wx.CLIP_SIBLINGS | wx.NO_FULL_REPAINT_ON_RESIZE
        
    checked = Spec(lambda self: self.wx_obj.GetValue(), 
                   lambda self, value: self.wx_obj.SetValue(value), 
                   default=False, type="boolean")
    label = Spec(lambda self: self.wx_obj.GetLabel(), 
                 lambda self, value: self.wx_obj.SetLabel(value),
                 type="string")

    onclick = EventSpec('click', binding=wx.EVT_CHECKBOX, kind=FormEvent)


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    c = CheckBox(frame, name="chkTest", border='none', label="Check me!")
    assert c.get_parent() is frame
    assert c.name == "chkTest"
    assert c.label == "Check me!"
    from pprint import pprint
    # assign some event handlers:
    c.onclick = lambda event: pprint("click: %s" % event.target.checked)
    frame.Show()
    app.MainLoop()
