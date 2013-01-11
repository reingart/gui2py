
import wx
from ..event import EventHandler, FormEvent
from ..widget import Widget, Spec, new_id


class Button(Widget):
    "A simple push-button with a label"

    specs = Widget.specs + [
            Spec('label', optional=False, default='Button'),
            Spec('default', optional=False, default=False),
            ]
    handlers = Widget.handlers + [
            EventHandler('click', binding=wx.EVT_BUTTON, kind=FormEvent),
        ]
    
    def create(self, parent, **kwargs):
        self.wx_obj = wx.Button(parent,
                    new_id(kwargs.get('id')),
                    style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS,
                   )
        Widget.create(self, **kwargs)
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

    default = property(_getDefault, _setDefault)
    label = property(lambda self: self.wx_obj.GetLabel(), 
                     lambda self, label: self.wx_obj.SetLabel(label))



if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    b = Button()
    b.create(frame, name="btnTest", label="click me!", default=True)
    assert b.get_parent() is frame
    assert b.name == "btnTest"
    assert b.default == True
    print b.label
    assert b.label == "click me!"
    def my_action(evt):
        print evt.name
        print evt.target
    b.bind("click", my_action)
    frame.Show()
    app.MainLoop()