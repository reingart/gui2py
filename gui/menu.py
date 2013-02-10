

import wx
from .event import FormEvent
from .components import Component, Spec, StyleSpec, EventSpec, InitSpec, DimensionSpec
from . import images
from . import registry


DEBUG = False


class wx_DummyWindow:
    "Class to emulate (and normalize) menues in wx whit gui object model"
    # if using custom-draw menues (agw.FlatMenu) this would not be necesary 
    # (so wx_Menu* could be replaced someday..)
    # note that wx ignores dimension and almost all event on menus
    # Font and Background/Textcolour seems to work only on MSW
    
    def __init__(self, parent, *args, **kwargs):
        self._parent = parent
    
    def GetParent(self):
        return self._parent
    
    def GetSize(self):
        return [-1, -1]
    
    GetSizeTuple = GetClientSize = GetSize
    GetPositionTuple = GetSizeTuple
    
    def GetCharWidth(self):
        return 0
    
    def GetCharHeight(self):
        return 0
        
    def Dummy(self, *args, **kwargs):
        pass
    
    Show = SetSize = Refresh = Move = SetToolTip = Dummy
    SetClientSize  = Dummy 	
    IsShown = lambda self: True
    
    def Bind(self, evt, handler, id=None):
        # this should reach top level window:
        if evt == wx.EVT_SIZE:
            pass
        else:
            if DEBUG: print "binding MENU", self.__class__.__name__, id, handler
            self.parent.Bind(evt, handler, id=id or self.GetId())
    
    def Unbind(self, evt, id=None):
        if DEBUG: print "unbinding MENU", self.Text, self.GetId()
        self.parent.Unbind(evt, id=id or self.GetId())


class wx_MenuItem(wx_DummyWindow, wx.MenuItem):
    def __init__(self, parent, *args, **kwargs):
        wx_DummyWindow.__init__(self, parent, *args, **kwargs)
        wx.MenuItem.__init__(self, parentMenu=parent, 
                             id=kwargs['id'], 
                             text=kwargs['label'], 
                             help=kwargs['help'], 
                             kind=kwargs['style'], 
                             #subMenu=None,
                             )
        self.parent = parent
        if self.GetKind() == wx.ITEM_SEPARATOR:
            self.parent.AppendSeparator()       # do not use AppendItem on MSW
        #elif self.GetKind() == wx.ITEM_CHECK:
        #    self.parent.AppendCheckItem(wx.NewId(), self.GetText())            
        else:
            self.parent.AppendItem(self)

    def Enable(self, value):
        # avoid assertion in Enable: invalid menu item
        if not self.GetKind() == wx.ITEM_SEPARATOR:
            wx.MenuItem.Enable(self, value)

    def Destroy(self):
        self.parent.RemoveItem(self)
        wx.MenuItem.Destroy(self)

    def Check(self, value):
        # avoid assertion in Check(): invalid menu item
        if self.GetKind() == wx.ITEM_CHECK:
            wx.MenuItem.Check(self, value)

    GetForegroundColour = wx.MenuItem.GetTextColour
    SetForegroundColour = wx.MenuItem.SetTextColour
            

class MenuItem(Component):
    "A MenuItem represents one selectable item in a Menu"

    _wx_class = wx_MenuItem
    _registry = registry.MENU

    label = InitSpec(lambda self: self.wx_obj.GetText(), 
                     lambda self, label: self.wx_obj.SetText(label),
                     optional=False, default='MenuItem', type="string", 
                     doc="text to show as caption")
    help = InitSpec(lambda self: self.wx_obj.GetText(), 
                 lambda self, label: self.wx_obj.SetText(label),
                 optional=True, default='', type="string", 
                 doc="text to show as help in the status bar?")
    onclick = EventSpec('click', binding=wx.EVT_MENU, kind=FormEvent)

    def rebuild(self, **kwargs):
        # avoid recreating the object (not supported yet!)
        Component.rebuild(self, False, **kwargs)


class MenuItemCheckable(MenuItem):
    "A MenuItem represents one selectable item in a Menu"

    _wx_class = wx_MenuItem
    _registry = registry.MENU
    _style = wx.ITEM_CHECK
    
    checked = Spec(lambda self: self.wx_obj.IsChecked(), 
                   lambda self, value: self.wx_obj.Check(value),
                   default=False, type="boolean")


class MenuItemSeparator(MenuItem):

    _style = wx.ITEM_SEPARATOR


class wx_Menu(wx_DummyWindow, wx.Menu):
    
    def __init__(self, parent, *args, **kwargs):
        wx_DummyWindow.__init__(self, parent, *args, **kwargs)
        # if this is a popup menu, call constructor with:
        #   kwargs.get("label"), kwargs.get("style")
        wx.Menu.__init__(self)
        self.parent = parent
        if isinstance(parent, wx.MenuBar):
            self.parent.Append(self, kwargs.get("label"))
        else:
            self.parent.AppendSubMenu(submenu=self, 
                                   text=kwargs.get("label"))
        id = self.parent.GetLastId()
        self.GetId = lambda: id

    def Destroy(self):
        if isinstance(self.parent, wx.MenuBar):
            self.parent.RemoveItem(self)
        else:
            self.parent.Remove(self.GetId())
        try:
            wx.Menu.Destroy(self)
        except TypeError:
            # we were removed! ignore "got _wxPyDeadObject instance instead"
            pass
            
    # unsupported methods:
    
    GetBackgroundColour = SetBackgroundColour = wx_DummyWindow.Dummy
    SetFont = wx_DummyWindow.Dummy 
    GetFont = lambda self: wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    GetForegroundColour = lambda self: 'black'
    SetForegroundColour = wx_DummyWindow.Dummy

    def Enable(self, value):
        "enable or disable all menu items"
        for i in range(self.GetMenuItemCount()):
            it = self.FindItemByPosition(i) 
            it.Enable(value)
    
    def IsEnabled(self, *args, **kwargs):
        "check if all menu items are enabled"
        for i in range(self.GetMenuItemCount()):
            it = self.FindItemByPosition(i) 
            if not it.IsEnabled():
                return False
        return True

    def SetItemLabel(self, menu, label):
        #return #return menu.GetTitle()
        id = menu.GetId()
        print "MENUID", id
        self.SetLabel(id, label)
        #menu.SetLabel(menu.GetTitle())
        pass

    def GetItemLabel(self, menu):
        #return menu.GetTitle()
        try:
            return self.GetLabel(menu.GetId())
        except:
            import pdb; pdb.set_trace()    

    def GetLastId(self):
        return list(self.GetMenuItems())[-1].GetId()


class Menu(Component):
    "A Menu contains 0..n MenuItem objects."
    
    _wx_class = wx_Menu
    _registry = registry.MENU

    def _set_label(self, value):
        # note that wx.Menu.SetTitle() does not work on gtk for menubars
       #self.wx_obj.SetTitle(value)     # do not use SetTitle (in msw is shown)  
       self.wx_obj.parent.SetItemLabel(self.wx_obj, value)
                
    def _get_label(self):
        # note that wx.Menu.GetTitle() does not work on windows for menubars
        return self.wx_obj.parent.GetItemLabel(self.wx_obj)

    def find(self, item_id=None):
        "Recursively find a menu item by its id (useful for event handlers)"
        for it in self:
            if it.id == item_id:
                return it
            elif isinstance(it, Menu):
                found = it.find(item_id)
                if found:
                    return found 

    def rebuild(self, **kwargs):
        # avoid recreating the object (not supported yet!)
        Component.rebuild(self, False, **kwargs)
    
    label = InitSpec(_get_label,  _set_label,
                     optional=False, default='Menu', type="string", 
                     doc="text to show as caption")         


class wx_MenuBar(wx_DummyWindow, wx.MenuBar):

    def __init__(self, parent, *args, **kwargs):
        # it should receive (self, parent, id, pos, size, style, name)
        # but it doesnt!
        # TypeError: new_MenuBar() takes at most 1 argument (7 given)
        wx_DummyWindow.__init__(self, parent, *args, **kwargs)
        wx.MenuBar.__init__(self)
        self.parent = parent

    # unsupported methods:
    
    GetBackgroundColour = SetBackgroundColour = wx_DummyWindow.Dummy
    SetFont = wx_DummyWindow.Dummy 
    GetFont = lambda self: wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    GetForegroundColour = lambda self: 'black'
    SetForegroundColour = wx_DummyWindow.Dummy

    def Enable(self, value):
        "enable or disable all top menus"
        for i in range(self.GetMenuCount()):
            self.EnableTop(i, value)
    
    def IsEnabled(self, *args, **kwargs):
        "check if all top menus are enabled"
        for i in range(self.GetMenuCount()):
            if not self.IsEnabledTop(i):
                return False
        return True

    def RemoveItem(self, menu):
        "Helper method to remove a menu avoiding using its position"
        menus = self.GetMenus()     # get the list of (menu, title)
        menus = [submenu for submenu in menus if submenu[0] != menu]
        self.SetMenus(menus)
        
    def SetItemLabel(self, menu, label):
        menus = self.GetMenus()     # get the list of (menu, title)
        pos = [submenu[0] for submenu in menus].index(menu)
        self.SetMenuLabel(pos, label)

    def GetItemLabel(self, menu):
        menus = self.GetMenus()     # get the list of (menu, title)
        for submenu, title in menus:
            if submenu == menu:
                return title

    def GetLastId(self):
        return -1 #self.GetMenus()[-1][0].GetId()


class MenuBar(Component):

    _wx_class = wx_MenuBar
    _image = images.menubar
    _registry = registry.CONTROLS
    
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)
        if hasattr(self, "_designer") and self.designer:
            # create a basic menu
            id = wx.NewId()
            m = Menu(self, label='Menu', name="menu_%s" % id, id=id)
            id = wx.NewId()
            mi = MenuItem(m, label='MenuItem', name='menu_item_%s' % id, id=id)
            mi.designer = self.designer

        self._parent.menubar = self

    def find(self, item_id=None):
        "Recursively find a menu item by its id (useful for event handlers)"
        for it in self:
            found = it.find(item_id)
            if found:
                return found 



# update metadata for the add context menu at the designer:

MenuBar._meta.valid_children = [Menu, ] 
Menu._meta.valid_children = [MenuItem, MenuItemCheckable, MenuItemSeparator, Menu] 

# Unit Test

if __name__ == '__main__' :
    import sys, os
    
    # disable ubuntu unity menubar
    os.environ['UBUNTU_MENUPROXY'] = '0'
    
    app = wx.App(redirect=False)
        
    from gui.windows import Window

    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))

    mb = MenuBar(w, name="menubar") 
    m1 = Menu(mb, label='File', name="mnu_file")
    mi11 = MenuItem(m1, label='Open', name='menu_file_open')
    mi12 = MenuItem(m1, label='Save', name='menu_file_save', enabled=False)
    mi13 = MenuItem(m1, label='Quit', name='menu_file_quit')
    m11 = Menu(m1, label='Recent files', name="mnu_recent_file")
    mi111 = MenuItem(m11, label='file1', name='menu_recent_file1')
    mi112 = MenuItem(m11, label='file2', name='menu_recent_file2')
    mi113 = MenuItem(m11, label='file3', name='menu_recent_file3')
    m2 = Menu(mb, label='Edit', name="mnu_edit")
    mi21 = MenuItem(m2, label='Copy', name='menu_edit_copy')
    mi22 = MenuItem(m2, label='Cut', name='menu_edit_cut')
    mi23 = MenuItem(m2, label='Paste', name='menu_edit_paste')

    m2.enabled = False  # disable a whole menu

    def disable_all(event):
        mb.enabled = False  # disable the menubar

    def enable_edit(event):
        m2.enabled = not m2.enabled
        mi11.label = "Close" if m2.enabled else "Open" 
        mi12.enabled = not mi12.enabled

    mi11.onclick = enable_edit
    mi13.onclick = disable_all

    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)

    w.show()
    app.MainLoop()
