import wx
from ..event import FormEvent
from ..component import Control, SubComponent
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .listbox import ItemContainerControl
from .. import images 
from types import TupleType, ListType, StringTypes, NoneType, IntType

from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin


class wx_ListCtrl(wx.ListCtrl, ColumnSorterMixin, ListCtrlAutoWidthMixin):

    def __init__(self, *args,  **kwargs):
        #if 'max_columns' in kwargs:
        max_columns = kwargs.pop('max_columns')
        item_data_map = kwargs.pop('item_data_map')
        wx.ListCtrl.__init__(self, *args, **kwargs)
        # Now that the list exists we can init the other base class,
        # see wxPython/lib/mixins/listctrl.py
        self.itemDataMap = item_data_map
        ColumnSorterMixin.__init__(self, max_columns)

        # Perform init for AutoWidth (resizes the last column to take up
        # the remaining display width)
        ListCtrlAutoWidthMixin.__init__(self)

    # Used by the wxColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    def OnGetItemText(self, item, col):
        if self.obj and self.obj._ongetitemdata:
            return self.obj._ongetitemdata(item, col)


class ListView(Control):
    "A multi-column list (wx.ListCtrl)"

    _wx_class = wx_ListCtrl
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.list_ctrl

    def __init__(self, parent=None, **kwargs):
        # default sane values (if not init'ed previously):
        if not hasattr(self, "item_data_map"):
            self._max_columns = 99
            self._autoresize = 1
            self.item_data_map = ListModel(self)
            self._key = 0             # used to generate unique keys (ItemData)

        Control.__init__(self, parent, **kwargs)

    # Emulate some listBox methods
    def clear(self):
        self.wx_obj.DeleteAllItems()
        self.item_data_map = ListModel(self)

    # Emulate some listBox methods
    def get_count(self):
        "Get the item (row) count"
        return self.wx_obj.GetItemCount()
    
    def set_count(self, value):
        "Set item (row) count -useful only in virtual mode-"
        if self.view == "report" and self.virtual and value is not None:
            self.wx_obj.SetItemCount(value)

    def get_selected_items(self):
        numcols = self.wx_obj.GetColumnCount()
        numitems = self.wx_obj.GetSelectedItemCount()
        items = [None] * numitems
        GetNextItem = self.wx_obj.GetNextItem
        if numcols == 1:
            GetItemText = self.wx_obj.GetItemText
            itemidx = -1
            for i in xrange(numitems):
                itemidx = GetNextItem(itemidx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                if itemidx == -1:
                    #Odd, selection changed?
                    break
                items[i] = GetItemText(itemidx)
        else:
            GetItem = self.wx_obj.GetItem
            cols = range(numcols)
            itemidx = -1
            for i in xrange(numitems):
                itemidx = GetNextItem(itemidx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                if itemidx == -1:
                    #Odd, selection changed?
                    break
                items[i] = map(lambda x: GetItem(itemidx, x).GetText(), cols)
        return items

    # Emulate some listBox methods
    def get_string_selection(self):
        return self.get_selected_items()

    # Emulate some listBox methods
    def append(self, a_list):
        self.insert_items(a_list, self.wx_obj.GetItemCount())

    # Emulate some listBox methods
    def insert_items(self, a_list, position=-1):
        if not isinstance(a_list, (ListType, TupleType)):
            raise AttributeError, "unsupported type, list expected"
            
        if len(a_list) == 0:
            return

        numcols = self.wx_obj.GetColumnCount()
        numitems = self.wx_obj.GetItemCount()

        # Allow negative indexing to mean from the end of the list
        if position < 0:
            position = numitems + position
        # But only allow from the start of the list on
        if position < 0:
            position = numitems

        datamap = self.item_data_map
        for a_item in a_list:
            key = self._new_key()           
            datamap[key] = a_item
            #position += 1


    def delete(self, a_position):
        "Deletes the item at the zero-based index 'n' from the control."
        key = self.wx_obj.GetItemData(a_position)
        #self.wx_obj.DeleteItem(a_position)
        del self.item_data_map[key]
 
    def get_item_data_map(self):
        return self._item_data_map

    def set_item_data_map(self, a_dict):
        self._item_data_map = a_dict
        # update the reference int the wx obj (if already created)
        if hasattr(self, "wx_obj"): 
            self.wx_obj.itemDataMap = a_dict

    def set_selection(self, itemidx, select=1):
        numitems = self.wx_obj.GetItemCount()
        if numitems == 0:
            return
        if itemidx < 0:
            itemidx = numitems + itemidx
        if itemidx < 0:
            itemidx = 0
        elif itemidx >= numitems:
            itemidx = numitems - 1

        if select:
            self.wx_obj.SetItemState(itemidx, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        else:
            self.wx_obj.SetItemState(itemidx, 0, wx.LIST_STATE_SELECTED)

    def set_string_selection(self, item, select=1):
        numitems = self.wx_obj.GetItemCount()
        if numitems == 0:
            return -1
        #TODO:  Expand search to all columns, for now it adds no functionality
        itemidx = self.wx_obj.FindItem(-1, item, 1)
        if itemidx < 0:
            return itemidx

        if select:
            self.wx_obj.SetItemState(itemidx, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        else:
            self.wx_obj.SetItemState(itemidx, 0, wx.LIST_STATE_SELECTED)
        return itemidx

    def _get_items( self ) :
        numitems = self.wx_obj.GetItemCount()
        numcols = self.wx_obj.GetColumnCount()
        items = [None] * numitems
        if numcols == 1:
            GetItemText = self.wx_obj.GetItemText
            for i in xrange(numitems ) :
                items[i] = GetItemText(i)
        else:
            GetItem = self.wx_obj.GetItem
            cols = range(numcols)
            for i in xrange(numitems) :
                items[i] = map(lambda x: GetItem(i, x).GetText(), cols)
        return items

    def _set_items(self, a_list):
        if isinstance(a_list, NoneType):
            a_list = []
        elif not isinstance(a_list, ListType) and not isinstance(a_list, TupleType):
            raise AttributeError, "unsupported type, list expected"

        numitems = len(a_list)
        if numitems == 0:
            self.wx_obj.DeleteAllItems()
            self.item_data_map = ListModel(self)
            return

        # If just simple list of strings convert it to a single column list
        if isinstance(a_list[0], StringTypes):
            a_list = map(lambda x:[x], a_list)
        elif isinstance(a_list[0], ListType) or isinstance(a_list[0], TupleType):
            pass
        else:
            raise AttributeError, "unsupported element type"
        self.wx_obj.DeleteAllItems()
        self.item_data_map = ListModel(self)
        self.insert_items(a_list)
    
    def _new_key(self):
        "Create a unique key for this list control (currently: just a counter)"
        self._key += 1
        return self._key

    def _get_sort_column(self):
        return self.wx_obj.GetSortState()[0]

    def _set_sort_column(self, col=None):
        order = +1 if self.sort_order=='ascending' else -1
        if col is not None:
            self.wx_obj.SortListItems(col, order)

    def _get_column_headings(self):
        "Return a list of children sub-components that are column headings"
        # return it in the same order as inserted in the ListCtrl
        headers = [ctrl for ctrl in self if isinstance(ctrl, ColumnHeader)]
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
    item_data_map = InitSpec(get_item_data_map, set_item_data_map,
                           doc="internal data (for Sort mixin)")
    
    headers = InternalSpec(_get_column_headings,
                           doc="Return a list of current column headers")
    items = InternalSpec(_get_items, _set_items)

    item_selection = Spec(get_selected_items, set_selection)
    string_selection = Spec(get_string_selection, set_string_selection)
    
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


class ColumnHeader(SubComponent):
    "ListView sub-component to handle heading, align and width of columns"

    _created = False
    
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
        self._ordered_list = []

    def __setitem__(self, key, kwargs):
        # convert item to dict if given as list / str
        if isinstance(kwargs, basestring):
            kwargs = [kwargs]
        if isinstance(kwargs, list):
            kwargs = dict([(col.name, kwargs[col.index]) for col
                          in self._list_view.headers if col.index<len(kwargs)])
        # create the new item
        item = ListItem(self, key, **kwargs)
        dict.__setitem__(self, key, item)
        # check if we should insert the item:
        if key not in self._ordered_list:
            self._ordered_list.append(key)
            self.insert(key)
        else:
            self.update(key)
        #return item

    def __getitem__(self, key):
        # if key is a column index, get the actual item key to look up:
        if key < 0:     # TODO: support key > 0
            key = self._ordered_list[key]
        return dict.__getitem__(self, key)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        position = self._ordered_list.index(key)
        self._list_view.wx_obj.DeleteItem(position)
        self._ordered_list.remove(key)

    def insert(self, key, position=-1):
        position = self._ordered_list.index(key)
        for col in sorted(self._list_view.headers, key=lambda col:col.index):
            if not col.name in self[key]:
                continue
            text = self[key][col.name]
            if not isinstance(text, basestring):
                text = col.represent(text)
            if col.index == 0:
                self._list_view.wx_obj.InsertStringItem(position, text)
            else:
                self._list_view.wx_obj.SetStringItem(position, col.index, text)
        # update internal data, used by ColumnSorterMixin
        self._list_view.wx_obj.SetItemData(position, key)
    
    def update(self, key, name):
        position = self._ordered_list.index(key)
        for col in sorted(self._list_view.headers, key=lambda col: col.index):
            if not col.name in self[key]:
                continue
            text = self[key][col.name]
            if not isinstance(text, basestring):
                text = col.represent(text)
            self._list_view.wx_obj.SetStringItem(position, col.index, text)


class ListItem(dict):
    "keys are column names, values are subitem values"

    def __init__(self, _list_model, _key, **kwargs):
        self._list_model = _list_model
        self._key = _key
        dict.__init__(self, **kwargs)

    def __setitem__(self, key, value):
        # if key is a column index, get the actual column name to look up:
        if not isinstance(key, basestring):
            key = self._list_model._list_view.headers[key].name
        # store the value and notify our parent to refresh the item
        dict.__setitem__(self, key, value)
        self._list_model.update(self._key, key)

    def __getitem__(self, key):
        # if key is a column index, get the actual column name to look up:
        if not isinstance(key, basestring):
            key = self._list_model._list_view.headers[key].name
        # return the data for the given column, None if nothing there
        return dict.get(self, key)


# update metadata for the add context menu at the designer:

ListView._meta.valid_children = [ColumnHeader, ] 


if __name__ == "__main__":
    import sys
    # basic test until unit_test
    import gui
    app = wx.App(redirect=False)    
    w = gui.Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
    lv = ListView(w, name="listview", view="report", vrule=True, hrule=True,
                  multiselect="--multiselect" in sys.argv)

    ch1 = ColumnHeader(lv, name="col1", text="Col 1", align="left", width=200)
    ch2 = ColumnHeader(lv, name="col2", text="Col 2", align="center")
    ch3 = ColumnHeader(lv, name="col3", text="Col 3", align="right", width=100)
    ch1.represent = ch2.represent = lambda value: str(value)
    ch3.represent = lambda value: "%0.2f" % value

    lv.items = [[1, 2, 3], ['4', '5', 6], ['7', '8', 9]]
    lv.insert_items([['a', 'b', 'c']], -1)
    #lv.append("d")
    #lv.append("e", "datum1")
    #lv.data_selection = "datum2"
    from pprint import pprint
    # assign some event handlers:
    lv.onitemselected = lambda event: pprint("selection: %s" % str(event.target.item_selection))
    w.show()
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()
    
    #  basic tests
    print lv.get_count()
    assert lv.get_count() == 4
    lv.set_selection(1)
    assert lv.get_selected_items() == [[u'4', u'5', u'6.00']]
    
    lv.append(["Hello!"])
    lv.set_string_selection("Hello!")
    assert lv.get_string_selection()[0][0] == "Hello!"

    if '--virtual' in sys.argv:
        lv.virtual = True
        #lv.ongetitemdata = lambda item, col: "row %d, col %d" % (item, col)
        lv.item_count = 10000000
    
    lv.delete(0)

    # basic test of item model (TODO: unify lv.items and lv.item_data_map)
    lv.item_data_map[-1]['col3'] = "column 3!"
    assert lv.items[-1][2] == "column 3!"
    
    ch1.text = "Hello!"
    ch2.align = "center"
   
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    app.MainLoop()

