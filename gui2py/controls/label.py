
import wx
from ..event import FormEvent
from ..components import Control, Spec, EventSpec, InitSpec, StyleSpec


class Label(Control):
    "An uneditable block of text"

    _wx_class = wx.StaticText
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS

    def _setText(self, aString):
        self.wx_obj.SetLabel(aString)
        self.wx_obj.Refresh()
        self.wx_obj.Update()

    alignment = StyleSpec({'left': wx.ALIGN_LEFT, 
                           'center': wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE,
                           'right': wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE},
                           default='left')
    text = Spec(lambda self: self.wx_obj.GetLabel(), _setText,
                     default="Label")


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    t = Label(frame, name="lblTest", alignment="right", text="hello!")
    assert t.get_parent() is frame
    assert t.name == "lblTest"
    print "align", t.alignment
    print "text", t.text
    assert t.text == "hello!"
    from pprint import pprint
    # assign some event handlers:
    t.onmousemove = lambda event: pprint("%s %s %s" % (event.name, event.x, event.y))
    t.onmousedown = lambda event: pprint("click!")
    frame.Show()
    app.MainLoop()