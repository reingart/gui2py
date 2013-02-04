import wx

"Visual Layout Designers"


# dimensions used for the handle (based on wx.lib.resizewidget)
RW_THICKNESS = 4
RW_LENGTH = 12


class BasicDesigner:
    "Simple point-and-click layout designer (support moving controls)"

    def __init__(self, parent, inspector=None):
        self.parent = parent
        self.current = {}
        self.resizing = False
        # bind all objects that can be controlled by this class
        parent.designer = self
        self.inspector = inspector
        

    def hit_test(self, wx_obj, pos):
        # is the position in the area to be used for the resize handle?
        w, h = wx_obj.GetSize()
        if ( w - RW_THICKNESS <= pos.x <= w 
             and h - RW_LENGTH <= pos.y <= h ):
            return True
        if ( w - RW_LENGTH <= pos.x <= w 
             and h - RW_THICKNESS <= pos.y <= h ):
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
        print "down!"
        wx_obj = evt.GetEventObject()
        if wx_obj.Parent is None:
            evt.Skip()
        else:
            print wx_obj
            sx, sy = wx_obj.ScreenToClient(wx_obj.GetPositionTuple())
            dx, dy = wx_obj.ScreenToClient(wx.GetMousePosition())
            self.current['pos'] = wx_obj.ScreenToClient(wx.GetMousePosition())
            self.current['start'] = (sx - dx, sy - dy)
            self.current['wx_obj'] = wx_obj
            self.resizing = self.hit_test(wx_obj, evt.GetPosition())
            print "capture..."
            # do not capture on TextCtrl, it will fail (blocking) at least in gtk
            self.parent.wx_obj.CaptureMouse()


    def mouse_move(self, evt):
        "Move the selected object"
        print "move!"
        if self.current:
            wx_obj = self.current['wx_obj']
            sx, sy = self.current['start']
            x, y = wx.GetMousePosition()
            if self.resizing:
                # calculate the pos (minus the offset, not in a panel like rw!)
                #dx, dy = wx_obj.ScreenToClient(wx.GetMousePosition())
                pos = wx_obj.ScreenToClient(wx.GetMousePosition())
                delta = self.current['pos'] - pos 
                new_size = wx_obj.GetSize() - delta.Get()
                self.adjust_new_size(wx_obj, new_size)
                if new_size != wx_obj.GetSize():
                    wx_obj.SetSize(new_size)
                    self.current['pos'] = pos
                    ##self._bestSize = new_size 
            else:
                wx_obj.SetPosition(wx.Point(x + sx, y + sy))

    def __call__(self, evt):
        "Handler for EVT_MOUSE_EVENTS (binded in design mode)"
        if self.current or evt.LeftIsDown():
            if evt.LeftDown():
                self.mouse_down(evt)
            elif evt.LeftUp():
                self.mouse_up(evt)
            else:
                self.mouse_move(evt)
        else:
            wx_obj = evt.GetEventObject()
            if wx_obj is not self.parent:
                if not self.hit_test(wx_obj, evt.GetPosition()):
                    wx_obj.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
                else:
                    wx_obj.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
            else: 
                pass

    def mouse_up(self, evt):
        "Release the selected object"
        print "up!"
        if self.current: 
            wx_obj = self.current['wx_obj']
            if self.parent.wx_obj.HasCapture():
                self.parent.wx_obj.ReleaseMouse()
            self.current = {}
            if self.inspector:
                self.inspector.inspect(wx_obj.reference)

    def OnLayoutNeeded(self, evt):
        self.parent.wx_obj.Layout()


def save(evt):
    "Basic save functionality: just replaces the gui code"
    w = evt.target
    print "saving..."
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
    for line in fin:
        if line.startswith("# --- gui2py designer start ---"):
            fout.write(line)
            fout.write(newlines)
            fout.write(str(w))
            fout.write(newlines)
            for ctl in w:
                fout.write(str(ctl))
                fout.write(newlines)
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
    # basic proof-of-concept visual gui2py designer
    
    import sys,os
    app = wx.App(redirect=None)    

    # import controls (fill the registry!)
    from gui2py.windows import Window
    import gui2py.controls

    # import tools used by the designer
    from gui2py.tools.inspector import InspectorPanel
    from gui2py.tools.propeditor import PropertyEditorPanel
    from gui2py.tools.designer import BasicDesigner
    from gui2py.tools.toolbox import ToolBox, ToolBoxDropTarget

    # create the windows and the property editor / inspector
    log = sys.stdout
    f1 = wx.Frame(None, pos=(600,0), size=(300, 300))
    f2 = wx.Frame(None, pos=(600,350), size=(300, 300))
    propeditor = PropertyEditorPanel(f2, log)
    inspector = InspectorPanel(f1, propeditor, log)
    f1.Show()
    f2.Show()
    
    # create a toolbox 
    frame = wx.Frame(None, pos=(0, 0), size=(100, 400))
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
        w.show()

    w.onunload = save 
    
    frame.Show()
    tb.Show()
    
    app.MainLoop()

