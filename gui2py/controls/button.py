
import wx
from ..event import FormEvent
from ..components import Control, Spec, EventSpec


class Button(Control):
    "A simple push-button with a label"
    _wx_class = wx.Button
    
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

    default = Spec(_getDefault, _setDefault, default=False)
    label = Spec(lambda self: self.wx_obj.GetLabel(), 
                 lambda self, label: self.wx_obj.SetLabel(label),
                 optional=False, default='Button')
    onclick = EventSpec('click', binding=wx.EVT_BUTTON, kind=FormEvent)



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