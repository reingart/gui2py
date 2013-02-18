import wx
import os, sys

import gui.controls

from gui import registry


try:
    from agw import aui
    from agw.aui import aui_switcherdialog as ASD
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
    from wx.lib.agw.aui import aui_switcherdialog as ASD


DEBUG = False


class ToolBox(aui.AuiToolBar):
    "AUI ToolBar showing gui controls, capable of Drag & Drop"
    
    def __init__(self, parent):
        aui.AuiToolBar.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize,
                                 agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERTICAL | aui.AUI_TB_TEXT)

        self.default_tlw = None
        self.desinger = self.inspector = None
        prepend_items, append_items = [],[]
        self.SetToolBitmapSize(wx.Size(48, 48))
        #self.AddSimpleTool(ID_SampleItem+30, "Test", wx.ArtProvider.GetBitmap(wx.ART_ERROR))
        #self.AddSeparator()
        
        # store assoc of wx ID -> gui control (for drag&drop)
        self.menu_ctrl_map = {}
        
        # create a toolbar item for each control (ignore those that have no image)
        for name, ctrl in registry.CONTROLS.items():
            if ctrl._image:
                menu_id = wx.NewId()
                self.menu_ctrl_map[menu_id] = ctrl
                self.AddSimpleTool(menu_id, name, ctrl._image.GetBitmap())
                self.Bind(wx.EVT_MENU, self.tool_click, id=menu_id)

        # Handle "A drag operation involving a toolbar item has started"
        self.Bind(aui.EVT_AUITOOLBAR_BEGIN_DRAG, self.start_drag_opperation)

        # this can be useful in the future (TODO: multiple columns or groups)
        self.SetCustomOverflowItems(prepend_items, append_items)
        self.Realize()

    def tool_click(self, evt):
        "Event handler tool selection (just add to default handler)"
    
        # get the control
        ctrl = self.menu_ctrl_map[evt.GetId()]
        # create the control on the parent:
        if self.default_tlw:
            obj = ctrl(self.default_tlw, 
                       name="%s_%s" % (ctrl._meta.name.lower(), wx.NewId()), 
                       pos=(0, 0), designer=self.designer)
        # fix width and height if default is not visible
        w, h = obj.size
        if w < 10:
            w = 100
        if h < 10:
            h = 10
        obj.size = (w, h)
        # update the object at the inspector (to show the new control)
        if self.inspector:
            self.inspector.load_object(self.default_tlw)
            self.inspector.inspect(obj)
        
        
    def start_drag_opperation(self, evt):
        "Event handler for drag&drop functionality"
    
        # get the control
        ctrl = self.menu_ctrl_map[evt.GetToolId()]

        # create our own data format and use it in a custom data object
        ldata = wx.CustomDataObject("gui")
        ldata.SetData(ctrl._meta.name)      # only strings are allowed!

        # Also create a Bitmap version of the drawing
        bmp = ctrl._image.GetBitmap()

        # Now make a data object for the bitmap and also a composite
        # data object holding both of the others.
        bdata = wx.BitmapDataObject(bmp)
        data = wx.DataObjectComposite()
        data.Add(ldata)
        data.Add(bdata)

        # And finally, create the drop source and begin the drag
        # and drop opperation
        dropSource = wx.DropSource(self)
        dropSource.SetData(data)
        if DEBUG: print("Begining DragDrop\n")
        result = dropSource.DoDragDrop(wx.Drag_AllowMove)
        if DEBUG: print("DragDrop completed: %d\n" % result)

        if result == wx.DragMove:
            if DEBUG: print "dragmove!"
            self.Refresh()

    def set_default_tlw(self, tlw, designer, inspector):
        "track default top level window for toolbox menu default action"
        self.default_tlw = tlw
        self.designer = designer
        self.inspector = inspector


class ToolBoxDropTarget(wx.PyDropTarget):
    "Target of Drag&Drop operation (will create the dropped control)"
    
    def __init__(self, window, designer=None, inspector=None):
        wx.PyDropTarget.__init__(self)
        self.dv = window
        self.designer = designer  # used in design mode (set special handlers)
        self.inspector = inspector

        # specify the type of data we will accept
        self.data = wx.CustomDataObject("gui")
        self.SetDataObject(self.data)

    # some virtual methods that track the progress of the drag
    def OnEnter(self, x, y, d):
        if DEBUG: print("OnEnter: %d, %d, %d\n" % (x, y, d))
        return d

    def OnLeave(self):
        if DEBUG: print("OnLeave\n")

    def OnDrop(self, x, y):
        if DEBUG: print("OnDrop: %d %d\n" % (x, y))
        return True

    def OnDragOver(self, x, y, d):
        #self.log.WriteText("OnDragOver: %d, %d, %d\n" % (x, y, d))

        # The value returned here tells the source what kind of visual
        # feedback to give.  For example, if wxDragCopy is returned then
        # only the copy cursor will be shown, even if the source allows
        # moves.  You can use the passed in (x,y) to determine what kind
        # of feedback to give.  In this case we return the suggested value
        # which is based on whether the Ctrl key is pressed.
                
        if self.inspector:
            self.inspector.highlight(self.dv.wx_obj)   # show the possible drop target

        return d

    # Called when OnDrop returns True.  We need to get the data and
    # do something with it.
    def OnData(self, x, y, d):
        if DEBUG: print("OnData: %d, %d, %d\n" % (x, y, d))

        # copy the data from the drag source to our data object
        if self.GetData():
            # convert it back to a list of lines and give it to the viewer
            ctrl_name = self.data.GetData()
            ctrl = registry.CONTROLS[ctrl_name]
            # create the control on the parent:
            obj = ctrl(self.dv, 
                       name="%s_%s_%s" % (ctrl_name.lower(), x, y), 
                       pos=(x, y), designer=self.designer)
            # set default dimensions (width and height determined by wx):
            if hasattr(obj, "pos"):     # only Controls
                obj.left, obj.top = ["%spx" % dim for dim in obj.pos] 
                obj.width, obj.height = ["%spx" % dim for dim in obj.size]
            # update the object at the inspector (to show the new control)
            if self.inspector:
                self.inspector.load_object(self.dv)
                self.inspector.inspect(obj)

        # what is returned signals the source what to do
        # with the original data (move, copy, etc.)  In this
        # case we just return the suggested value given to us.
        return d  
               
        
if __name__ == '__main__':
    import sys,os
    app = wx.App()
    
    frame = wx.Frame(None)  # create a sample parent frame
    frame.Show()            # note: without AUI, this will look ugly
    tb = ToolBox(frame)     # create the toolbar
    tb.Show()

    # create a sample gui window
    from gui.windows import Window
    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False)
    w.show()
    # set the drop target (where controls will be created)
    dt = ToolBoxDropTarget(w.wx_obj)
    w.wx_obj.SetDropTarget(dt)

    app.MainLoop()

