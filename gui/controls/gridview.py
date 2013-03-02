
import wx
import wx.grid as gridlib

from ..event import GridEvent
from ..component import Control, Component
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .. import registry
from .. import images


class wx_Grid(gridlib.Grid):
    "Simple Grid control"
    # initially based on GridSimple.py wxPython demo
    
    def __init__(self, parent, *args, **kwargs):
        gridlib.Grid.__init__(self, parent, -1)
        ##mixins.GridAutoEditMixin.__init__(self)

        self.CreateGrid(25, 25)
        ##self.EnableEditing(False)

        # simple cell formatting
        self.SetColSize(3, 200)
        self.SetRowSize(4, 45)
        self.SetCellValue(0, 0, "First cell")
        self.SetCellValue(1, 1, "Another cell")
        self.SetCellValue(2, 2, "Yet another cell")
        self.SetCellValue(3, 3, "This cell is read-only")
        self.SetCellFont(0, 0, wx.Font(12, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        self.SetCellTextColour(1, 1, wx.RED)
        self.SetCellBackgroundColour(2, 2, wx.CYAN)
        self.SetReadOnly(3, 3, True)

        self.SetCellEditor(5, 0, gridlib.GridCellNumberEditor(1,1000))
        self.SetCellValue(5, 0, "123")
        self.SetCellEditor(6, 0, gridlib.GridCellFloatEditor())
        self.SetCellValue(6, 0, "123.34")
        self.SetCellEditor(7, 0, gridlib.GridCellNumberEditor())

        self.SetCellValue(6, 3, "You can veto editing this cell")

        #self.SetRowLabelSize(0)
        #self.SetColLabelSize(0)

        # attribute objects let you keep a set of formatting values
        # in one spot, and reuse them if needed
        attr = gridlib.GridCellAttr()
        attr.SetTextColour(wx.BLACK)
        attr.SetBackgroundColour(wx.RED)
        attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        # you can set cell attributes for the whole row (or column)
        self.SetRowAttr(5, attr)

        self.SetColLabelValue(0, "Custom")
        self.SetColLabelValue(1, "column")
        self.SetColLabelValue(2, "labels")

        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)

        #self.SetDefaultCellOverflow(False)
        #r = gridlib.GridCellAutoWrapStringRenderer()
        #self.SetCellRenderer(9, 1, r)

        # overflow cells
        self.SetCellValue( 9, 1, "This default cell will overflow into neighboring cells, but not if you turn overflow off.");
        self.SetCellSize(11, 1, 3, 3);
        self.SetCellAlignment(11, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE);
        self.SetCellValue(11, 1, "This cell is set to span 3 rows and 3 columns");


        editor = gridlib.GridCellTextEditor()
        editor.SetParameters('10')
        self.SetCellEditor(0, 4, editor)
        self.SetCellValue(0, 4, "Limited text")

        renderer = gridlib.GridCellAutoWrapStringRenderer()
        self.SetCellRenderer(15,0, renderer)
        self.SetCellValue(15,0, "The text in this cell will be rendered with word-wrapping")


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
