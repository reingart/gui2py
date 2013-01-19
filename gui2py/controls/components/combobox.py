import wx
from ..event import FormEvent
from ..widget import Widget, Spec, EventSpec, new_id
from .listbox import ItemContainerWidget


class ComboBox(ItemContainerWidget):
    "A combobox control (textbox + listbox)"

    def __init__(self, parent, readonly=False, **kwargs):
        # required read-only specs:
        style = 0
        self._readonly = readonly
        self._multiselect = False
        if readonly:
            style |= wx.CB_READONLY
        self.wx_obj = wx.ComboBox(
            parent, 
            id=new_id(kwargs.get('id')),
            value='',
            style=style | wx.CB_DROPDOWN | \
                  wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS,
            name=kwargs.get('name'),
        )
        Widget.__init__(self, **kwargs)

    text = Spec(lambda self: self.wx_obj.GetValue(), 
                lambda self, value: self.wx_obj.SetValue(value),
                default="")
    readonly = Spec(lambda self: self._readonly, default=False)

    onclick = onselect = EventSpec('click', 
                                   binding=wx.EVT_COMBOBOX, kind=FormEvent)
    onchange = EventSpec('change', binding=wx.EVT_TEXT, kind=FormEvent)


if __name__ == "__main__":
    import sys
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    c = ComboBox(frame, name="cboTest", border='none', 
                items={'datum1': 'a', 'datum2':'b', 'datum3':'c'},
                readonly='--readonly' in sys.argv,
                )
    c.append("d")
    c.append("e", "datum1")
    c.data_selection = "datum2"
    from pprint import pprint
    # assign some event handlers:
    c.onclick = lambda event: pprint("selection: %s" % str(event.target.selection))
    c.onchange = lambda event: pprint("text: %s" % event.target.text)
    print c.items
    frame.Show()
    app.MainLoop()


