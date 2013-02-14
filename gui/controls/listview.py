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
            self.item_data_map = {}
            self._key = 0             # used to generate unique keys (ItemData)

        Control.__init__(self, parent, **kwargs)

    # Emulate some listBox methods
    def clear(self):
        self.wx_obj.DeleteAllItems()
        self.item_data_map = {}

    # Emulate some listBox methods
    def get_count(self):
        return self.wx_obj.GetItemCount()

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
    def insert_items(self, a_list, position):
        if not isinstance(a_list, ListType) and not isinstance(a_list, TupleType):
            raise AttributeError, "unsupported type, list expected"
            
        if len(a_list) == 0:
            return

        numcols = self.wx_obj.GetColumnCount()
        numitems = self.wx_obj.GetItemCount()

        # If the list is empty or uninitialized fake an assignment and return
        if numitems == 0 or numcols == 0:
            self._set_items(a_list)
            return 

        # Convert our input into a list of list entries of the appropriate
        # number of columns.
        if isinstance(a_list[0], ListType) or isinstance(a_list[0], TupleType):
            if isinstance(a_list[0], TupleType):
                a_list = list(a_list)
            if numcols == len(a_list[0]):
                pass
            elif numcols > len(a_list[0]):
                blanks = [''] * (numcols - len(a_list[0]))
                a_list = map(lambda x:x + blanks, a_list)
            else:
                a_list = map(lambda x:x[:numcols], a_list)
        elif isinstance(a_list[0], StringTypes):
            blanks = [''] * (numcols - 1)
            a_list = map(lambda x:[x] + blanks, a_list)
        else:
            raise AttributeError, "unsupported type, list or string expected"

        # Allow negative indexing to mean from the end of the list
        if position < 0:
            position = numitems + position
        # But only allow from the start of the list on
        if position < 0:
            postiion = 0

        # If inserting within the current span of the list, we have
        # to copy the portion below the insertion point
        if position < numitems:
            currentitems = self._get_items()[position:]
            if isinstance(currentitems[0], StringTypes):
                currentitems = map(lambda x:[x], currentitems)
            a_list = a_list + currentitems

        datamap = self.item_data_map
        max = [0] * numcols
        for i in xrange(len(a_list)):
            offset = position + i
            key = self._new_key()
            l = len(a_list[i][0])
            if l > max[0]:
                max[0] = l
            if offset >= numitems:
                self.wx_obj.InsertStringItem(offset, a_list[i][0])
            else:
                self.wx_obj.SetStringItem(offset, 0, a_list[i][0])
            for j in range(1,numcols):
                l = len(a_list[i][j])
                if l > max[j]:
                    max[j] = l
                self.wx_obj.SetStringItem(offset, j, a_list[i][j])
            self.wx_obj.SetItemData(offset, key)
            datamap[key] = a_list[i]

    def delete(self, a_position):
        "Deletes the item at the zero-based index 'n' from the control."
        key = self.wx_obj.GetItemData(a_position)
        self.wx_obj.DeleteItem(a_position)
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

    def _set_items( self, a_list ) :
        if isinstance(a_list, NoneType):
            a_list = []
        elif not isinstance(a_list, ListType) and not isinstance(a_list, TupleType):
            raise AttributeError, "unsupported type, list expected"

        numitems = len(a_list)
        if numitems == 0:
            self.wx_obj.DeleteAllItems()
            self.item_data_map = {}
            return

        # If just simple list of strings convert it to a single column list
        if isinstance(a_list[0], StringTypes):
            a_list = map(lambda x:[x], a_list)
        elif isinstance(a_list[0], ListType) or isinstance(a_list[0], TupleType):
            pass
        else:
            raise AttributeError, "unsupported element type"
        # Here we have a list of a list of values.
        # If the number of values is greater than the maximum number
        # of columns allowed, truncate it.  Similarly remove or add
        # columns as necessary to accomodate the data up to the maximum
        # allowed.  It could be thought to just throw an exception
        # since the programmer flubbed it however I chose the
        # 'do what you can' approach. Note that we depend on the
        # first item in the list setting the number of columns for
        # all remaining items in the list.
        numcols = len(a_list[0])
        if numcols > self._max_columns:
            numcols = self._max_columns
        if numcols != self.wx_obj.GetColumnCount():
            if numcols == 1:
                self.wx_obj.ClearAll()
                self.wx_obj.InsertColumn(0,'List')
                self._column_headings = ['List']
            else:
                c = self.wx_obj.GetColumnCount()
                if c > numcols:
                    for i in range(c-1,numcols-1,-1):
                        self.wx_obj.DeleteColumn(i)
                        self._column_headings = self._column_headings[:-1]
                else:
                    for i in range(c,numcols):
                        colname = 'Col %d' % (i+1,)
                        self.wx_obj.InsertColumn(i, colname)
                        #self._column_headings.append(colname)
        self.wx_obj.DeleteAllItems()
        datamap = {}
        max = [0] * numcols
        blanks = [''] * numcols
        columnlist = range(1, numcols)
        for i in xrange(numitems):
            key = self._new_key()
            a_item = a_list[i]
            if len(a_item) < numcols:
                # Not the same number of columns in entry.
                # truncation is automatic, padding with
                # blanks is done here.
                a_item = a_item + blanks
            l = len(a_item[0])
            if l > max[0]:
                max[0] = l
            self.wx_obj.InsertStringItem(i, a_item[0])
            for j in columnlist:
                l = len(a_item[j])
                if l > max[j]:
                    max[j] = l
                self.wx_obj.SetStringItem(i, j, a_item[j])
            self.wx_obj.SetItemData(i, key)     # used by ColumnSorterMixin
            datamap[key] = a_item

        self.item_data_map = datamap
    
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
    
    items = InternalSpec(_get_items, _set_items)

    item_selection = Spec(get_selected_items, set_selection)
    string_selection = Spec(get_string_selection, set_string_selection)
    
    item_count = Spec(
        lambda self: self.wx_obj.GetItemCount(),
        lambda self, val: (val is not None and self.wx_obj.SetItemCount(val)),
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
      
    def set_parent(self, new_parent):
        "Associate the header to the control (it could be recreated)"
        SubComponent.set_parent(self, new_parent)
        # if index not given, append the column at the last position:
        if self.index == -1:
            self.index = self._parent.wx_obj.GetColumnCount()
        # insert the column in the listview:
        self._parent.wx_obj.InsertColumn(self.index, self.text, self._align, 
                                         self.width)
        self._created = True    # enable setattr hook

    def __setattr__(self, name, value):
        "Hook to update the column information in wx"
        object.__setattr__(self, name, value)
        if hasattr(self, "_created"):
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
    ch3 = ColumnHeader(lv, name="col2", text="Col 3", align="right", width=100)
    lv.items = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
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
    
    assert lv.get_count() == 4
    lv.set_selection(1)
    assert lv.get_selected_items() == [[u'4', u'5', u'6']]
    
    lv.append(["Hello!"])
    lv.set_string_selection("Hello!")
    assert lv.get_string_selection()[0][0] == "Hello!"

    if '--virtual' in sys.argv:
        lv.virtual = True
        #lv.ongetitemdata = lambda item, col: "row %d, col %d" % (item, col)
        lv.item_count = 10000000
    
    lv.delete(0)
    
    ch1.text = "Hello!"
    ch2.align = "center"
    print str(ch2)
    
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    print "VIEW MODE", lv.view
    app.MainLoop()

