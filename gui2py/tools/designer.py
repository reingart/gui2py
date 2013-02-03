import wx

"Visual Layout Designers"


# dimensions used for the handle (based on wx.lib.resizewidget)
RW_THICKNESS = 4
RW_LENGTH = 12


class BasicDesigner:
    "Simple point-and-click layout designer (support moving controls)"

    def __init__(self, parent):
        self.parent = parent.wx_obj
        self.current = {}
        self.resizing = False
        # bind all objects that can be controlled by this class
        self.capture(parent)

    def capture(self, obj):
        print "binding", obj.name
        # remove all binded events:
        obj.wx_obj.Unbind(wx.EVT_MOTION)
        obj.wx_obj.Unbind(wx.EVT_LEFT_DOWN)
        obj.wx_obj.Unbind(wx.EVT_LEFT_UP)
        obj.wx_obj.Unbind(wx.EVT_LEFT_DCLICK)
        obj.wx_obj.Unbind(wx.EVT_RIGHT_DOWN)
        obj.wx_obj.Unbind(wx.EVT_RIGHT_UP)
        obj.wx_obj.Unbind(wx.EVT_RIGHT_DCLICK)
        obj.wx_obj.Unbind(wx.EVT_MOUSE_EVENTS)
        obj.wx_obj.Unbind(wx.EVT_ENTER_WINDOW)
        obj.wx_obj.Unbind(wx.EVT_LEAVE_WINDOW)
        # connect our mouse event handler:
        obj.wx_obj.Bind(wx.EVT_MOUSE_EVENTS, self.mouse_over)
        for ctrl in obj:
            self.capture(ctrl)

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
        print wx_obj
        sx, sy = wx_obj.ScreenToClient(wx_obj.GetPositionTuple())
        dx, dy = wx_obj.ScreenToClient(wx.GetMousePosition())
        self.current['pos'] = wx_obj.ScreenToClient(wx.GetMousePosition())
        self.current['start'] = (sx - dx, sy - dy)
        self.current['wx_obj'] = wx_obj
        self.resizing = self.hit_test(wx_obj, evt.GetPosition())
        print "capture..."
        # do not capture on TextCtrl, it will fail (blocking) at least in gtk
        self.parent.CaptureMouse()


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

    def mouse_over(self, evt):
        print "over!"
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
            if self.parent.HasCapture():
                self.parent.ReleaseMouse()
            self.current = {}

    def OnLayoutNeeded(self, evt):
        self.parent.Layout()
        

if __name__ == "__main__":
    from gui2py.controls import Button, Label, TextBox, CheckBox, ListBox, ComboBox
    from gui2py.windows import Window
    
    app = wx.App()
    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False)
               
    o = Button(w, name="btnTest1", label="click me!", default=True)
    o = Button(w, name="btnTest2", label="click me!", default=True)
    o = Label(w, name="lblTest", alignment="right", size=(-1, 500), text="hello!")
    o = TextBox(w, name="txtTest", border=False, text="hello world!")
    d = BasicDesigner(w)
    w.show()
    app.MainLoop()
    
