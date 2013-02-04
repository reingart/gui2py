
import wx
from ..event import FormEvent
from ..components import Control, Spec, EventSpec, InitSpec, StyleSpec
from .. import images 


class Label(Control):
    "An uneditable block of text"

    _wx_class = wx.StaticText
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.label

    def _set_text(self, a_string):
        self.wx_obj.SetLabel(a_string)
        if self.size[0] <= 1:
            # adjust default width (to actually show the label)
            self.width = self.wx_obj.GetCharWidth() * len(a_string)
        self.wx_obj.Refresh()
        self.wx_obj.Update()

    alignment = StyleSpec({'left': wx.ALIGN_LEFT, 
                           'center': wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE,
                           'right': wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE},
                           default='center')
    text = Spec(lambda self: self.wx_obj.GetLabel(), _set_text,
                     default="sample text label...", type="string")


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
