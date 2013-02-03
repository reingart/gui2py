import wx

"Visual Layout Designers"


# dimensions used for the handle (based on wx.lib.resizewidget)
RW_THICKNESS = 4
RW_LENGTH = 12


class BasicDesigner:
    "Simple point-and-click layout designer (support moving controls)"

    def __init__(self, wx_objs):
        self.parent = wx_objs[0]
        self.current = {}
        self.resizing = False
        # bind all objects that can be controlled by this class
        for wx_obj in wx_objs:
            wx_obj.Bind(wx.EVT_LEFT_DOWN, self.mouse_down)
            wx_obj.Bind(wx.EVT_MOTION, self.mouse_move)
            wx_obj.Bind(wx.EVT_LEFT_UP, self.mouse_up)
            wx_obj.Bind(wx.EVT_MOUSE_EVENTS, self.mouse_over)

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
        
        wx_obj.CaptureMouse()


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
        if self.current or evt.LeftIsDown():
            evt.Skip()
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
            if wx_obj.HasCapture():
                wx_obj.ReleaseMouse()
            self.current = {}

    def OnLayoutNeeded(self, evt):
        self.parent.Layout()
        

if __name__ == "__main__":
    
    app = wx.App()
    f = wx.Frame(None, -1, 'designer.py')
    b1 = wx.Button(f, -1, "foo")
    b2 = wx.Button(f, -1, "bar")
    d = BasicDesigner([f, b1, b2])
    f.Show()
    app.MainLoop()
    
