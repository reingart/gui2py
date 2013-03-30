import wx
import wx.lib.agw.supertooltip as STT
from .. import images

"Visual Layout Designers"

DEBUG = False

GRID_SIZE = (10, 10)

CURSOR_HAND = wx.CURSOR_HAND
CURSOR_MOVING = wx.CURSOR_RIGHT_ARROW
CURSOR_SIZING = wx.CURSOR_SIZENWSE


class BasicDesigner:
    "Simple point-and-click layout designer (supports move & resize controls)"

    def __init__(self, parent, inspector=None):
        self.parent = parent
        self.current = None
        self.selection = []
        self.resizing = False
        # bind all objects that can be controlled by this class
        parent.designer = self
        self.inspector = inspector
        self.last_wx_obj = None     # used to draw the resize handle
        self.onclose = None
        self.timestamp = None       # used to track double clicks on MSW
        self.last_xy = None         # last clicked position

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
                # update the selection markers position (needed if using sizer!)
                for obj in self.selection:
                    wx.CallAfter(obj.sel_marker.update)
            evt.Skip()  # call the default handler
        elif evt.GetEventType() == wx.EVT_CLOSE.typeId:
            # call the external close handler (useful to save)
            if self.onclose:
                if not self.onclose(evt, self):
                    evt.Veto()  # if onclose returns False, close is ignored
                else:
                    evt.Skip() 
        elif evt.GetEventType() == wx.EVT_KEY_DOWN.typeId:
            self.key_press(evt)
        elif evt.GetEventType() == wx.EVT_LEFT_DOWN.typeId:
            # calculate time between clicks (is this a double click?)
            if not self.timestamp or evt.Timestamp - self.timestamp > 1000 or \
                   self.last_xy != evt.GetPositionTuple():
                # no, process normal mouse click and store obj for later dclick
                self.mouse_down(evt)
                self.last_obj = getattr(evt.GetEventObject(), "obj")
            elif self.inspector:
                # on dclick, inspect & edit the default property (ie label)
                wx.CallAfter(self.inspector.inspect, self.last_obj, False, True)
            self.timestamp = evt.Timestamp
            self.last_xy = evt.GetPositionTuple()
        elif evt.GetEventType() == wx.EVT_LEFT_UP.typeId:
            self.mouse_up(evt)
        elif evt.GetEventType() == wx.EVT_MOTION.typeId:
            # wait 500ms before EVT_LEFT_DOWN to prevent accidental moves
            if self.timestamp and evt.Timestamp - self.timestamp > 500:
                self.mouse_move(evt)
        elif evt.GetEventType() == wx.EVT_RIGHT_DOWN.typeId and self.inspector:
            # on right click, inspect and pop up the context menu
            # do this after this event to prevent reference issues (deletions!)
            self.current = None
            wx.CallAfter(self.inspector.inspect, 
                         getattr(evt.GetEventObject(), "obj"), True, True, 
                         evt.GetPositionTuple())
        # allow default behavior (set focus / tab change):
        if isinstance(evt.GetEventObject(), wx.Notebook):
            evt.Skip()
       
    def mouse_down(self, evt): 
        "Get the selected object and store start position"
        if DEBUG: print "down!"
        if not evt.ControlDown() and not evt.ShiftDown():
            for obj in self.selection:
                # clear marker
                if obj.sel_marker:
                    obj.sel_marker.show(False)
                    obj.sel_marker.destroy()
                    obj.sel_marker = None
            self.selection = []  # clear previous selection

        wx_obj = evt.GetEventObject()

        if wx_obj.Parent is None:
            evt.Skip()
            #if self.inspector and hasattr(wx_obj, "obj"):
            #    self.inspector.inspect(wx_obj.obj)  # inspect top level window
            #self.dclick = False
        else:
            # create the selection marker and assign it to the control
            obj = wx_obj.obj
            if DEBUG: print wx_obj
            sx, sy = wx_obj.ScreenToClient(wx_obj.GetPositionTuple())
            dx, dy = wx_obj.ScreenToClient(wx.GetMousePosition())
            self.pos = wx_obj.ScreenToClient(wx.GetMousePosition())
            self.start = (sx - dx, sy - dy)
            self.current = wx_obj
            if DEBUG: print "capture..."
            # do not capture on TextCtrl, it will fail (blocking) at least in gtk
            # do not capture on wx.Notebook to allow selecting the tabs
            if not isinstance(wx_obj, wx.Notebook):
                self.parent.wx_obj.CaptureMouse()
            self.select(obj, keep_selection=True)

    def mouse_move(self, evt):
        "Move the selected object"
        if DEBUG: print "move!"
        if self.current:
            wx_obj = self.current
            sx, sy = self.start
            x, y = wx.GetMousePosition()
            # update gui specs (this will overwrite relative dimensions):
            x, y = (x + sx, y + sy)
            if evt.ShiftDown():     # snap to grid:
                x = x / GRID_SIZE[0] * GRID_SIZE[0]
                y = y / GRID_SIZE[1] * GRID_SIZE[1]
            wx_obj.obj.pos = (wx.Point(x, y))

    def do_resize(self, evt, wx_obj, (n, w, s, e)):
        "Called by SelectionTag"
        # calculate the pos (minus the offset, not in a panel like rw!)
        pos = wx_obj.ScreenToClient(wx.GetMousePosition())
        x, y = pos
        if evt.ShiftDown():     # snap to grid:
            x = x / GRID_SIZE[0] * GRID_SIZE[0]
            y = y / GRID_SIZE[1] * GRID_SIZE[1]
        pos = wx.Point(x, y)
        if not self.resizing or self.resizing != (wx_obj, (n, w, s, e)):
            self.pos = list(pos)                        # store starting point
            self.resizing = (wx_obj, (n, w, s, e))      # track obj and handle
        else:
            delta = pos - self.pos 
            if DEBUG: print "RESIZING: n, w, s, e", n, w, s, e
            if n or w or s or e:
                # resize according the direction (n, w, s, e)
                x = wx_obj.Position[0] + e * delta[0]
                y = wx_obj.Position[1] + n * delta[1]
                if not isinstance(wx_obj, wx.TopLevelWindow):
                    width = wx_obj.Size[0] + (w - e) * delta[0]
                else:
                    width = wx_obj.ClientSize[0] + (w - e) * delta[0]
                if n or s:
                    height = wx_obj.Size[1] + (s - n) * delta[1]
                else:
                    height = None
            else:
                # just move
                x = wx_obj.Position[0] + delta[0]
                y = wx_obj.Position[1] + delta[1]
                width = height = None
            new_pos = (x, y)
            new_size = (width, height)
            if new_size != wx_obj.GetSize() or new_pos != wx_obj.GetPosition():
                # reset margins (TODO: avoid resizing recursion)
                wx_obj.obj.margin_left = 0
                wx_obj.obj.margin_right = 0
                wx_obj.obj.margin_top = 0
                wx_obj.obj.margin_bottom = 0
                wx_obj.obj.pos = new_pos      # update gui specs (position)
                # update gui specs (size), but do not alter default value
                if width is not None and height is not None:
                    wx_obj.obj.size = new_size
                elif width is not None:
                    wx_obj.obj.width = width
                elif height is not None:
                    wx_obj.obj.height = height
                # only update on sw for a smooth resize
                if w:
                    self.pos[0] = pos[0]        # store new starting point
                if s:
                    self.pos[1] = pos[1]        # store new starting point

    def mouse_up(self, evt):
        "Release the selected object"
        if DEBUG: print "up!"
        self.resizing = False
        if self.current: 
            wx_obj = self.current
            if self.parent.wx_obj.HasCapture():
                self.parent.wx_obj.ReleaseMouse()
            self.current = None
            if self.inspector:
                self.inspector.inspect(wx_obj.obj)
            if DEBUG: print "SELECTION", self.selection

    def key_press(self, event):
        "support cursor keys to move components one pixel at a time"
        key = event.GetKeyCode()
        if key in (wx.WXK_LEFT, wx.WXK_UP, wx.WXK_RIGHT, wx.WXK_DOWN):
            for obj in self.selection:
                x, y = obj.pos
                if event.ShiftDown():     # snap to grid:t 
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
                obj.pos = (x, y)
                # update the position on the propertyEditor status bar
                ##self.setToolTipDrag(name, (x, y), self.component[name].size)
        elif key == wx.WXK_DELETE:
            self.delete(event)
        elif key == wx.WXK_INSERT:
            self.duplicate(event)
        else:
            if DEBUG: print "KEY:", key

    def delete(self, event):
        "delete all of the selected objects"
        # get the selected objects (if any)
        for obj in self.selection:
            if obj:
                if DEBUG: print "deleting", obj.name
                obj.destroy()
        self.selection = []                         # clean selection
        self.inspector.load_object()                # reload the tree        

    def duplicate(self, event):
        "create a copy of each selected object"
        # duplicate the selected objects (if any)
        new_selection = []
        for obj in self.selection:
            if obj:
                if DEBUG: print "duplicating", obj.name
                obj.sel_marker.destroy()
                obj.sel_marker = None
                obj2 = obj.duplicate()
                obj2.sel_marker = SelectionMarker(obj2)
                obj2.sel_marker.show(True)
                new_selection.append(obj2)
        self.selection = new_selection              # update with new obj's
        self.inspector.load_object()                # reload the tree

    def select(self, obj, keep_selection=False):
        # if not keep old selection, unselect all current selected objs.
        if not keep_selection:
            while self.selection:
                old_obj = self.selection.pop()
                old_obj.sel_marker.destroy()
                old_obj.sel_marker = None
        if not obj.sel_marker:
            obj.sel_marker = SelectionMarker(obj)
            obj.sel_marker.show(True)
        self.selection.append(obj)

    def draw_grid(self, event):
        wx_obj = event.GetEventObject()
        dc = wx.PaintDC(wx_obj)
        brush = dc.GetBackground()
        brush.SetColour(wx_obj.GetBackgroundColour())
        dc.SetBackground(brush)
        #dc.Clear()
        # should the color be settable by the user and then save
        # that in the prefs?
        dc.SetPen(wx.Pen('black', 1, wx.SOLID))
        w, h = wx_obj.GetClientSize()
        xgrid, ygrid = GRID_SIZE
        nx = w / xgrid
        ny = h / ygrid
        for x in range(1, nx + 1):
            for y in range(1, ny + 1):
                dc.DrawPoint(x * xgrid, y * ygrid)

    def OnLayoutNeeded(self, evt):
        self.parent.wx_obj.Layout()


class SelectionTag(wx.Window):
    "small black squares that appear at the corners of the active widgets"

    names = ["top-left", "top-right", "bottom-right", "bottom-left", 
             "top", "right", "left", "bottom", "middle"]
    # map each size handle with cardinal points: (n, w, s, e)
    direction = [(1, 0, 0, 1), (1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 1),
                 (1, 0, 0, 0), (0, 0, 0, 1), (0, 1, 0, 0), (0, 0, 1, 0), 
                 (0, 0, 0, 0)]
    cursors = [wx.CURSOR_SIZENWSE, wx.CURSOR_SIZENESW, wx.CURSOR_SIZENWSE, 
               wx.CURSOR_SIZENESW, wx.CURSOR_SIZENS, wx.CURSOR_SIZEWE, 
               wx.CURSOR_SIZEWE, wx.CURSOR_SIZENS, wx.CURSOR_SIZING]
    
    def __init__(self, parent, owner, pos=None, index=None, designer=None):
        kwds = { 'size': (7, 7) }
        if pos:
            kwds['position'] = pos
        wx.Window.__init__(self, parent, -1, **kwds)
        if index < 8:
            self.SetBackgroundColour(wx.BLUE) #wx.BLACK)
        self.Hide()
        self.Bind(wx.EVT_MOUSE_EVENTS, self.motion)
        self.designer = designer
        self.owner = owner
        self.index = index
        self.SetCursor(wx.StockCursor(self.cursors[index]))
        self.Raise()    # put over all the other controls so it get the events!
    
    def motion(self, evt):
        if evt.LeftDown():
            self.CaptureMouse()
        if evt.LeftIsDown():
            self.designer.do_resize(evt, self.owner.wx_obj, self.direction[self.index])
        elif evt.LeftUp() and self.HasCapture():
            self.ReleaseMouse()


class SelectionMarker:
    "Collection of the 4 SelectionTagS for each widget"
    
    def __init__(self, owner, visible=False):
        self.visible = visible
        self.owner = owner
        self.parent = owner.wx_obj.GetParent()
        self.designer = owner.designer
        ##if wx.Platform == '__WXMSW__': self.parent = owner.wx_obj
        self.tag_pos = None
        self.tags = None
        #self.tags = [ SelectionTag(self.parent) for i in range(4) ]
        self.update()
        if visible:
            for t in self.tags: t.Show()

    def update(self, event=None):
        if self.owner is self.parent: x, y = 0, 0
        else: x, y = self.owner.wx_obj.GetPosition()
        w, h = self.owner.wx_obj.GetClientSize()
        def position(j):
            if not j: return x-8, y-8                       # top-left
            elif j == 1: return x + w + 1, y - 8            # top-right
            elif j == 2: return x + w + 1, y + h +1         # bottom-right
            elif j == 3: return x - 8, y + h                # bottom-left
            elif j == 4: return x + w/2 - 4, y - 8          # top
            elif j == 5: return x - 8, y + h/2 - 4          # left
            elif j == 6: return x + w + 1, y + h/2 - 3      # right
            elif j == 7: return x + w/2 - 4, y + h + 1      # bottom
            elif j == 8: return x + w/2 - 4, y + h/2 - 4    # middle
        self.tag_pos = [ position(i) for i in range(8) ]
        if self.visible:
            if not self.tags:
                self.tags = [ SelectionTag(self.parent, self.owner, index=i, designer=self.designer) for i in range(8) ]
            for i in range(8):
                self.tags[i].SetPosition(self.tag_pos[i])
        if event: event.Skip()

    def show(self, visible):
        if self.visible != visible:
            self.visible = visible
            if self.visible:
                if not self.tags:
                    self.tags = [ SelectionTag(self.parent, self.owner, index=i, designer=self.designer) for i in range(8) ]
                for i in range(8):
                    self.tags[i].SetPosition(self.tag_pos[i])
                    self.tags[i].Show()
            elif self.tags:
                for tag in self.tags: tag.Destroy()
                self.tags = None

    def destroy(self):
        if self.tags:
            for tag in self.tags: tag.Destroy()
            self.tags = None

    def reparent(self, parent):
        self.parent = parent
        if self.tags:
            for tag in self.tags: tag.Reparent(parent)


def save(evt, designer):
    "Basic save functionality: just replaces the gui code"

    # ask the user if we should save the changes:
    ok = gui.confirm("Save the changes?", "GUI2PY Designer", 
                     cancel=True, default=True)
    if ok:
        wx_obj = evt.GetEventObject()
        w = wx_obj.obj
        try:
            if DEBUG: print "saving..."
            # make a backup:
            fin = open(designer.filename, "r")
            fout = open(designer.filename + ".bak", "w")
            fout.write(fin.read())
            fout.close()
            fin.close()
            # reopen the files to proccess them
            fin = open(designer.filename + ".bak", "r")
            fout = open(designer.filename, "w")
            copy = True
            newlines = fin.newlines or "\n"

            def dump(obj):
                "recursive convert object to string"
                for ctl in obj:
                    fout.write(str(ctl))
                    fout.write(newlines)
                    dump(ctl)

            for line in fin:
                if line.startswith("# --- gui2py designer generated code starts ---"):
                    fout.write(line)
                    fout.write(newlines)
                    fout.write(str(w))
                    fout.write(newlines)
                    dump(w)
                    fout.write(newlines)
                    copy = False
                if line.startswith("# --- gui2py designer generated code ends ---"):
                    copy = True
                if copy:
                    fout.write(line)
                    #fout.write("\n\r")
            fout.close()
            fin.close()
        except Exception, e:
            import traceback
            print(traceback.print_exc())
            ok = gui.confirm("Close anyway?\n%s" % str(e), 'Unable to save:', 
                             ok=True, cancel=True)
    if ok is not None:
        wx.CallAfter(exit)    # terminate the designer program
    return ok                 # ok to close and exit! 


# show a nice and unostrusive welcome & help
    
class CustomToolTipWindow(STT.ToolTipWindow):

    def CalculateBestPosition(self,widget):
        "When dealing with a Top-Level window position it absolute lower-right"
        if isinstance(widget, wx.Frame):
            screen = wx.ClientDisplayRect()[2:]
            left,top = widget.ClientToScreenXY(0,0)
            right,bottom = widget.ClientToScreenXY(*widget.GetClientRect()[2:])
            size = self.GetSize()
            xpos = right
            ypos = bottom - size[1]
            self.SetPosition((xpos,ypos))
        else:
            STT.ToolTipWindow.CalculateBestPosition(self)

# ToolTipWindow should be redefined as it is used internally by SuperToolTip
STT.ToolTipWindow = CustomToolTipWindow

def wellcome_tip(wx_obj):
    "Show a tip message"
    
    msg = ("Close the main window to exit & save.\n"
           "Drag & Drop / Click the controls from the ToolBox to create new ones.\n"
           "Left click on the created controls to select them.\n"
           "Double click to edit the default property.\n"
           "Right click to pop-up the context menu.\n")
    tip = STT.SuperToolTip(msg)

    tip.SetHeader("Welcome to gui2py designer!")
    tip.SetTarget(wx_obj)
    tip.SetDrawHeaderLine(True)
    tip.ApplyStyle("Office 2007 Blue")
    tip.SetDropShadow(True)
    tip.SetHeaderBitmap(images.designer.GetBitmap())
    tip.SetEndDelay(15000)                      # hide in 15 s
    wx.CallLater(1000, tip.DoShowNow)           # show the tip in 1 s
    wx.CallLater(30000, tip.EnableTip, False)   # disable the tip in 30 s
    #wx.CallLater(31000, tip.SetTarget, None)            


if __name__ == '__main__':
    # basic proof-of-concept visual gui designer
    
    import sys,os
    
    #    
    os.environ['UBUNTU_MENUPROXY'] = '0'
    app = wx.App(redirect=None)    

    # import controls (fill the registry!)
    import gui

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
        
    f1 = wx.Frame(None, pos=(600, 25), size=(300, 300), title="GUI Inspector")
    f2 = wx.Frame(None, pos=(600, 350), size=(300, 300), 
                        title="GUI Property Editor")
    propeditor = PropertyEditorPanel(f2, log)
    inspector = InspectorPanel(f1, propeditor, log)
    f1.Show()
    f2.Show()
    
    # create a toolbox 
    frame = wx.Frame(None, pos=(0, 25), size=(80, 600), title="GUI Toolbox")
    tb = ToolBox(frame)

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # let the user choose the file to edit:
        filename = gui.open_file("Select the file to edit", ".", "sample.pyw")
        if not filename:
            exit()
    
    vars = {}
    execfile(filename, vars)
    root = None
    for name, value in vars.items():
        if not isinstance(value, gui.Window):
            continue
        root = value       # TODO: support many windows
        # load the window in the widget inspector
        inspector.load_object(root)
        # associate the window with the designer: 
        # (override mouse events to allow moving and resizing)
        designer = BasicDesigner(root, inspector)
        # associate the window with the toolbox:
        # (this will allow to drop new controls on the window)
        obj = root
        def set_drop_target(obj):
            "Recursively create and set the drop target for obj and childs"
            if isinstance(obj, (gui.Panel, gui.TabPanel, gui.Window)):
                dt = ToolBoxDropTarget(obj, root, designer=designer, 
                                                  inspector=inspector)
                obj.drop_target = dt
            for child in obj:
                set_drop_target(child)
        set_drop_target(root)
        # link the designer (context menu) and toolbox (tool click)
        inspector.set_designer(designer)
        tb.set_default_tlw(root, designer, inspector)
        root.show()

    if root:
        designer.onclose = save 
        designer.filename = filename
        
        frame.Show()
        tb.Show()
        
        wellcome_tip(root.wx_obj)
        
        app.MainLoop()
    else:
        gui.alert("No window to design!")
        
