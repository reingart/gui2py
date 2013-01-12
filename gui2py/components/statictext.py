
import wx
from ..event import FormEvent
from ..widget import Widget, Spec, EventSpec, new_id, widget_metaclass


class StaticText(Widget):
    "An uneditable block of text"

    __metaclass__ = widget_metaclass

    def __init__(self, parent, alignment=None, **kwargs):
        self.wx_obj = wx.StaticText(parent, 
                                    new_id(kwargs.get('id')),
                        style=self.__getAlignment(alignment) | \
                        wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS,
                        name=kwargs.get("name"))
        self._alignment = alignment
        Widget.__init__(self, **kwargs)

    def __getAlignment(self, aString):
        if not aString or aString == 'left':
            return wx.ALIGN_LEFT
        elif aString == 'center':
            return wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
        elif aString == 'right':
            return wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE
        else:
            raise 'invalid StaticText.alignment value: ', aString

    def _setText(self, aString):
        self.wx_obj.SetLabel(aString)
        self.wx_obj.Refresh()
        self.wx_obj.Update()

    def _getAlignment(self):
        return self._alignment

    alignment = Spec(_getAlignment, None,
                     values=[ 'left', 'right', 'center'])
    text = Spec(lambda self: self.wx_obj.GetLabel(), _setText,
                     default="StaticText")


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    t = StaticText(frame, name="lblTest", text="hello!")
    assert t.get_parent() is frame
    assert t.name == "lblTest"
    print "align", t.alignment
    print "text", t.text
    assert t.text == "hello!"
    from pprint import pprint
    # assign some event handlers:
    t.onmousemove = lambda event: pprint("%s %s %s" % (event.name, event.x, event.y))
    frame.Show()
    app.MainLoop()