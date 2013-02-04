import wx
from ..event import FormEvent
from ..components import Control, Spec, EventSpec, StyleSpec
from .. import images 


class ItemContainerControl(Control):
    "Interface for all controls that have string subitems wich may be selected"
    
    # internally, uses _items_dict to map strings to client data
    
    def _get_selection(self):
        "Returns the index of the selected item (list for multiselect) or None"
        if self.multiselect:
            return self.wx_obj.GetSelections()
        else:
            sel = self.wx_obj.GetSelection()
            if sel == wx.NOT_FOUND:
                return None
            else:
                return sel

    def _set_selection(self, index):
        "Sets the item at index 'n' to be the selected item."
        if index is None:
            self.wx_obj.SetSelection(-1)
        else:
            self.wx_obj.SetSelection(index)

    def _get_string_selection(self):
        "Returns the label of the selected item or an empty string if none"
        if self.multiselect:
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
    
    def _get_data_selection(self):
        if self.multiselect:
            return [self.wx_obj.GetClientData(i) for i in 
                    self.wx_obj.GetSelections() if i>=0]
        else:
            i = self.wx_obj.GetSelection()
            if i >= 0:
                return self.wx_obj.GetClientData(i)

    def _set_data_selection(self, data):
        # an arg of None or empty string will remove the selection
        if data is None:
            self.wx_obj.SetSelection(-1)
        else:
            if not self.multiselect:
                data = [data]
            elif not isinstance(data, (tuple, list)):
                raise ValueError("data must be a list of values!")
            for datum in data:
                s = self._items_dict[datum]
                i = self.wx_obj.FindString(s)
                self.wx_obj.SetSelection(i)
            
    def _get_items(self):
        items = []
        for i in range(self.wx_obj.GetCount()):
            items.append(self.wx_obj.GetString(i))
        return items

    def _set_items(self, a_iter):
        "Clear and set the strings (and data if any) in the control from a list"

        self._items_dict = {}
        if not a_iter:
            string_list = []
            data_list = []
        elif not isinstance(a_iter, (tuple, list, dict)):
            raise ValueError("items must be an iterable")
        elif isinstance(a_iter, dict):
            # use keys as data, values as label strings
            self._items_dict = a_iter
            string_list = a_iter.values()
            data_list = a_iter.keys()
        elif isinstance(a_iter[0], (tuple, list)) and len(a_iter[0]) == 2:
            # like the dict, but ordered
            self._items_dict = dict(a_iter)
            data_list, string_list = zip(*a_iter)
        else:
            # use the same strings as data
            string_list = a_iter
            data_list = a_iter

        # set the strings
        self.wx_obj.SetItems(string_list)
        # set the associated data
        for i, data in enumerate(data_list):
            self.set_data(i, data)

    def set_data(self, n, data):
        "Associate the given client data with the item at position n."
        self.wx_obj.SetClientData(n, data)
        # reverse association:
        self._items_dict[data] = self.get_string(n)

    def	get_data(self, n):
        "Returns the client data associated with the given item, (if any.)"
        return self.wx_obj.GetClientData(n)

    def append(self, a_string, data=None):
        "Adds the item to the control, associating the given data if not None."
        self.wx_obj.Append(a_string, data)
        # reverse association:
        self._items_dict[data] = a_string        

    def append_items(self, a_list):
        "Apend several items at once to the control."
        self.wx_obj.AppendItems(a_list)

    def clear(self):
        "Removes all items from the control."
        self.wx_obj.Clear()
        self._items_dict = {}

    def delete(self, a_position):
        "Deletes the item at the zero-based index 'n' from the control."
        self.wx_obj.Delete(a_position)
        data = self.get_data()
        if data in self._items_dict:
            del self._items_dict[data]

    def find_string(self, a_string):
        "Finds an item whose label matches the given string"
        return self.wx_obj.FindString(a_string)

    def get_string(self, a_position):
        "Returns the label of the item with the given index."
        return self.wx_obj.GetString(a_position)

    def set_string(self, n, a_string):
        "Sets the label for the given item."
        self.wx_obj.SetString( n, a_string )

    def get_count(self):
        "Returns the number of items in the control."
        return self.wx_obj.GetCount()

    # KEA was getSelected
    def is_selected(self, a_position):
        """Determines whether an item is selected.
        a_position is the zero-based item index
        Returns True if the given item is selected, False otherwise.
        """
        return self.wx_obj.IsSelected(a_position)        
        
    items = Spec(_get_items, _set_items, type="array")
    selection = Spec(_get_selection, _set_selection, type="integer")
    string_selection = Spec(_get_string_selection, _set_string_selection,
                            type="string")
    data_selection = Spec(_get_data_selection, _set_data_selection)


class ListBox(ItemContainerControl):
    "A list that only allows a single item (or multiple items) to be selected."
    
    _wx_class = wx.ListBox
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.listbox

    def insert_items(self, aList, aPosition):
        self.wx_obj.InsertItems(a_list, a_position)

    multiselect = StyleSpec({True: wx.LB_EXTENDED, False: wx.LB_SINGLE}, 
                            default=False)

    onclick = onselect = EventSpec('click', 
                                   binding=wx.EVT_LISTBOX, kind=FormEvent)
    ondblclick = EventSpec('dblclick', 
                                   binding=wx.EVT_LISTBOX_DCLICK, kind=FormEvent)
    

if __name__ == "__main__":
    import sys
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    c = ListBox(frame, name="lstTest", border='none', 
                items={'datum1': 'a', 'datum2':'b', 'datum3':'c'},
                multiselect="--multiselect" in sys.argv)
    c.append("d")
    c.append("e", "datum1")
    c.data_selection = "datum2"
    from pprint import pprint
    # assign some event handlers:
    c.onclick = lambda event: pprint("selection: %s" % str(event.target.selection))
    c.ondblclick = lambda event: pprint(
        "stringselection: %s dataselection: %s" % 
        (str(event.target.string_selection), str(event.target.data_selection)))
    frame.Show()
    app.MainLoop()
