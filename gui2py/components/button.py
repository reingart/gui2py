
import wx
from ..event import FormEvent
from ..widget import Widget, Spec, EventSpec, new_id, widget_metaclass


class Button(Widget):
    "A simple push-button with a label"
    
    __metaclass__ = widget_metaclass
    
    def __init__(self, parent, **kwargs):
        self.wx_obj = wx.Button(parent,
                    new_id(kwargs.get('id')),
                    style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS,
                   )
        Widget.__init__(self, **kwargs)
        ##self.wx_obj.SetLabel(kwargs['label'])
        ##  self._bindEvents(event.WIDGET_EVENTS + ButtonEvents)

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
    b.onclick = lambda event: pprint(event.timestamp)
    b.onblur = b.onfocus = lambda event: pprint(event.name)
    # remove an event handler:
    b.onblur = None
    frame.Show()
    app.MainLoop()