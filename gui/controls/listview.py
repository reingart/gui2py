
import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .listbox import ItemContainerControl
from .. import images 
from types import TupleType, ListType, StringTypes, NoneType, IntType

from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin


class wx_ListCtrl(wx.ListCtrl, ColumnSorterMixin, ListCtrlAutoWidthMixin):

    # Used by the wxColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self


class ListView(Control):
    "A multi-column list (wx.ListCtrl)"

    _wx_class = wx_ListCtrl
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.list_ctrl

    def __init__(self, parent=None, **kwargs):
        # default sane values (if not init'ed previously):
        if not hasattr(self, "item_data_map"):
            self._maxColumns = 99
            self._autoresize = 1
            self._column_headings = []
            self.item_data_map = {}

        Control.__init__(self, parent, **kwargs)

        # Now that the list exists we can init the other base class,
        # see wxPython/lib/mixins/listctrl.py
        ColumnSorterMixin.__init__(self.wx_obj, self._maxColumns)

        # Perform init for AutoWidth (resizes the last column to take up
        # the remaining display width)
        ListCtrlAutoWidthMixin.__init__(self.wx_obj)


    # Emulate some listBox methods
    def clear(self):
        self.wx_obj.DeleteAllItems()
        self.item_data_map = {}

    # Emulate some listBox methods
    def get_count(self):
        return self.wx_obj.GetItemCount()

    def _get_column_headings(self):
        return self._column_headings

    def get_column_heading_info(self):
        numcols = self.wx_obj.GetColumnCount()
        result = [None] * numcols
        if self._autoresize:
            for i in xrange(numcols):
                listItem = self.wx_obj.GetColumn(i)
                result[i] = [listItem.GetText(), wx.LIST_AUTOSIZE, listItem.GetAlign()]
        else:
            for i in xrange(numcols):
                listItem = self.wx_obj.GetColumn(i)
                result[i] = [listItem.GetText(), listItem.GetWidth(), listItem.GetAlign()]
        return result

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
            self.wx_obj.SetItemData(offset, offset)
            datamap[offset] = a_list[i]
        if self._autoresize:
            charwidth = self.wx_obj.GetCharWidth()
            maxwidth = self.wx_obj.GetBestVirtualSize()[0]*2
            for i in range(numcols):
                hdrwidth = (len(self._column_headings[i])+1) * charwidth
                colwidth = (max[i]+2) * charwidth
                curcolwidth = self.wx_obj.GetColumnWidth(i)
                if colwidth < curcolwidth:
                    colwidth = curcolwidth
                if colwidth < hdrwidth:
                    colwidth = hdrwidth
                if colwidth < 20:
                    colwidth = 20
                elif colwidth > maxwidth:
                    colwidth = maxwidth
                self.wx_obj.SetColumnWidth(i, colwidth)
            self.wx_obj.resizeLastColumn(self.wx_obj.GetColumnWidth(numcols-1))

    def _set_column_headings(self, a_list):
        print "setting column headings", a_list
        if isinstance(a_list, ListType) or isinstance(a_list, TupleType) or isinstance(a_list, StringTypes):
            pass
        else:
            raise 'invalid MultiColumnList.SetHeading value: ', a_list

        self.wx_obj.ClearAll()
        self.item_data_map = {}
        self._autoresize = 1

        if isinstance(a_list, StringTypes):
            self.wx_obj.InsertColumn(0, a_list, width=self.wx_obj.GetBestVirtualSize()[0])
            self._column_headings = [a_list]
            return
        elif isinstance(a_list, TupleType):
            a_list = list(a_list)

        self._column_headings = a_list

        numcols = len(a_list)
        if numcols == 0:
            return
        elif numcols > self._maxColumns:
            numcols = self._maxColumns
            self._column_headings = a_list[:numcols]

        if isinstance(a_list[0], StringTypes):
            for i in xrange(numcols):
                self.wx_obj.InsertColumn(i, a_list[i], width=wx.LIST_AUTOSIZE)
        elif isinstance(a_list[0], ListType) or isinstance(a_list[0], TupleType):
            w = len(a_list[0])
            if w == 2 and isinstance(a_list[0][0], StringTypes) and isinstance(a_list[0][1], IntType):
                flag = 0
                for i in xrange(numcols):
                    if a_list[i][1] != wx.LIST_AUTOSIZE:
                        flag = 1
                    self.wx_obj.InsertColumn(i, a_list[i][0], width=a_list[i][1])
                if flag:
                    self._autoresize = 0
            elif w == 3 and \
                   isinstance(a_list[0][0], StringTypes) and \
                   isinstance(a_list[0][1], IntType) and \
                   isinstance(a_list[0][2], IntType):
                flag = 0
                for i in xrange(numcols):
                    if a_list[i][1] != wx.LIST_AUTOSIZE:
                        flag = 1
                    self.wx_obj.InsertColumn(i, a_list[i][0], format=a_list[i][2], width=a_list[i][1])
                if flag:
                    self._autoresize = 0
            elif w == 1 and isinstance(a_list[0][0], StringTypes):
                for i in xrange(numcols):
                    self.wx_obj.InsertColumn(i, a_list[i][0], width=wx.LIST_AUTOSIZE)
                self._autoresize = 1
            else:
                raise 'invalid MultiColumnList.SetHeading value: ', a_list
        else:
            raise 'invalid MultiColumnList.SetHeading value: ', a_list

        if numcols == 1:
            self.wx_obj.SetColumnWidth(0, self.wx_obj.GetBestVirtualSize()[0])
 
    def get_item_data_map(self, a_dict):
        return self.item_data_map

    def set_item_data_map(self, a_dict):
        self.item_data_map = a_dict

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

    def _get_max_columns(self):
        return self._maxColumns

    def _set_max_columns(self, aString):
        # Could perhaps call the mixin __init__ method again, doesn't look
        # like it would cause harm.  For now however leave this a restriction.
        raise AttributeError, "maxColumns attribute is read-only"

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
        print "setting items", a_list
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
        if numcols > self._maxColumns:
            numcols = self._maxColumns
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
                        self._column_headings.append(colname)
        self.wx_obj.DeleteAllItems()
        datamap = {}
        max = [0] * numcols
        blanks = [''] * numcols
        columnlist = range(1, numcols)
        for i in xrange(numitems):
            aItem = a_list[i]
            if len(aItem) < numcols:
                # Not the same number of columns in entry.
                # truncation is automatic, padding with
                # blanks is done here.
                aItem = aItem + blanks
            l = len(aItem[0])
            if l > max[0]:
                max[0] = l
            self.wx_obj.InsertStringItem(i, aItem[0])
            for j in columnlist:
                l = len(aItem[j])
                if l > max[j]:
                    max[j] = l
                self.wx_obj.SetStringItem(i, j, aItem[j])
            self.wx_obj.SetItemData(i, i)
            datamap[i] = aItem
        if self._autoresize:
            charwidth = self.wx_obj.GetCharWidth()
            maxwidth = self.wx_obj.GetBestVirtualSize()[0]*2
            for i in range(numcols):
                hdrwidth = (len(self._column_headings[i])+1) * charwidth
                colwidth = int((max[i]+1) * charwidth)
                if colwidth < hdrwidth:
                    colwidth = hdrwidth
                if colwidth < 20:
                    colwidth = 20
                elif colwidth > maxwidth:
                    colwidth = maxwidth
                self.wx_obj.SetColumnWidth(i, colwidth)
            self.wx_obj.resizeLastColumn(self.wx_obj.GetColumnWidth(numcols-1))
        self.item_data_map = datamap


    view = StyleSpec({'report': wx.LC_REPORT,
                      'list': wx.LC_LIST,
                      'icon': wx.LC_ICON,
                      'small icon': wx.LC_SMALL_ICON}, default='report') 
    hrule = StyleSpec(wx.LC_HRULES, 
                doc="Draws light horizontal rules between rows (report mode).")
    vrule = StyleSpec(wx.LC_VRULES, 
                doc="Draws light vertical rules between rows (report mode).")
    multiselect = StyleSpec({True: 0, False: wx.LC_SINGLE_SEL}, 
                default=True)
    hide_headers = StyleSpec(wx.LC_NO_HEADER, default=False,
                        doc="No header in report mode")
    sort_order = StyleSpec({'ascending': wx.LC_SORT_ASCENDING,
                            'descending': wx.LC_SORT_DESCENDING,
                            'none': 0}, default='none',
                    doc="Sort order (must still supply a comparison callback")
    sort_key = Spec(_name="_sort_key", doc="comparison callback")
    virtual = StyleSpec(wx.LC_VIRTUAL, default=False,
            doc="The application provides items text on demand (report mode)")
    
    headers = InternalSpec(_get_column_headings, _set_column_headings)
    items = InternalSpec(_get_items, _set_items)

    item_selection = Spec(get_selected_items, set_selection)
    string_selection = Spec(get_string_selection, set_string_selection)

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


if __name__ == "__main__":
    import sys
    # basic test until unit_test
    import gui
    app = wx.App(redirect=False)
    w = gui.Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
    lv = ListView(w, name="listview", view="report", vrule=True, hrule=True,
                  headers=['col1', 'col2', 'col3'],
                  items=[['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']],
                  multiselect="--multiselect" in sys.argv)
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
    
    print lv.get_column_heading_info()
    assert lv.get_count() == 4
    lv.set_selection(1)
    assert lv.get_selected_items() == [[u'4', u'5', u'6']]
    
    lv.append(["Hello!"])
    lv.set_string_selection("Hello!")
    assert lv.get_string_selection()[0][0] == "Hello!"
    
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    print "VIEW MODE", lv.view
    app.MainLoop()

