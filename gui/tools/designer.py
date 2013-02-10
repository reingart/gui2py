import wx

"Visual Layout Designers"

DEBUG = False

# dimensions used for the handle (based on wx.lib.resizewidget)
RW_THICKNESS = 4
RW_LENGTH = 12

# colors for the handle (based on wx.lib.resizewidget)
RW_PEN   = 'black'
RW_FILL  = '#A0A0A0'
RW_FILL2 = '#E0E0E0'

GRID_SIZE = (10, 10)

CURSOR_HAND = wx.CURSOR_HAND
CURSOR_MOVING = wx.CURSOR_RIGHT_ARROW
CURSOR_SIZING = wx.CURSOR_SIZENWSE

class BasicDesigner:
    "Simple point-and-click layout designer (support moving controls)"

    def __init__(self, parent, inspector=None):
        self.parent = parent
        self.current = {}
        self.selection = []
        self.resizing = False
        # bind all objects that can be controlled by this class
        parent.designer = self
        self.inspector = inspector
        self.last_wx_obj = None     # used to draw the resize handle
        

    def hit_test(self, wx_obj, pos):
        # is the position in the area to be used for the resize handle?
        w, h = wx_obj.GetSize()
        if ( w - RW_THICKNESS * 3 <= pos.x <= w 
             and h - RW_LENGTH * 3 <= pos.y <= h ):
            return True
        if ( w - RW_LENGTH * 3 <= pos.x <= w 
             and h - RW_THICKNESS * 3 <= pos.y <= h ):
            return True
        return False

    def adjust_new_size(self, wx_obj, new_size):
        if new_size.width < RW_LENGTH:
            new_size.width = RW_LENGTH
        if new_size.height < RW_LENGTH:
            new_size.height = RW_LENGTH
            
        if wx_obj:
            minsize = wx_obj.GetMinSize()
            if minsize.width != -1 and new_size.width - RW_THICKNESS < minsize.width:
                new_size.width = minsize.width + RW_THICKNESS
            if minsize.height != -1 and new_size.height - RW_THICKNESS < minsize.height:
                new_size.height = minsize.height + RW_THICKNESS
            maxsize = wx_obj.GetMaxSize()
            if maxsize.width != -1 and new_size.width - RW_THICKNESS > maxsize.width:
                new_size.width = maxsize.width + RW_THICKNESS
            if maxsize.height != -1 and new_size.height - RW_THICKNESS > maxsize.height:
                new_size.height = maxsize.height + RW_THICKNESS
    

    def mouse_down(self, evt): 
        "Get the selected object and store start position"
        if DEBUG: print "down!"
        wx_obj = evt.GetEventObject()
        if wx_obj.Parent is None:
            evt.Skip()
            if not evt.ControlDown():
                self.selection = []  # clear previous selection
            if self.inspector and hasattr(wx_obj, "obj"):
                self.inspector.inspect(wx_obj.obj)  # inspect top level window
        else:
            if DEBUG: print wx_obj
            sx, sy = wx_obj.ScreenToClient(wx_obj.GetPositionTuple())
            dx, dy = wx_obj.ScreenToClient(wx.GetMousePosition())
            self.current['pos'] = wx_obj.ScreenToClient(wx.GetMousePosition())
            self.current['start'] = (sx - dx, sy - dy)
            self.current['wx_obj'] = wx_obj
            self.resizing = self.hit_test(wx_obj, evt.GetPosition())
            if DEBUG: print "capture..."
            # do not capture on TextCtrl, it will fail (blocking) at least in gtk
            self.parent.wx_obj.CaptureMouse()


    def mouse_move(self, evt):
        "Move the selected object"
        if DEBUG: print "move!"
        if self.current:
            wx_obj = self.current['wx_obj']
            sx, sy = self.current['start']
            x, y = wx.GetMousePosition()
            if self.resizing:
                # calculate the pos (minus the offset, not in a panel like rw!)
                #dx, dy = wx_obj.ScreenToClient(wx.GetMousePosition())
                pos = wx_obj.ScreenToClient(wx.GetMousePosition())
                x, y = pos
                if evt.ShiftDown():     # snap to grid:
                    x = x / GRID_SIZE[0] * GRID_SIZE[0]
                    y = y / GRID_SIZE[1] * GRID_SIZE[1]
                pos = wx.Point(x, y)
                delta = self.current['pos'] - pos 
                new_size = wx_obj.GetSize() - delta.Get()
                self.adjust_new_size(wx_obj, new_size)
                if new_size != wx_obj.GetSize():
                    # reset margins (TODO: avoid resizing recursion)
                    wx_obj.obj.margin_left = 0
                    wx_obj.obj.margin_right = 0
                    wx_obj.obj.margin_top = 0
                    wx_obj.obj.margin_bottom = 0
                    wx_obj.obj.size = new_size    # update gui specs
                    self.current['pos'] = pos
                    ##self._bestSize = new_size 
            else:
                # update gui specs (this will overwrite relative dimensions):
                x, y = (x + sx, y + sy)
                if evt.ShiftDown():     # snap to grid:
                    x = x / GRID_SIZE[0] * GRID_SIZE[0]
                    y = y / GRID_SIZE[1] * GRID_SIZE[1]
                wx_obj.obj.pos = (wx.Point(x, y))
                    
    def draw_grip(self, wx_obj):
        "draw the resize handle"
        # TODO: draw a transparent panel over the widget (to catch all events)
        if self.last_wx_obj and self.last_wx_obj != wx_obj:
            self.last_wx_obj.Refresh()
        if wx_obj:
            dc = wx.ClientDC(wx_obj)
            w,h = wx_obj.GetSize()
            points = [ (w - 1,            h - RW_LENGTH),
                       (w - RW_THICKNESS, h - RW_LENGTH),
                       (w - RW_THICKNESS, h - RW_THICKNESS),
                       (w - RW_LENGTH,    h - RW_THICKNESS),
                       (w - RW_LENGTH,    h - 1),
                       (w - 1,            h - 1),
                       (w - 1,            h - RW_LENGTH),
                       ]
            dc.SetPen(wx.Pen(RW_PEN, 1))
            fill = RW_FILL
            dc.SetBrush(wx.Brush(fill))
            dc.DrawPolygon(points)
        self.last_wx_obj = wx_obj        

    def __call__(self, evt):
        "Handler for EVT_MOUSE_EVENTS (binded in design mode)"
        if evt.IsCommandEvent():
            # menu clicked
            if self.inspector:
                wx_obj = evt.GetEventObject()
                if isinstance(wx_obj, wx.Frame):
                    wx_obj = wx_obj.GetMenuBar()    # wx28/MSW
                obj = wx_obj.obj.find(evt.GetId())
                self.inspector.inspect(obj)
        elif evt.GetEventType() == wx.EVT_PAINT.typeId:
            wx_obj = evt.GetEventObject()
            if isinstance(wx_obj, wx.Frame):
                self.draw_grid(evt)
            else:
                evt.Skip()  # call the default handler
        elif evt.GetEventType() == wx.EVT_SIZE.typeId:
            # update the size in the propeditor (only for the top level window)
            obj = evt.GetEventObject().obj
            if not obj.get_parent():  
                w, h = obj.size
                if w and h:
                    obj._width, obj._height = "%spx" % w, "%spx" % str(h)
                    wx.CallAfter(self.inspector.inspect, obj)
            evt.Skip()  # call the default handler
        elif evt.GetEventType() == wx.EVT_KEY_DOWN.typeId:
            self.key_press(evt)
        elif evt.GetEventType() == wx.EVT_KEY_UP.typeId:
            if not evt.ControlDown():
                self.selection = []     # clear selection
        elif self.current or evt.LeftIsDown():
            if evt.LeftDown():
                self.mouse_down(evt)
            elif evt.LeftUp():
                self.mouse_up(evt)
            else:
                self.mouse_move(evt)
        else:
            wx_obj = evt.GetEventObject()
            if wx_obj is not self.parent.wx_obj:
                if not self.hit_test(wx_obj, evt.GetPosition()):
                    wx_obj.SetCursor(wx.StockCursor(CURSOR_HAND))
                else:
                    wx_obj.SetCursor(wx.StockCursor(CURSOR_SIZING))
                self.draw_grip(wx_obj)      # draw the resize handle (SW)
            else: 
                self.draw_grip(None)        # clear the resize handle
            

    def mouse_up(self, evt):
        "Release the selected object"
        if DEBUG: print "up!"
        if self.current: 
            wx_obj = self.current['wx_obj']
            if self.parent.wx_obj.HasCapture():
                self.parent.wx_obj.ReleaseMouse()
            self.current = {}
            if self.inspector:
                self.inspector.inspect(wx_obj.obj)
            # keep selected object (for keypress)
            self.selection.append(wx_obj)
            if DEBUG: print "SELECTION", self.selection

    def key_press(self, event):
        "support cursor keys to move components one pixel at a time"
        key = event.GetKeyCode()
        if key in (wx.WXK_LEFT, wx.WXK_UP, wx.WXK_RIGHT, wx.WXK_DOWN):
            for wx_obj in self.selection:
                x, y = wx_obj.GetPosition()
                if event.ShiftDown():     # snap to grid:
                    # for now I'm only going to align to grid
                    # in the direction of the cursor movement 
                    if key == wx.WXK_LEFT:
                        x = (x - GRID_SIZE[0]) / GRID_SIZE[0] * GRID_SIZE[0]
                    elif key == wx.WXK_RIGHT:
                        x = (x + GRID_SIZE[0]) / GRID_SIZE[0] * GRID_SIZE[0]
                    elif key == wx.WXK_UP:
                        y = (y - GRID_SIZE[1]) / GRID_SIZE[1] * GRID_SIZE[1]
                    elif key == wx.WXK_DOWN:
                        y = (y + GRID_SIZE[1]) / GRID_SIZE[1] * GRID_SIZE[1]
                else:
                    if key == wx.WXK_LEFT:
                        x = x - 1
                    elif key == wx.WXK_RIGHT:
                        x = x + 1
                    elif key == wx.WXK_UP:
                        y = y - 1
                    elif key == wx.WXK_DOWN:
                        y = y + 1
                wx_obj.SetPosition((x, y))
                # make sure sizing handles follow component
                ##self.showSizingHandles(name)
                # update the position on the propertyEditor status bar
                ##self.setToolTipDrag(name, (x, y), self.components[name].size)

    def draw_grid(self, event):
        wx_obj = event.GetEventObject()
        dc = wx.PaintDC(wx_obj)
        brush = dc.GetBackground()
        brush.SetColour(wx_obj.GetBackgroundColour())
        dc.SetBackground(brush)
        dc.Clear()
        # should the color be settable by the user and then save
        # that in the prefs?
        dc.SetPen(wx.Pen('darkgray', 1, wx.SOLID))
        w, h = wx_obj.GetClientSize()
        xgrid, ygrid = GRID_SIZE
        nx = w / xgrid
        ny = h / ygrid
        for x in range(1, nx + 1):
            for y in range(1, ny + 1):
                dc.DrawPoint(x * xgrid, y * ygrid)

    def OnLayoutNeeded(self, evt):
        self.parent.wx_obj.Layout()


def save(evt):
    "Basic save functionality: just replaces the gui code"
    wx_obj = evt.GetEventObject()
    w = wx_obj.obj
    if DEBUG: print "saving..."
    # make a backup:
    fin = open("sample.pyw", "ru")
    fout = open("sample.pyw.bak", "w")
    fout.write(fin.read())
    fout.close()
    fin.close()
    # reopen the files to proccess them
    fin = open("sample.pyw.bak", "ru")
    fout = open("sample.pyw", "w")
    copy = True
    newlines = fin.newlines or "\n"

    def dump(obj):
        "recursive convert object to string"
        for ctl in obj:
            fout.write(str(ctl))
            fout.write(newlines)
            dump(ctl)

    for line in fin:
        if line.startswith("# --- gui2py designer start ---"):
            fout.write(line)
            fout.write(newlines)
            fout.write(str(w))
            fout.write(newlines)
            dump(w)
            fout.write(newlines)
            copy = False
        if line.startswith("# --- gui2py designer end ---"):
            copy = True
        if copy:
            fout.write(line)
            #fout.write("\n\r")
    fout.close()
    fin.close()
    exit()


if __name__ == '__main__':
    # basic proof-of-concept visual gui designer
    
    import sys,os
    
    #    
    os.environ['UBUNTU_MENUPROXY'] = '0'
    app = wx.App(redirect=None)    

    # import controls (fill the registry!)
    from gui.windows import Window
    import gui.controls
    import gui.menu

    # import tools used by the designer
    from gui.tools.inspector import InspectorPanel
    from gui.tools.propeditor import PropertyEditorPanel
    from gui.tools.designer import BasicDesigner
    from gui.tools.toolbox import ToolBox, ToolBoxDropTarget

    # create the windows and the property editor / inspector
    if DEBUG:
        log = sys.stdout
    else:
        log = open(os.devnull, 'w')
        
    f1 = wx.Frame(None, pos=(600, 0), size=(300, 300), 
                        title="GUI Property Editor")
    f2 = wx.Frame(None, pos=(600, 350), size=(300, 300), title="GUI Inspector")
    propeditor = PropertyEditorPanel(f2, log)
    inspector = InspectorPanel(f1, propeditor, log)
    f1.Show()
    f2.Show()
    
    # create a toolbox 
    frame = wx.Frame(None, pos=(0, 0), size=(100, 400), title="GUI Toolbox")
    tb = ToolBox(frame)

    filename = "sample.pyw"
    vars = {}
    execfile(filename, vars)
    w = None
    for name, value in vars.items():
        if not isinstance(value, Window):
            continue
        w = value       # TODO: support many windows
        # load the window in the widget inspector
        inspector.load_object(w)
        # associate the window with the designer: 
        # (override mouse events to allow moving and resizing)
        designer = BasicDesigner(w, inspector)
        # associate the window with the toolbox:
        # (this will allow to drop new controls on the window)
        dt = ToolBoxDropTarget(w, designer=designer, inspector=inspector)
        w.drop_target = dt
        # link the designer (context menu)
        inspector.set_designer(designer)
        w.show()

    w.wx_obj.Bind(wx.EVT_CLOSE, save) 
    
    frame.Show()
    tb.Show()
    
    app.MainLoop()

