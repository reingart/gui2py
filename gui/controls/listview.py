import wx
from ..event import FormEvent
from ..component import Control, SubComponent
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .listbox import ItemContainerControl
from .. import images 
from .. import registry
from types import TupleType, ListType, StringTypes, NoneType, IntType, DictType

from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin


class wx_ListCtrl(wx.ListCtrl, ColumnSorterMixin, ListCtrlAutoWidthMixin):

    def __init__(self, *args,  **kwargs):
        #if 'max_columns' in kwargs:
        max_columns = kwargs.pop('max_columns')
        wx.ListCtrl.__init__(self, *args, **kwargs)
        # Now that the list exists we can init the other base class,
        # see wxPython/lib/mixins/listctrl.py
        ColumnSorterMixin.__init__(self, max_columns)

        # Perform init for AutoWidth (resizes the last column to take up
        # the remaining display width)
        ListCtrlAutoWidthMixin.__init__(self)
        
        # maps for PyData support (like TreeCtrl)
        self._py_data_map = {}
        self._wx_data_map = {}

    # Used by the wxColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    def GetColumnSorter(self):
        """Returns a callable object to be used for comparing column values when sorting."""
        return self.__ColumnSorter

    def OnGetItemText(self, item, col):
        if self.obj and self.obj._ongetitemdata:
            return self.obj._ongetitemdata(item, col)

    # Allow to store arbitrary python data (like TreeCtrl PyData) 
    # (ListCtrl supports only long as item data type)
    # For more info see: http://wiki.wxpython.org/ListControls
    
    def GetPyData(self, item):
        "Returns the pyth item data associated with the item"
        wx_data = self.GetItemData(item)
        py_data = self._py_data_map.get(wx_data)
        return py_data

    def SetPyData(self, item, py_data):
        "Set the python item data associated wit the wx item"
        wx_data = wx.NewId()                           # create a suitable key
        self.SetItemData(item, wx_data)   # store it in wx 
        self._py_data_map[wx_data] = py_data           # map it internally
        self._wx_data_map[py_data] = wx_data           # reverse map
        return wx_data

    def FindPyData(self, start, py_data):
        "Do a reverse look up for an item containing the requested data"
        # first, look at our internal dict:
        wx_data = self._wx_data_map[py_data]
        # do the real search at the wx control:
        return self.FindItemData(start, wx_data)

    def DeleteItem(self, item):
        "Remove the item from the list and unset the related data"
        wx_data = self.GetItemData(item)
        py_data = self._py_data_map[wx_data]
        del self._py_data_map[wx_data]
        del self._wx_data_map[py_data]
        wx.ListCtrl.DeleteItem(self, item)

    def DeleteAllItems(self):
        "Remove all the item from the list and unset the related data"
        self._py_data_map.clear()
        self._wx_data_map.clear()
        wx.ListCtrl.DeleteAllItems(self)

    def __ColumnSorter(self, wx_key1, wx_key2):
        py_key1 = self._py_data_map[wx_key1]
        py_key2 = self._py_data_map[wx_key2]
        return ColumnSorterMixin._ColumnSorterMixin__ColumnSorter(self, py_key1, py_key2)


class ListView(Control):
    "A multi-column list (wx.ListCtrl)"

    _wx_class = wx_ListCtrl
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.list_ctrl

    def __init__(self, parent=None, **kwargs):
        # default sane values (if not init'ed previously):
        if not hasattr(self, "_items"):
            self._max_columns = 99
        Control.__init__(self, parent, **kwargs)

    # Emulate some listBox methods

    def clear(self):
        self._items.clear()

    def get_count(self):
        "Get the item (row) count"
        return self.wx_obj.GetItemCount()
    
    def set_count(self, value):
        "Set item (row) count -useful only in virtual mode-"
        if self.view == "report" and self.virtual and value is not None:
            self.wx_obj.SetItemCount(value)

    def get_selected_items(self):
        return [it for it in self.items if it.selected]

    def append(self, a_list):
        self.insert_items(a_list, self.wx_obj.GetItemCount())

    def insert_items(self, a_list, index=-1):
        if not isinstance(a_list, (ListType, TupleType, DictType)):
            raise AttributeError("unsupported type, list expected")
        elif not a_list:
            return
        # calculate the zero-based index position (-1 like python lists)
        index = max(self.get_count() + index + 1, 0) if index < 0 else index
        if isinstance(a_list, DictType):
            for i, (key, a_item) in enumerate(a_list.items()):
                self._items.add(index + i, key, a_item)
        else:
            for i, a_item in enumerate(a_list):
                self._items.add(index + i, None, a_item)

    def delete(self, a_position):
        "Deletes the item at the zero-based index 'n' from the control."
        key = self.wx_obj.GetPyData(a_position)
        del self._items[key]
 
    def _get_items(self):
        return self._items

    def _set_items(self, a_list):
        if isinstance(a_list, NoneType):
            a_list = []
        elif not isinstance(a_list, (ListType, TupleType, DictType)):
            raise AttributeError("unsupported type, list/tuple/dict expected")

        self._items = ListModel(self)
        self.wx_obj.itemDataMap = self._items

        self.insert_items(a_list)
    
    def _get_sort_column(self):
        return self.wx_obj.GetSortState()[0]

    def _set_sort_column(self, col=None):
        order = +1 if self.sort_order=='ascending' else -1
        if col is not None:
            wx.CallAfter(self.wx_obj.SortListItems, col, order)

    def _get_column_headings(self):
        "Return a list of children sub-components that are column headings"
        # return it in the same order as inserted in the ListCtrl
        headers = [ctrl for ctrl in self if isinstance(ctrl, ListColumn)]
        return sorted(headers, key=lambda ch: ch.index)

    view = StyleSpec({'report': wx.LC_REPORT,
                      'list': wx.LC_LIST,
                      'icon': wx.LC_ICON,
                      'small icon': wx.LC_SMALL_ICON}, default='report') 
    hrule = StyleSpec(wx.LC_HRULES, 
                doc="Draws light horizontal rules between rows (report mode).")
    vrule = StyleSpec(wx.LC_VRULES, 
                doc="Draws light vertical rules between rows (report mode).")
    multiselect = StyleSpec({True: 0, False: wx.LC_SINGLE_SEL}, 
                default=True, doc="Allow multiple selection")
    hide_headers = StyleSpec(wx.LC_NO_HEADER, default=False,
                        doc="No header in report mode")
    
    virtual = StyleSpec(wx.LC_VIRTUAL, default=False,
            doc="The application provides items text on demand (report mode)")
    
    max_columns = InitSpec(lambda self: self._max_columns, default=99, 
                           doc="Maximum number of columns (for Sort mixin)")
    
    columns = InternalSpec(_get_column_headings,
                           doc="Return a list of current column headers")
    items = InternalSpec(_get_items, _set_items)
   
    item_count = Spec(get_count, set_count,
        default=None,
        doc="indicate to the control the number of items it contains (virtual)")
    
    sort_order = Spec(mapping={'ascending': wx.LC_SORT_ASCENDING,
                               'descending': wx.LC_SORT_DESCENDING,}, 
                      default='ascending', _name="_sort_order", type="enum",
                      doc="Sort order (auto sort mixin)")
    sort_column = Spec(_get_sort_column, _set_sort_column,
                       doc="Column used in auto sort mixin", type='integer')
    ongetitemdata = InternalSpec(_name="_ongetitemdata",
                    default=lambda row, col: "row %d column %d" % (row, col),
                    doc="Function to get the str for item/col (virtual mode)")

    # events:
    onitemselected = EventSpec('item_selected', 
                           binding=wx.EVT_LIST_ITEM_SELECTED, kind=FormEvent)
    onitemactivated = EventSpec('item_activated', 
                           binding=wx.EVT_LIST_ITEM_ACTIVATED, kind=FormEvent)
    onitemfocused = EventSpec('item_focused', 
                           binding=wx.EVT_LIST_ITEM_FOCUSED, kind=FormEvent)
    onitemcontext = EventSpec('item_context', 
                           binding=wx.EVT_LIST_ITEM_RIGHT_CLICK, kind=FormEvent)
    onlistkeydown = EventSpec('list_key_down', 
                           binding=wx.EVT_LIST_KEY_DOWN, kind=FormEvent)
    oncolumnclick = EventSpec('column_click', 
                           binding=wx.EVT_LIST_COL_CLICK, kind=FormEvent)


class ListColumn(SubComponent):
    "ListView sub-component to handle heading, align and width of columns"

    _created = False
    _registry = registry.MISC
    
    def set_parent(self, new_parent, init=False):
        "Associate the header to the control (it could be recreated)"
        self._created = False
        SubComponent.set_parent(self, new_parent, init)
        # if index not given, append the column at the last position:
        if self.index == -1 or self.index > self._parent.wx_obj.GetColumnCount():
            self.index = self._parent.wx_obj.GetColumnCount()
        # insert the column in the listview:
        self._parent.wx_obj.InsertColumn(self.index, self.text, self._align, 
                                         self.width)
        self._created = True    # enable setattr hook

    def __setattr__(self, name, value):
        "Hook to update the column information in wx"
        object.__setattr__(self, name, value)
        if name not in ("_parent", "_created") and self._created:
            # get the internal column info (a.k.a. wx.ListItem)
            info = self._parent.wx_obj.GetColumn(self.index)
            if name == "_text":
                info.SetText(value)
            elif name == "_width":
                info.SetWidth(value)
            elif name == "_align":
                info.SetAlign(value)
            self._parent.wx_obj.SetColumn(self.index, info)     # update it...

    name = InitSpec(optional=False, default="", _name="_name", type='string')
    text = InitSpec(optional=False, default="", _name="_text", type='string')
    index = InitSpec(optional=False, default=-1, _name="_index", type='integer')
    align = InitSpec(mapping={'left': wx.LIST_FORMAT_LEFT,
                              'center': wx.LIST_FORMAT_CENTRE,
                              'right': wx.LIST_FORMAT_RIGHT}, 
                     default='left', _name="_align", type="enum",
                     doc="Column Format")
    width = InitSpec(default=wx.LIST_AUTOSIZE, _name="_width", type="integer",
                     doc="Column width (default=autosize)")
    represent = InitSpec(default=lambda v: v, _name="_represent", type='string',
                     doc="function to returns a representation for the subitem")


class ListModel(dict):
    "ListView Items model map"
    
    def __init__(self, _list_view):
        self._list_view = _list_view
        self.clear()

    def __setitem__(self, key, kwargs):
        self.add(key=key, kwargs=kwargs)

    def add(self, index=-1, key=None, kwargs=None):
        # convert item to dict if given as list / str
        if isinstance(kwargs, basestring):
            kwargs = [kwargs]
        if isinstance(kwargs, list):
            kwargs = dict([(col.name, kwargs[col.index]) for col
                          in self._list_view.columns if col.index<len(kwargs)])
        if key is None:
            key = self._new_key()
        # check if we have to update the ListCtrl:
        update = key in self
        # create the new item
        item = ListItem(self, key, **kwargs)
        dict.__setitem__(self, key, item)       # add the key/value to the dict
        if update:
            self._update(key)
        else:
            self._insert(key, index)            # do the insert in the control
        return item

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        index = self._list_view.wx_obj.FindPyData(-1, key)
        if index >= 0:
            self._list_view.wx_obj.DeleteItem(index)

    def __call__(self, index=None):
        if index is not None:
            if index < 0:
                index = max(len(self) + index, 0)
            key = self._list_view.wx_obj.GetPyData(index)
            return self[key]
        else:
            return self.items()  # shortcut!

    def __iter__(self):
        return self.itervalues()

    def _new_key(self):
        "Create a unique key for this list control (currently: just a counter)"
        self._key += 1
        return self._key

    def _insert(self, key, index=-1):
        if index <0:
            index = self._list_view.wx_obj.GetItemCount()   # append it
        for col in sorted(self._list_view.columns, key=lambda col: col.index):
            if not col.name in self[key]:
                continue
            text = self[key][col.name]
            if not isinstance(text, basestring):
                text = col.represent(text)
            if col.index == 0:
                self._list_view.wx_obj.InsertStringItem(index, text)
            else:
                self._list_view.wx_obj.SetStringItem(index, col.index, text)
        # update internal data, used by ColumnSorterMixin
        self._list_view.wx_obj.SetPyData(index, key)
    
    def _update(self, key, name=None):
        index = self._list_view.wx_obj.FindPyData(-1, key)
        for col in sorted(self._list_view.columns, key=lambda col: col.index):
            if not col.name in self[key]:
                continue
            text = self[key][col.name]
            if not isinstance(text, basestring):
                text = col.represent(text)
            self._list_view.wx_obj.SetStringItem(index, col.index, text)

    def clear(self):
        "Remove all items and reset internal structures"
        dict.clear(self)
        self._key = 0
        if hasattr(self._list_view, "wx_obj"):
            self._list_view.wx_obj.DeleteAllItems()


class ListItem(dict):
    "keys are column names, values are subitem values"

    def __init__(self, list_model, key, **kwargs):
        self._list_model = list_model
        self.key = key
        dict.__init__(self, **kwargs)

    def __setitem__(self, key, value):
        # if key is a column index, get the actual column name to look up:
        if not isinstance(key, basestring):
            key = self._list_model._list_view.columns[key].name
        # store the value and notify our parent to refresh the item
        dict.__setitem__(self, key, value)
        self._list_model._update(self.key, key)

    def __getitem__(self, key):
        # if key is a column index, get the actual column name to look up:
        if not isinstance(key, basestring):
            key = self._list_model._list_view.columns[key].name
        # return the data for the given column, None if nothing there
        return dict.get(self, key)

    @property
    def index(self):
        "Get the actual position (can vary due insertion/deletions and sorting)"
        return self._list_model._list_view.wx_obj.FindPyData(-1, self.key)

    def _is_selected(self):
        return self._list_model._list_view.wx_obj.IsSelected(self.index)
    
    def _select(self, on):
        self._list_model._list_view.wx_obj.Select(self.index, on)

    selected = property(_is_selected, _select)

    def ensure_visible(self):
        self._list_model._list_view.wx_obj.EnsureVisible(self.index)
        
    def focus(self):
        self._list_model._list_view.wx_obj.Focus(self.index)


# update metadata for the add context menu at the designer:

ListView._meta.valid_children = [ListColumn, ] 


if __name__ == "__main__":
    import sys
    # basic test until unit_test
    import gui
    app = wx.App(redirect=False)    
    w = gui.Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
    lv = ListView(w, name="listview", view="report", vrule=True, hrule=True,
                  multiselect="--multiselect" in sys.argv)

    ch1 = ListColumn(lv, name="col1", text="Col 1", align="left", width=200)
    ch2 = ListColumn(lv, name="col2", text="Col 2", align="center")
    ch3 = ListColumn(lv, name="col3", text="Col 3", align="right", width=100)
    ch1.represent = ch2.represent = lambda value: str(value)
    ch3.represent = lambda value: "%0.2f" % value

    lv.items = [[1, 2, 3], ['4', '5', 6], ['7', '8', 9]]
    lv.insert_items([['a', 'b', 'c']])
    #lv.append("d")
    #lv.append("e", "datum1")
    #lv.data_selection = "datum2"
    from pprint import pprint
    # assign some event handlers:
    lv.onitemselected = lambda event: pprint("selection: %s" % str(event.target.get_selected_items()))
    w.show()
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()
    
    #  basic tests
    assert lv.get_count() == 4
    lv.items(1).selected = True
    # check that internal selection match:
    assert lv.get_selected_items() == [{'col2': '5', 'col3': 6, 'col1': '4'}]
    
    if '--virtual' in sys.argv:
        lv.virtual = True
        #lv.ongetitemdata = lambda item, col: "row %d, col %d" % (item, col)
        lv.item_count = 10000000
    
    lv.delete(0)

    # basic test of item model
    lv.items(-1)['col3'] = "column 3!"
    assert lv.items(-1)[2] == "column 3!"
    assert lv.items(2)[2] == "column 3!"
    
    lv.items[2].selected = True
    lv.items[3].ensure_visible()
    lv.items[3].focus()
    
    ch1.text = "Hello!"
    ch2.align = "center"

    lv.insert_items([['a', 'b', 'c']], 0)       # add as first item
    lv.insert_items([['x', 'y', 'z']], -1)      # add as last item
    assert lv.items(0)[0] == "a"
    assert lv.items(len(lv.items)-1)[0] == "x"
    
    # test PyData keys:
    lv.items['key'] = [99, 98, 97]
    assert lv.items['key'] == {'col2': 98, 'col3': 97, 'col1': 99}
    
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    app.MainLoop()

