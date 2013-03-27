
import wx
from ..component import Control, Spec, StyleSpec, InitSpec
from .. import images 


class Line(Control):
    "A simple push-button with a label (or image)"
    _wx_class = wx.StaticLine
    _image = images.line
    
    layout = StyleSpec({'vertical': wx.LI_VERTICAL, 
                        'horizontal': wx.LI_HORIZONTAL},  
                        default='horizontal', doc="Line layout")
    label = None

    
if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    b = Line(frame, name="line", layout='vertical')
    frame.Show()
    app.MainLoop()
