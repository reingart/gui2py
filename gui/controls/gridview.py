
import wx
import wx.grid as gridlib

from ..event import GridEvent
from ..component import Control, Component
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

        self._table = GridTable(data, colnames, plugins={})
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
    
    def __init__(self, data, colnames, plugins):
        """data is a list of the form
        [(rowname, dictionary),
        dictionary.get(colname, None) returns the data for column
        colname
        """
        # The base class must be initialized *first*
        gridlib.PyGridTableBase.__init__(self)
        self.data = data
        self.colnames = colnames
        self.plugins = plugins or {}
        # XXX
        # we need to store the row length and column length to
        # see if the table has changed size
        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def GetNumberCols(self):
        return len(self.colnames)

    def GetNumberRows(self):
        return len(self.data)

    def GetColLabelValue(self, col):
        return self.colnames[col]

    def GetRowLabelValue(self, row):
        return "row %03d" % int(self.data[row][0])

    def GetValue(self, row, col):
        return str(self.data[row][1].get(self.GetColLabelValue(col), ""))

    def GetRawValue(self, row, col):
        return self.data[row][1].get(self.GetColLabelValue(col), "")

    def SetValue(self, row, col, value):
        self.data[row][1][self.GetColLabelValue(col)] = value

    def ResetView(self, grid):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        grid.BeginBatch()

        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), Grid.GRIDTABLE_NOTIFY_ROWS_DELETED, Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), Grid.GRIDTABLE_NOTIFY_COLS_DELETED, Grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:

            if new < current:
                msg = Grid.GridTableMessage(self,delmsg,new,current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = Grid.GridTableMessage(self,addmsg,new-current)
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
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = Grid.GridTableMessage(self, Grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)

    def _updateColAttrs(self, grid):
        """
        wx.Grid -> update the column attributes to add the
        appropriate renderer given the column name.  (renderers
        are stored in the self.plugins dictionary)

        Otherwise default to the default renderer.
        """
        col = 0

        for colname in self.colnames:
            attr = Grid.GridCellAttr()
            if colname in self.plugins:
                renderer = self.plugins[colname](self)

                if renderer.colSize:
                    grid.SetColSize(col, renderer.colSize)

                if renderer.rowSize:
                    grid.SetDefaultRowSize(renderer.rowSize)

                attr.SetReadOnly(True)
                attr.SetRenderer(renderer)

            grid.SetColAttr(col, attr)
            col += 1

    # ------------------------------------------------------
    # begin the added code to manipulate the table (non wx related)
    def AppendRow(self, row):
        #print 'append'
        entry = {}

        for name in self.colnames:
            entry[name] = "Appended_%i"%row

        # XXX Hack
        # entry["A"] can only be between 1..4
        entry["A"] = random.choice(range(4))
        self.data.insert(row, ["Append_%i"%row, entry])

    def DeleteCols(self, cols):
        """
        cols -> delete the columns from the dataset
        cols hold the column indices
        """
        # we'll cheat here and just remove the name from the
        # list of column names.  The data will remain but
        # it won't be shown
        deleteCount = 0
        cols = cols[:]
        cols.sort()

        for i in cols:
            self.colnames.pop(i-deleteCount)
            # we need to advance the delete count
            # to make sure we delete the right columns
            deleteCount += 1

        if not len(self.colnames):
            self.data = []

    def DeleteRows(self, rows):
        """
        rows -> delete the rows from the dataset
        rows hold the row indices
        """
        deleteCount = 0
        rows = rows[:]
        rows.sort()

        for i in rows:
            self.data.pop(i-deleteCount)
            # we need to advance the delete count
            # to make sure we delete the right rows
            deleteCount += 1

    def SortColumn(self, col):
        """
        col -> sort the data based on the column indexed by col
        """
        name = self.colnames[col]
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

import random
colnames = ["Row", "This", "Is", "A", "Test"]

data = []

for row in range(1000):
    d = {}
    for name in ["This", "Test", "Is"]:
        d[name] = random.random()

    d["Row"] = len(data)
    # XXX
    # the "A" column can only be between one and 4
    d["A"] = random.choice(range(4))
    data.append((str(row), d))



if __name__ == "__main__":
    import sys
    # basic test until unit_test
    import gui
    app = wx.App(redirect=False)    
    w = gui.Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
    lv = GridView(w, name="grid1", 
                  #multiselect="--multiselect" in sys.argv,
                  )

    #ch1 = ColumnHeader(lv, name="col1", text="Col 1", align="left", width=200)
    #ch2 = ColumnHeader(lv, name="col2", text="Col 2", align="center")
    #ch3 = ColumnHeader(lv, name="col3", text="Col 3", align="right", width=100)
    #ch1.represent = ch2.represent = lambda value: str(value)
    #ch3.represent = lambda value: "%0.2f" % value

    #lv.items = [[1, 2, 3], ['4', '5', 6], ['7', '8', 9]]
    #lv.insert_items([['a', 'b', 'c']])
    #lv.append("d")
    #lv.append("e", "datum1")
    #lv.data_selection = "datum2"
    # assign some event handlers:
    #lv.onitemselected = ""
    w.show()
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
