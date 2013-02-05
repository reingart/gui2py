

import wx
from .event import FormEvent
from .components import Component, Spec, StyleSpec, EventSpec, InitSpec
from . import images 


class DummyWindow:
    "Class to emulate (and normalize) menues in wx whit gui2py object model"
    # if using custom-draw menues (agw.FlatMenu) this would not be necesary 
    # (so wx_Menu* could be replaced someday..)
    # note that wx ignores dimension and almost all event on menus
    
    def __init__(self, parent, *args, **kwargs):
        self._parent = parent
    
    def GetParent(self):
        return self._parent
    
    def GetSize(self):
        return [0, 0]
    
    GetSizeTuple = GetSize
    GetPositionTuple = GetSizeTuple
    
    def GetCharWidth(self):
        return 0
    
    def GetCharHeight(self):
        return 0
        
    def Dummy(self, *args, **kwargs):
        pass
    
    Show = SetSize = SetBackgroundColour = Refresh = Move = SetToolTip = Dummy
    SetClientSize = SetForegroundColour = Dummy
    
    def Enable(self, value):
        pass    # should this do something else...?
        # TypeError: Required argument 'enable' (pos 3) not found
        #wx.MenuBar.Enable(self, self.GetId(), enable=value)       

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


class wx_MenuItem(DummyWindow, wx.MenuItem):
    def __init__(self, parent, *args, **kwargs):
        DummyWindow.__init__(self, parent, *args, **kwargs)
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

            

class MenuItem(Component):
    "A MenuItem represents one selectable item in a Menu"

    _wx_class = wx_MenuItem

    checkable = StyleSpec(wx.ITEM_CHECK, default=False)
    separator = StyleSpec(wx.ITEM_SEPARATOR, default=False)              
    checked = Spec(lambda self: self.wx_obj.IsChecked(), 
                   lambda self, value: self.wx_obj.Check(value),
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


class wx_Menu(DummyWindow, wx.Menu):
    
    def __init__(self, parent, *args, **kwargs):
        DummyWindow.__init__(self, parent, *args, **kwargs)
        # if this is a popup menu, call constructor with:
        #   kwargs.get("label"), kwargs.get("style")
        wx.Menu.__init__(self)
        self.parent = parent
        self.GetId = lambda self=self: kwargs['id']
        self.parent.Append(self, kwargs.get("label"))

        
        
class Menu(Component):
    "A Menu contains 0..n MenuItem objects."
    
    _wx_class = wx_Menu

    label = InitSpec(lambda self: self.wx_obj.GetTitle(), 
                     lambda self, value: self.wx_obj.SetTitle(value),
                     optional=False, default='Menu', type="string", 
                     doc="text to show as caption")
                     

class wx_MenuBar(DummyWindow, wx.MenuBar):

    def __init__(self, parent, *args, **kwargs):
        # it should receive (self, parent, id, pos, size, style, name)
        # but it doesnt!
        # TypeError: new_MenuBar() takes at most 1 argument (7 given)
        DummyWindow.__init__(self, parent, *args, **kwargs)
        wx.MenuBar.__init__(self)
        self.parent = parent
        self.parent.SetMenuBar(self)
        


class MenuBar(Menu):

    _wx_class = wx_MenuBar


# Unit Test

if __name__ == '__main__' :
    import sys
    
    app = wx.App(redirect=False)
        
    from gui2py.windows import Window

    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))

    mb = MenuBar(w) 
    m1 = Menu(mb, label='File', name="mnu_file")
    mi11 = MenuItem(m1, label='Open', name='menu_file_open')
    mi12 = MenuItem(m1, label='Save', name='menu_file_save')
    mi13 = MenuItem(m1, label='Quit', name='menu_file_quit')
    m2 = Menu(mb, label='Edit', name="mnu_edit")
    mi21 = MenuItem(m2, label='Copy', name='menu_edit_copy')
    mi22 = MenuItem(m2, label='Cut', name='menu_edit_cut')
    mi23 = MenuItem(m2, label='Paste', name='menu_edit_paste')

    mi13.onclick = "exit()"

    w.show()
    app.MainLoop()
