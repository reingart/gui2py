
import  wx
import  wx.gizmos   as  gizmos

from gui import registry
from gui.tools.propeditor import PropertyEditorPanel


DEBUG = False
#----------------------------------------------------------------------

class InspectorPanel(wx.Panel):
    def __init__(self, parent, propeditor, log):
        self.log = log
        self.propeditor = propeditor
        self.designer = None
        self.highlighting = None
        self.selected_obj = None   # used by the toolbox as default drop target
        
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
        for name, ctrl in registry.CONTROLS.items() + registry.WINDOWS.items() + registry.MENU.items():
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
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelect)

    def set_designer(self, designer):
        "track designer for context menu"
        self.designer = designer

    def load_object(self, obj=None):
        "Add the object and all their childs"
        # if not obj is given, do a full reload using the current root
        if obj:
            self.root_obj = obj
        else:
            obj = self.root_obj
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("application")
        self.tree.SetItemText(self.root, "App", 1)
        self.tree.SetItemText(self.root, "col 2 root", 2)
        #self.tree.SetItemImage(self.root, fldridx, which = wx.TreeItemIcon_Normal)
        #self.tree.SetItemImage(self.root, fldropenidx, which = wx.TreeItemIcon_Expanded)

        self.build_tree(self.root, obj)
        self.tree.Expand(self.root)

    def inspect(self, obj, context_menu=False, edit_prop=False):
        "Select the object and show its properties"
        child = self.tree.FindItem(self.root, obj.name)
        if DEBUG: print "inspect child", child
        if child:
            self.tree.ScrollTo(child)
            self.tree.SetCurrentItem(child)
            self.tree.SelectItem(child)
            child.Selected = True
            self.activate_item(child, edit_prop)
            if context_menu:
                self.show_context_menu(child)            

    def build_tree(self, parent, obj):
        if DEBUG: print "building", obj.__class__.__name__
        child = self.tree.AppendItem(parent, obj.name)
        self.tree.SetItemText(child, obj.__class__.__name__, 1)
        if obj._meta.name in self.images_map:
            self.tree.SetItemImage(child, self.images_map[obj._meta.name])
        self.tree.SetItemData(child, wx.TreeItemData(obj))
        #self.tree.SetItemImage(child, fldropenidx, which = wx.TreeItemIcon_Expanded)
        for ctrl in obj:
            self.build_tree(child, ctrl)
        self.tree.Expand(child)


    def OnActivate(self, evt):
        child = evt.GetItem()
        print('OnActivate: %s' % self.tree.GetItemText(child))
        self.activate_item(child, select=True)
    
    def activate_item(self, child, edit_prop=False, select=False):
        "load the selected item in the property editor"
        d = self.tree.GetItemData(child)
        if d:
            o = d.GetData()
            self.selected_obj = o
            self.propeditor.load_object(o)
            if edit_prop:
                wx.CallAfter(self.propeditor.edit)
            if select and self.designer:
                self.designer.select(o)
        else:
            self.selected_obj = None
    
    def do_highlight(self, tlw, rect, colour, pen_width=2):
        if not self.highlighting and tlw:
            self.highlighting = tlw
            if not tlw.IsFrozen():
                tlw.Freeze()

            dc = wx.ScreenDC()
            dco = None
                
            dc.SetPen(wx.Pen(colour, pen_width))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)

            drawRect = wx.Rect(*rect)
            dc.DrawRectangleRect(drawRect)

            drawRect.Inflate(2,2)
            pos = tlw.ScreenToClient(drawRect.GetPosition())
            drawRect.SetPosition(pos)
            wx.CallLater(300, self.do_unhighlight, tlw, drawRect)
            return dc, dco
    
    def do_unhighlight(self, tlw, rect):
        if not tlw:
            return
        if tlw.IsFrozen():
            tlw.Thaw()
        tlw.RefreshRect(rect)
        self.highlighting = None

    def highlight(self, win):
        if win and isinstance(win, wx.Window):
            rect = win.GetClientRect()
            tlw = win.GetTopLevelParent()
            pos = win.ClientToScreen((0,0))
            rect.SetPosition(pos)
            self.do_highlight(tlw, rect, 'red')

    def OnSelect(self, evt):
        child = evt.GetItem()
        if DEBUG: print('OnSelect: %s' % self.tree.GetItemText(child))
        d = self.tree.GetItemData(child)
        if d:
            o = d.GetData()
            self.highlight(o.wx_obj if o else None)


    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        self.show_context_menu(item)
    
    def show_context_menu(self, item):
        "Open a popup menu with options regarding the selected object"
        if item:
            d = self.tree.GetItemData(item)
            if d:
                obj = d.GetData()
                if obj:
                    # highligh and store the selected object:
                    self.highlight(obj.wx_obj)
                    self.obj = obj
                    
                    # make the context menu
                    menu = wx.Menu()
                    id_del, id_dup, id_raise, id_lower = [wx.NewId() for i
                                                            in range(4)]
                    menu.Append(id_del, "Delete")
                    menu.Append(id_dup, "Duplicate")
                    menu.Append(id_raise, "Bring to Front")
                    menu.Append(id_lower, "Send to Back")

                    # make submenu!
                    sm = wx.Menu()
                    for ctrl in sorted(obj._meta.valid_children,
                                       key=lambda c: 
                                            registry.ALL.index(c._meta.name)):
                        new_id = wx.NewId()
                        sm.Append(new_id, ctrl._meta.name)
                        self.Bind(wx.EVT_MENU, 
                                  lambda evt, ctrl=ctrl: self.add_child(ctrl), 
                                  id=new_id)
                        
                    menu.AppendMenu(wx.NewId(), "Add child", sm)

                    self.Bind(wx.EVT_MENU, self.delete, id=id_del)
                    self.Bind(wx.EVT_MENU, self.duplicate, id=id_dup)
                    self.Bind(wx.EVT_MENU, self.bring_to_front, id=id_raise)
                    self.Bind(wx.EVT_MENU, self.send_to_back, id=id_lower)

                    self.PopupMenu(menu)
                    menu.Destroy()
                    self.load_object(self.root_obj)     # reload the tree
    
    def delete(self, evt, obj=None):
        # remove the object from parent and destroy it:
        if obj:
            self.obj = obj
        self.obj.destroy()
        del self.obj

    def duplicate(self, evt):
        # create a similar copy of the object
        obj2 = self.obj.duplicate()

    def bring_to_front(self, evt):
        self.obj.z_order(1)

    def send_to_back(self, evt):
        self.obj.z_order(0)
    
    def add_child(self, ctrl):
        new_id = wx.NewId()
        obj = ctrl(self.obj, 
               name="%s_%s" % (ctrl._meta.name.lower(), new_id),
               id=new_id, 
               designer=self.designer)
        # update the object at the inspector (to show the new control)
        wx.CallAfter(self.inspect, obj)
    
    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())


#----------------------------------------------------------------------

class InspectorTool:

    def __init__(self, parent=None, log=None):
        if log is None:
            import sys
            log = sys.stdout

        self.f1 = wx.Frame(parent, pos=(600,0), size=(300, 300))
        self.f2 = wx.Frame(parent, pos=(600,350), size=(300, 300))
        self.propeditor = PropertyEditorPanel(self.f2, log)
        self.inspector = InspectorPanel(self.f1, self.propeditor, log)
    
    def show(self, root_obj, visible=True):
        self.inspector.load_object(root_obj)
        self.f1.Show(visible)
        self.f2.Show(visible)
        
        
#----------------------------------------------------------------------



if __name__ == '__main__':
    import sys,os
    app = wx.App(redirect=None)
    
    from gui.controls import Button, Label, TextBox, CheckBox, ListBox, ComboBox
    from gui.windows import Window

    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
               
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
    
    InspectorTool().show(w)
    
    app.MainLoop()

