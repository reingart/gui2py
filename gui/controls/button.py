
import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec
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
    onclick = EventSpec('click', binding=wx.EVT_BUTTON, kind=FormEvent)

    
class wx_BitmapButton(wx.BitmapButton):

    def __init__(self, *args, **kwargs):
        # remove label as for bitmap button, it is a image (bitmap)
        if 'label' in kwargs:
            del kwargs['label']
        wx.BitmapButton.__init__(self, *args, **kwargs)
    


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
