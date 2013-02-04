
import  wx
import  wx.gizmos   as  gizmos

from gui2py import registry
from gui2py.tools.propeditor import PropertyEditorPanel

#----------------------------------------------------------------------

class InspectorPanel(wx.Panel):
    def __init__(self, parent, propeditor, log):
        self.log = log
        self.propeditor = propeditor
        wx.Panel.__init__(self, parent, -1)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = gizmos.TreeListCtrl(self, -1, style =
                                        wx.TR_DEFAULT_STYLE
                                        | wx.TR_HAS_BUTTONS
                                        #| wx.TR_TWIST_BUTTONS
                                        | wx.TR_ROW_LINES
                                        | wx.TR_COLUMN_LINES
                                        #| wx.TR_NO_LINES 
                                        | wx.TR_FULL_ROW_HIGHLIGHT
                                   )

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        self.images_map = {}
        for name, ctrl in registry.CONTROLS.items() + registry.WINDOWS.items():
            if ctrl._image:
                #bmp = wx.Bitmap(os.path.join(path, filename), wx.BITMAP_TYPE_XPM)
                self.images_map[name] = il.Add(ctrl._image.GetBitmap().ConvertToImage().Scale(16,16).ConvertToBitmap())             
 
        self.tree.SetImageList(il)
        self.il = il

        # create some columns
        self.tree.AddColumn("Object name")
        self.tree.AddColumn("Class")
        #self.tree.AddColumn("Column 2")
        self.tree.SetMainColumn(0) # the one with the tree in it...
        self.tree.SetColumnWidth(0, 175)

        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)

    def load_object(self, obj):
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("application")
        self.tree.SetItemText(self.root, "App", 1)
        self.tree.SetItemText(self.root, "col 2 root", 2)
        #self.tree.SetItemImage(self.root, fldridx, which = wx.TreeItemIcon_Normal)
        #self.tree.SetItemImage(self.root, fldropenidx, which = wx.TreeItemIcon_Expanded)

        self.build_tree(self.root, obj)
        self.tree.Expand(self.root)


    def build_tree(self, parent, obj):
        child = self.tree.AppendItem(parent, obj.name)
        self.tree.SetItemText(child, obj.__class__.__name__, 1)
        self.tree.SetItemImage(child, self.images_map[obj.__class__.__name__])
        self.tree.SetItemData(child, wx.TreeItemData(obj))
        #self.tree.SetItemImage(child, fldropenidx, which = wx.TreeItemIcon_Expanded)
        for ctrl in obj:
            self.build_tree(child, ctrl)
        self.tree.Expand(child)


    def OnActivate(self, evt):
        child = evt.GetItem()
        print('OnActivate: %s' % self.tree.GetItemText(child))
        f = wx.Frame(self)
        o = self.tree.GetItemData(child).GetData()
        self.propeditor.load_object(o)
        self.propeditor.Parent.SetFocus()
        

    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        if item:
            self.log.write('Flags: %s, Col:%s, Text: %s' %
                           (flags, col, self.tree.GetItemText(item, col)))

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())


#----------------------------------------------------------------------

def runTest(frame, nb, log):
    win = TestPanel(nb, log)
    return win

#----------------------------------------------------------------------



if __name__ == '__main__':
    import sys,os
    app = wx.App()
    
    from gui2py.controls import Button, Label, TextBox, CheckBox, ListBox, ComboBox
    from gui2py.windows import Window

    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False)
               
    o = Button(w, name="btnTest", label="click me!", default=True)
    o = Label(w, name="lblTest", alignment="right", size=(-1, 500), text="hello!")
    o = TextBox(w, name="txtTest", border=False, text="hello world!")
    o = CheckBox(w, name="chkTest", border='none', label="Check me!")
    o = ListBox(w, name="lstTest", border='none', 
                items={'datum1': 'a', 'datum2':'b', 'datum3':'c'},
                multiselect="--multiselect" in sys.argv)
    o = ComboBox(w, name="cboTest",
                items={'datum1': 'a', 'datum2':'b', 'datum3':'c'},
                readonly='--readonly' in sys.argv,
                )
    w.show()

    log = sys.stdout
    f1 = wx.Frame(None)
    f2 = wx.Frame(None)
    propeditor = PropertyEditorPanel(f2, log)
    inspector = InspectorPanel(f1, propeditor, log)
    inspector.load_object(w)
    f1.Show()
    f2.Show()
    
    from gui2py.tools.designer import BasicDesigner
    d = BasicDesigner(w)
    
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()
    
    app.MainLoop()

