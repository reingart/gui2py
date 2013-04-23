#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Grid Model-View-Controller control (uses wx.Grid & PyGridBaseTable)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicables

# Initial implementation was based on PythonCard's Grid component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)
# Note: pythoncard version was trivial, Model and View code are completely new

import wx
import wx.grid as gridlib

from ..event import GridEvent
from ..component import Control, Component, SubComponent
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .. import registry
from .. import images


class wx_Grid(gridlib.Grid):
    "Simple Grid control"
    # initially based on GridSimple.py / Grid_MegaExample.py wxPython demo
    
    def __init__(self, parent, *args, **kwargs):
        # The base class must be initialized *first*
        gridlib.Grid.__init__(self, parent, -1)
        ##mixins.GridAutoEditMixin.__init__(self)

        self._table = GridTable(self, plugins={})
        self.SetTable(self._table)
        #self._plugins = plugins

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        self._table.ResetView(self)


class GridView(Control):
    "A Grid (gridlib.Grid) used for displaying and editing tabular data"

    _wx_class = wx_Grid
    _image = images.grid

    def _get_items(self):
        return self._items

    def _set_items(self, a_list):
        if a_list is None:
            a_list = []
        elif not isinstance(a_list, (list, tuple, dict)):
            raise AttributeError("unsupported type, list/tuple/dict expected")

        self._items = GridModel(self, a_list)
        self.wx_obj.Refresh()
        #self.insert_items(a_list)
        
    def _get_column_headings(self):
        "Return a list of children sub-components that are column headings"
        # return it in the same order as inserted in the Grid
        headers = [ctrl for ctrl in self if isinstance(ctrl, GridColumn)]
        return sorted(headers, key=lambda ch: ch.index)
    
    columns = InternalSpec(_get_column_headings,
                           doc="Return a list of current column headers")
    items = InternalSpec(_get_items, _set_items)
    
    # events:
    ongridmouseclick = EventSpec('grid_mouse_click', 
                       binding=gridlib.EVT_GRID_CELL_LEFT_CLICK, kind=GridEvent)
    ongridmouserclick = EventSpec('grid_mouse_rclick', 
                       binding=gridlib.EVT_GRID_CELL_RIGHT_CLICK, kind=GridEvent)
    ongridmousedclick = EventSpec('grid_mouse_dclick', 
                       binding=gridlib.EVT_GRID_CELL_LEFT_DCLICK, kind=GridEvent)
    ongridlabelclick = EventSpec('grid_label_click', 
                       binding=gridlib.EVT_GRID_LABEL_LEFT_CLICK, kind=GridEvent)
    ongridlabelrclick = EventSpec('grid_label_rclick', 
                       binding=gridlib.EVT_GRID_LABEL_RIGHT_CLICK, kind=GridEvent)
    ongridlabeldclick = EventSpec('grid_label_dclick', 
                       binding=gridlib.EVT_GRID_LABEL_LEFT_DCLICK, kind=GridEvent)
    ongridrowsize = EventSpec('grid_row_size', 
                       binding=gridlib.EVT_GRID_ROW_SIZE, kind=GridEvent)
    ongridcolsize = EventSpec('grid_col_size', 
                       binding=gridlib.EVT_GRID_COL_SIZE, kind=GridEvent)
    ongridrangeselect = EventSpec('grid_range_select', 
                       binding=gridlib.EVT_GRID_RANGE_SELECT, kind=GridEvent)
    ongridcellchange = EventSpec('grid_cell_change', 
                       binding=gridlib.EVT_GRID_CELL_CHANGE, kind=GridEvent)
    ongridselectcell = EventSpec('grid_select_cell', 
                       binding=gridlib.EVT_GRID_SELECT_CELL, kind=GridEvent)
    ongrideditornshown = EventSpec('grid_editor_shown', 
                       binding=gridlib.EVT_GRID_EDITOR_SHOWN, kind=GridEvent)
    ongrideditorhidden = EventSpec('grid_editor_hidden', 
                       binding=gridlib.EVT_GRID_EDITOR_HIDDEN, kind=GridEvent)
    ongrideditorcreated = EventSpec('grid_editor_created', 
                       binding=gridlib.EVT_GRID_EDITOR_CREATED, kind=GridEvent)


class GridTable(gridlib.PyGridTableBase):
    "A custom wx.Grid Table using user supplied data"
    
    def __init__(self, wx_grid, plugins):
        "data is a list of the form {row_index: {col_name: value}"
        # The base class must be initialized *first*
        gridlib.PyGridTableBase.__init__(self)
        self.wx_grid = wx_grid
        self.plugins = plugins or {}
        # we need to store the row length and column length to
        # see if the table has changed size
        self._rows = 0
        self._cols = 0

    # shortcuts to gui2py:
    columns = property(lambda self: self.wx_grid.obj.columns)
    data = property(lambda self: self.wx_grid.obj.items)

    def GetNumberCols(self):
        if not hasattr(self.wx_grid, "obj"):
            return 0  # not initialized yet!
        else:
            return len(self.columns)

    def GetNumberRows(self):
        if not hasattr(self.wx_grid, "obj"):
            return 0  # not initialized yet! 
        else:
            return len(self.data)

    def GetColLabelValue(self, col):
        return self.columns[col].text

    def GetRowLabelValue(self, row):
        return "row %03d" % row

    def GetValue(self, row, col):
        return self.data[row].get(self.columns[col].name, "")

    def GetRawValue(self, row, col):
        return self.data[row].get(self.columns[col].name, "")

    def SetValue(self, row, col, value):
        # if using types, do not convert to str (already done if needed)
        self.data[row][self.columns[col].name] = value

    def SetRawValue(self, row, col, value):
        self.data[row][self.columns[col].name] = value      # TODO: = SetValue?

    def IsEmptyCell(self, row, col):
        return self.columns[col].name not in self.data[row]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.columns[col]._type
    
    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, type_name):
        col_type = self.columns[col]._type.split(':')[0]
        if col_type == type_name:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, type_name):
        return self.CanGetValueAs(row, col, type_name)
        
    def InsertCols(self, *args, **kwargs):
        wx.CallAfter(self.ResetView, self.wx_grid)

    def AppendCols(self, *args, **kwargs):
        wx.CallAfter(self.ResetView, self.wx_grid)

    def DeleteCols(self, *args, **kwargs):
        wx.CallAfter(self.ResetView, self.wx_grid)

    def InsertRows(self, *args, **kwargs):
        wx.CallAfter(self.ResetView, self.wx_grid)

    def AppendRows(self, *args, **kwargs):
        wx.CallAfter(self.ResetView, self.wx_grid)

    def DeleteRows(self, *args, **kwargs):
        wx.CallAfter(self.ResetView, self.wx_grid)

    def ResetView(self, grid):
        "Update the grid if rows and columns have been added or deleted"
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), 
             gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, 
             gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), 
             gridlib.GRIDTABLE_NOTIFY_COLS_DELETED,
             gridlib.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:

            if new < current:
                msg = gridlib.GridTableMessage(self,delmsg,new,current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = gridlib.GridTableMessage(self,addmsg,new-current)
                grid.ProcessTableMessage(msg)
                self.UpdateValues(grid)

        grid.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()
        # update the column rendering plugins
        self._updateColAttrs(grid)

        # update the scrollbars and the displayed part of the grid
        grid.AdjustScrollbars()
        grid.ForceRefresh()


    def UpdateValues(self, grid):
        "Update all displayed values"
        # This sends an event to the grid table to update all of the values
        msg = gridlib.GridTableMessage(self, 
                                    gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)

    def _updateColAttrs(self, grid):
        "update the column attributes to add the appropriate renderer"
        col = 0

        for column in self.columns:
            attr = gridlib.GridCellAttr()
            if False:  # column.readonly
                attr.SetReadOnly()
            if False:  # column.renderer
                attr.SetRenderer(renderer)
            grid.SetColSize(col, column.width)
            grid.SetColAttr(col, attr)
            col += 1
        #grid.SetDefaultRowSize(renderer.rowSize)

    def SortColumn(self, col):
        "col -> sort the data based on the column indexed by col"
        name = self.columns[col].name
        _data = []

        for row in self.data:
            rowname, entry = row
            _data.append((entry.get(name, None), row))

        _data.sort()
        self.data = []

        for sortvalue, row in _data:
            self.data.append(row)

    # end table manipulation code
    # ----------------------------------------------------------


class GridColumn(SubComponent):
    "Grid sub-component to handle heading, align, width and props of columns"

    _created = False
    _registry = registry.MISC
    
    def set_parent(self, new_parent, init=False):
        "Associate the header to the control (it could be recreated)"
        self._created = False
        SubComponent.set_parent(self, new_parent, init)
        # if index not given, append the column at the last position:
        if self.index == -1 or self.index >= len(self._parent.columns):
            self.index = len(self._parent.columns) - 1
        # insert the column in the listview:
        self._parent.wx_obj.AppendCols(1)
        #self._parent.wx_obj.SetColLabelValue(self.index, self.text)
        #self.SetColLabel(self.index, self.align)
        #self._parent.wx_obj.SetColSize(self.index, self.width)
        self._created = True    # enable setattr hook

    def destroy(self):
        self._parent.wx_obj.DeleteCols(self.index, 1)
        # reindex (maybe this should be moved to GridView)
        for column in self._parent.columns[self.index+1:]:
            column.index = column.index - 1
        del self._parent[self.name]
        #SubComponent.destroy(self)

    def __setattr__(self, name, value):
        "Hook to update the column information in wx"
        object.__setattr__(self, name, value)
        if name not in ("_parent", "_created") and self._created:
            self._parent.wx_obj.Refresh()

    name = InitSpec(optional=False, default="", _name="_name", type='string')
    text = InitSpec(optional=False, default="", _name="_text", type='string')
    index = InitSpec(optional=False, default=-1, _name="_index", type='integer')
    align = InitSpec(mapping={'left': wx.ALIGN_LEFT,
                              'center': wx.ALIGN_CENTRE,
                              'right': wx.ALIGN_RIGHT}, 
                     default='left', _name="_align", type="enum",
                     doc="Grid Column Horizontal Alignment")
    width = InitSpec(default=wx.LIST_AUTOSIZE, _name="_width", type="integer",
                     doc="Column width (default=autosize)")
    represent = InitSpec(default=lambda v: v, _name="_represent", type='string',
                     doc="function to returns a representation for the subitem")
    type = InitSpec(mapping={'string': gridlib.GRID_VALUE_STRING,
                             'text': gridlib.GRID_VALUE_TEXT,
                             'number': gridlib.GRID_VALUE_NUMBER,
                             'float': gridlib.GRID_VALUE_FLOAT,  # double?
                             'long': gridlib.GRID_VALUE_LONG,
                             'bool': gridlib.GRID_VALUE_BOOL,
                             'choice': gridlib.GRID_VALUE_CHOICE,
                             'choiceint': gridlib.GRID_VALUE_CHOICEINT,
                             'datetime': gridlib.GRID_VALUE_DATETIME,
                             }, 
                     default='string', _name="_type", type="edit_enum",
                     doc="Type of value of a cell, use ':' for additional "
                         "parameters: 'choice:all,MSW,GTK,MAC' or 'double:6,2'"
                     )


class GridModel(list):
    "GridView rows model (each element should be a dict-like {col_name: value})"
    
    def __init__(self, _grid_view, data):
        list.__init__(self)
        self._grid_view = _grid_view
        self.clear()
        for it in data:
            self.append(it)

    def insert(self, pos, values):
        "Insert a number of rows into the grid (and associated table)"
        row = GridRow(self, *values)
        list.insert(self, pos, row)
        self._grid_view.wx_obj.InsertRows(pos, numRows=1)

    def append(self, values):
        "Insert a number of rows into the grid (and associated table)"
        row = GridRow(self, *values)
        list.append(self, row)
        self._grid_view.wx_obj.AppendRows(numRows=1)
        
    def __setitem__(self, pos, value):
        row = GridRow(self, *value)
        list.__setitem__(self, pos, row)
        # update the grid (just the row affected):
        self._refresh(pos)

    def _refresh(self, pos, col=None):
        # TODO: see if there is a specialized message to send to the table
        # NOTE: if couses flicker, both calls should be enclosed in a grid batch
        self._grid_view.wx_obj.DeleteRows(pos, numRows=1)
        self._grid_view.wx_obj.InsertRows(pos, numRows=1)

    def __delitem__(self, pos):
        "Delete row from position pos"
        list.__delitem__(self, pos)
        self._grid_view.wx_obj.DeleteRows(pos, numRows=1)

    def clear(self):
        "Remove all rows and reset internal structures"
        ## list has no clear ... remove items in reverse order
        for i in range(len(self)-1, -1, -1):
            del self[i]
        self._key = 0
        if hasattr(self._grid_view, "wx_obj"):
            self._grid_view.wx_obj.ClearGrid()


class GridRow(dict):
    "keys are column names, values are cell values"

    def __init__(self, grid_model, *args, **kwargs):
        self._grid_model = grid_model
        # convert items to a key:value map (column names are keys)
        if args:
            columns = self._grid_model._grid_view.columns
            for i, arg in enumerate(args):
                kwargs[columns[i].name] = arg                
        dict.__init__(self, **kwargs)

    def __setitem__(self, key, value):
        # if key is a column index, get the actual column name to look up:
        if not isinstance(key, basestring):
            col = key
            column = self._grid_model._grid_view.columns[key]
            key = column.name
        else:
            for i, column in enumerate(self._grid_model._grid_view.columns):
                if column.name == key:
                    col = i
                    break
            else:
                col = None  # raise an exception?
        if col is not None and self[key] != value:
            # store the value and notify the view to refresh the item
            dict.__setitem__(self, key, value)
            pos = self.index
            # refresh the value (usefull if value setted programatically)
            self._grid_model._refresh(pos, col)

    def __getitem__(self, key):
        # if key is a column index, get the actual column name to look up:
        if not isinstance(key, basestring):
            key = self._grid_model._grid_view.columns[key].name
        # return the data for the given column, None if nothing there
        return dict.get(self, key)

    @property
    def index(self):
        "Get the actual position (can vary due insertion/deletions and sorting)"
        return self._grid_model.index(self)

    def _is_selected(self):
        return self._grid_model._grid_view.wx_obj.IsInSelection(self.index, 0)
    
    def _select(self, on):
        if on:
            self._grid_model._grid_view.wx_obj.SelectRow(self.index, True)
        else:
            # this clear all the selection, TODO: clear just this row
            self._grid_model._grid_view.wx_obj.ClearSelection()

    selected = property(_is_selected, _select)

    def ensure_visible(self):
        self._grid_model._grid_view.wx_obj.EnsureVisible(self.index)
        
    def focus(self):
        self._grid_model._grid_view.wx_obj.Focus(self.index)


# update metadata for the add context menu at the designer:

GridView._meta.valid_children = [GridColumn, ] 


if __name__ == "__main__":
    import sys
    # basic test until unit_test
    import gui
    app = wx.App(redirect=False)    
    w = gui.Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
    gv = GridView(w, name="grid1", 
                  #multiselect="--multiselect" in sys.argv,
                  )

    ch1 = GridColumn(gv, name="col1", text="Col 1", align="left", width=100)
    ch2 = GridColumn(gv, name="col2", text="Col 2", align="center")
    ch3 = GridColumn(gv, name="col3", text="Col 3", align="right", width=100, type="number")
    ch4 = GridColumn(gv, name="col4", text="Col 4", align="right", width=100, type="float")
    #ch1.represent = ch2.represent = lambda value: str(value)
    #ch3.represent = lambda value: "%0.2f" % value

    gv.items = [[1, 2, 3, 3.141516], ['4', 5, 6.], ['7', 8, 9]]
    
    #lv.insert_items([['a', 'b', 'c']])
    #lv.append("d")
    #lv.append("e", "datum1")
    #lv.data_selection = "datum2"
    # assign some event handlers:
    #lv.onitemselected = ""
    w.show()
    
    def update(p):
        if p == 1:
            gv.items[0][0] = "hola!"            # change a cell programatically
            gv.items.insert(0, [10, 11, 12.])   # insert a row at first pos
            gv.items[2] = [99, 98, 97, 96.543]  # replace a complete row
            del gv.items[-1]                    # delete the last row
        if p == 2:
            gv.items[0][3] = 1/2.0
        print "updated!"
    wx.CallLater(2000, update, 1)
    wx.CallLater(3000, update, 2)
        
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()
    
    #  basic tests
    ##assert lv.get_count() == 4
    ##lv.items(1).selected = True
    # check that internal selection match:
    ##assert lv.get_selected_items() == [{'col2': '5', 'col3': 6, 'col1': '4'}]
    
    ##if '--virtual' in sys.argv:
    ##    lv.virtual = True
    ##    #lv.ongetitemdata = lambda item, col: "row %d, col %d" % (item, col)
    ##    lv.item_count = 10000000
    
    ##lv.delete(0)

    # basic test of item model
    ##lv.items(-1)['col3'] = "column 3!"
    ##assert lv.items(-1)[2] == "column 3!"
    ##assert lv.items(2)[2] == "column 3!"
    
    ##lv.items[2].selected = True
    ##lv.items[3].ensure_visible()
    ##lv.items[3].focus()
    
    ##ch1.text = "Hello!"
    ##ch2.align = "center"

    ##lv.insert_items([['a', 'b', 'c']], 0)       # add as first item
    ##lv.insert_items([['x', 'y', 'z']], -1)      # add as last item
    ##assert lv.items(0)[0] == "a"
    ##assert lv.items(len(lv.items)-1)[0] == "x"
    
    # test PyData keys:
    ##lv.items['key'] = [99, 98, 97]
    ##assert lv.items['key'] == {'col2': 98, 'col3': 97, 'col1': 99}
    
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    app.MainLoop()
