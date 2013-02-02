import wx
import os, sys

try:
    dirName = os.path.dirname(os.path.abspath(__file__))
except:
    dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.split(dirName)[0])

try:
    from agw import aui
    from agw.aui import aui_switcherdialog as ASD
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
    from wx.lib.agw.aui import aui_switcherdialog as ASD

ID_SampleItem = wx.ID_HIGHEST

def createtoolbar(self):
    tb5 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_OVERFLOW | aui.AUI_TB_VERTICAL)

    prepend_items, append_items = [],[]
    tb5.SetToolBitmapSize(wx.Size(48, 48))
    tb5.AddSimpleTool(ID_SampleItem+30, "Test", wx.ArtProvider.GetBitmap(wx.ART_ERROR))
    tb5.AddSeparator()
    path = os.path.join(dirName, "gui2py", "icons")
    for filename in os.listdir(path):
        if filename.endswith(".xpm"):
            bmp = wx.Bitmap(os.path.join(path, filename), wx.BITMAP_TYPE_XPM)
            tb5.AddSimpleTool(ID_SampleItem+31, "Test", bmp)
    #tb5.AddSimpleTool(ID_SampleItem+32, "Test", wx.ArtProvider.GetBitmap(wx.ART_INFORMATION))
    #tb5.AddSimpleTool(ID_SampleItem+33, "Test", wx.ArtProvider.GetBitmap(wx.ART_WARNING))
    #tb5.AddSimpleTool(ID_SampleItem+34, "Test", wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE))
    tb5.SetCustomOverflowItems(prepend_items, append_items)
    tb5.Realize()
    print aui.__file__
    return tb5
    
if __name__ == '__main__':
    import sys,os
    app = wx.App()
    f = wx.Frame(None)
    
    tb5 = createtoolbar(f)
    frame = wx.Frame(None)
    frame.Show()
    tb5.Show()
    log = sys.stdout
    f.Show()
    app.MainLoop()

