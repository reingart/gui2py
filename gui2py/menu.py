

import wx
from .event import FormEvent
from .components import Component, Spec, StyleSpec, EventSpec, InitSpec, DimensionSpec
from . import images
from . import registry


class wx_DummyWindow:
    "Class to emulate (and normalize) menues in wx whit gui2py object model"
    # if using custom-draw menues (agw.FlatMenu) this would not be necesary 
    # (so wx_Menu* could be replaced someday..)
    # note that wx ignores dimension and almost all event on menus
    # Font and Background/Textcolour seems to work only on MSW
    
    def __init__(self, parent, *args, **kwargs):
        self._parent = parent
    
    def GetParent(self):
        return self._parent
    
    def GetSize(self):
        return [0, 0]
    
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
    
    def Enable(self, value):
        pass    # should this do something else...?
        # TypeError: Required argument 'enable' (pos 3) not found
        #wx.MenuBar.Enable(self, self.GetId(), enable=value)   
    
    def IsEnabled(self, *args, **kwargs):
        return True    

    def Bind(self, evt, handler, id=None):
        # this should reach top level window:
        if evt == wx.EVT_SIZE:
            print "ignoring resize event!"
            pass
        else:
            print "binding MENU", self.__class__.__name__, id, handler
            self.parent.Bind(evt, handler, id=id or self.GetId())
    
    def Unbind(self, evt, id=None):
        #print "unbinding MENU", self.Text, self.GetId()
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
        self.parent.AppendItem(self)

    def Check(self, value):
        # avoid assertion in Check(): invalid menu item
        if self.GetKind() & wx.ITEM_CHECK:
            wx.MenuItem.Check(self, value)

    GetForegroundColour = wx.MenuItem.GetTextColour
    SetForegroundColour = wx.MenuItem.SetTextColour
            

class MenuItem(Component):
    "A MenuItem represents one selectable item in a Menu"

    _wx_class = wx_MenuItem
    _registry = registry.MENU

    checkable = StyleSpec(wx.ITEM_CHECK, default=False)
    separator = StyleSpec(wx.ITEM_SEPARATOR, default=False)              
    checked = Spec(lambda self: self.checkable and self.wx_obj.IsChecked(), 
                   lambda self, value: self.checkable and self.wx_obj.Check(value),
                   default=False, type="boolean")
    label = InitSpec(lambda self: self.wx_obj.GetText(), 
                     lambda self, label: self.wx_obj.SetText(label),
                     optional=False, default='MenuItem', type="string", 
                     doc="text to show as caption")
    help = InitSpec(lambda self: self.wx_obj.GetText(), 
                 lambda self, label: self.wx_obj.SetText(label),
                 optional=True, default='', type="string", 
                 doc="text to show as help in the status bar?")
    onclick = EventSpec('click', binding=wx.EVT_MENU, kind=FormEvent)


class wx_Menu(wx_DummyWindow, wx.Menu):
    
    def __init__(self, parent, *args, **kwargs):
        wx_DummyWindow.__init__(self, parent, *args, **kwargs)
        # if this is a popup menu, call constructor with:
        #   kwargs.get("label"), kwargs.get("style")
        wx.Menu.__init__(self)
        self.parent = parent
        self.GetId = lambda self=self: kwargs['id']
        if isinstance(parent, wx.MenuBar):
            self.pos = self.parent.GetMenuCount()
            self.parent.Append(self, kwargs.get("label"))
        else:
            self.pos = self.parent.GetMenuItemCount()
            self.parent.AppendSubMenu(submenu=self, 
                                   text=kwargs.get("label"),
                                   help=kwargs.get("label"))

    # unsupported methods:
    
    GetBackgroundColour = SetBackgroundColour = wx_DummyWindow.Dummy
    SetFont = wx_DummyWindow.Dummy 
    GetFont = lambda self: wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    GetForegroundColour = lambda self: 'black'
    SetForegroundColour = wx_DummyWindow.Dummy

        
class Menu(Component):
    "A Menu contains 0..n MenuItem objects."
    
    _wx_class = wx_Menu
    _registry = registry.MENU

    def _set_label(self, value):
        # note that wx.Menu.SetTitle() does not work on gtk for menubars
        pos = self.wx_obj.pos
        self.wx_obj.parent.SetMenuLabel(pos, value)
    
    def _get_label(self):
        # note that wx.Menu.GetTitle() does not work on windows for menubars
        pos = self.wx_obj.pos
        return self.wx_obj.parent.GetMenuLabel(pos)

    label = InitSpec(_get_label,  _set_label,
                     optional=False, default='Menu', type="string", 
                     doc="text to show as caption")
    help = InitSpec(lambda self: self.wx_obj.GetText(), 
                 lambda self, label: self.wx_obj.SetText(label),
                 optional=True, default='', type="string", 
                 doc="text to show as help in the status bar?")               


class wx_MenuBar(wx_DummyWindow, wx.MenuBar):

    def __init__(self, parent, *args, **kwargs):
        # it should receive (self, parent, id, pos, size, style, name)
        # but it doesnt!
        # TypeError: new_MenuBar() takes at most 1 argument (7 given)
        wx_DummyWindow.__init__(self, parent, *args, **kwargs)
        wx.MenuBar.__init__(self)
        self.parent = parent
        self.parent.SetMenuBar(self)    

    # unsupported methods:
    
    GetBackgroundColour = SetBackgroundColour = wx_DummyWindow.Dummy
    SetFont = wx_DummyWindow.Dummy 
    GetFont = lambda self: wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    GetForegroundColour = lambda self: 'black'
    SetForegroundColour = wx_DummyWindow.Dummy


class MenuBar(Component):

    _wx_class = wx_MenuBar
    _image = images.menubar


# Unit Test

if __name__ == '__main__' :
    import sys
    
    app = wx.App(redirect=False)
        
    from gui2py.windows import Window

    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))

    mb = MenuBar(w, name="menubar") 
    m1 = Menu(mb, label='File', name="mnu_file")
    mi11 = MenuItem(m1, label='Open', name='menu_file_open')
    mi12 = MenuItem(m1, label='Save', name='menu_file_save')
    mi13 = MenuItem(m1, label='Quit', name='menu_file_quit')
    m11 = Menu(m1, label='Recent files', name="mnu_recent_file")
    mi111 = MenuItem(m11, label='file1', name='menu_recent_file1')
    mi112 = MenuItem(m11, label='file2', name='menu_recent_file2')
    mi113 = MenuItem(m11, label='file3', name='menu_recent_file3')
    m2 = Menu(mb, label='Edit', name="mnu_edit")
    mi21 = MenuItem(m2, label='Copy', name='menu_edit_copy')
    mi22 = MenuItem(m2, label='Cut', name='menu_edit_cut')
    mi23 = MenuItem(m2, label='Paste', name='menu_edit_paste')

    mi13.onclick = "exit()"

    w.show()
    app.MainLoop()
