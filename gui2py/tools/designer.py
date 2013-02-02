import wx

"Visual Layout Designers"


class BasicDesigner:
    "Simple point-and-click layout designer (support moving controls)"

    def __init__(self, wx_objs):
        self.current = {}
        # bind all objects that can be controlled by this class
        for wx_obj in wx_objs:
            wx_obj.Bind(wx.EVT_LEFT_DOWN, self.mouse_down)
            wx_obj.Bind(wx.EVT_MOTION, self.mouse_move)
            wx_obj.Bind(wx.EVT_LEFT_UP, self.mouse_up)


    def mouse_down(self, evt): 
        "Get the selected object and store start position"
        print "down!"
        wx_obj = evt.GetEventObject()
        sx, sy = wx_obj.ScreenToClient(wx_obj.GetPositionTuple())
        dx, dy = wx_obj.ScreenToClient(wx.GetMousePosition())
        self.current['start'] = (sx - dx, sy - dy)
        self.current['wx_obj'] = wx_obj
        
        wx_obj.CaptureMouse()

    def mouse_move(self, evt):
        "Move the selected object"
        print "move!"
        if self.current:
            wx_obj = self.current['wx_obj']
            sx, sy = self.current['start']
            x, y = wx.GetMousePosition()
            wx_obj.SetPosition(wx.Point(x + sx, y + sy))

    def mouse_up(self, evt):
        "Release the selected object"
        print "up!"
        if self.current: 
            self.current['wx_obj'].ReleaseMouse()
            self.current = {}


if __name__ == "__main__":
    app = wx.App()
    f = wx.Frame(None, -1, 'designer.py')
    b1 = wx.Button(f, -1, "foo")
    b2 = wx.Button(f, -1, "bar")
    d = BasicDesigner([f, b1, b2])
    f.Show()
    app.MainLoop()
    
