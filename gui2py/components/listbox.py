import wx
from ..event import FormEvent
from ..widget import Widget, Spec, EventSpec, new_id


class ItemContainerWidget(Widget):
    "Interface for all controls that have string subitems wich may be selected"

    def _get_selection(self):
        if self._multiselect:
            return self.wx_obj.GetSelections()
        else:
            sel = self.wx_obj.GetSelection()
            if sel == wx.NOT_FOUND:
                return None
            else:
                return sel

    def _set_selection(self, index):
        if index is None:
            self.wx_obj.SetSelection(-1)
        else:
            self.wx_obj.SetSelection(index)

    def _get_string_selection(self):
        if self._multiselect:
            return [self.wx_obj.GetString(i) for i in 
                    self.wx_obj.GetSelections()]
        else:
            return self.wx_obj.GetStringSelection()

    def _set_string_selection(self, s):
        # an arg of None or empty string will remove the selection
        if s is None or s == '':
            self.wx_obj.SetSelection(-1)
        else:
            self.wx_obj.SetStringSelection(s)

    def _get_items(self):
        items = []
        for i in range(self.GetCount()):
            items.append(self.GetString(i))
        return items

    def _set_items(self, a_list):
        self.wx_obj.Set(a_list)

    def append(self, a_string):
        self.wx_obj.Append(a_string)

    def append_items(self, a_list):
        self.wx_obj.AppendItems(a_list)

    def clear(self):
        self.wx_obj.Clear()

    def delete(self, a_position):
        self.Delete(a_position )

    def find_string(self, a_string):
        return self.wx_obj.FindString(a_string)

    def get_string(self, a_position):
        return self.wx_obj.GetString(a_position)

    items = Spec(_get_items, _set_items)
    selection = Spec(_get_selection, _set_selection)
    string_selection = Spec(_get_string_selection, _set_string_selection)


class ListBox(ItemContainerWidget):
    "A list that only allows a single item (or multiple items) to be selected."
    
    def __init__(self, parent, multiselect=False, **kwargs):
    
        # required read-only specs:
        style = 0
        self._multiselect = multiselect
        if multiselect:
            style |= wx.LB_EXTENDED
        else:
            style |= wx.LB_SINGLE
        
        self.wx_obj = wx.ListBox(
            parent, 
            id=new_id(kwargs.get('id')),
            style=style | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS,
            name=kwargs.get('name'),
        )

        Widget.__init__(self, **kwargs)

    def insert_items(self, aList, aPosition):
        self.wx_obj.InsertItems(a_list, a_position)

    def get_count(self):
        return self.wx_obj.GetCount()

    # KEA was getSelected
    def is_selected(self, a_position):
        """Determines whether an item is selected.
        a_position is the zero-based item index
        Returns True if the given item is selected, False otherwise.
        """
        return self.wx_obj.IsSelected(a_position)

    def set_string( self, n, a_string ) :
        self.wx_obj.SetString( n, a_string )

    multiselect = Spec(lambda self: self._multiselect, default=False)

    onclick = onselect = EventSpec('click', 
                                   binding=wx.EVT_LISTBOX, kind=FormEvent)
    ondblclick = EventSpec('dblclick', 
                                   binding=wx.EVT_LISTBOX_DCLICK, kind=FormEvent)
    

if __name__ == "__main__":
    import sys
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    c = ListBox(frame, name="lstTest", border='none', items=['a', 'b', 'c'],
                multiselect="--multiselect" in sys.argv)
    from pprint import pprint
    # assign some event handlers:
    c.onclick = lambda event: pprint("selection: %s" % str(event.target.selection))
    c.ondblclick = lambda event: pprint("selection: %s" % str(event.target.string_selection))
    frame.Show()
    app.MainLoop()