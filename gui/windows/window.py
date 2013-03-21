import wx

from ..component import Component, Control
from ..spec import Spec, InitSpec, EventSpec, StyleSpec, InternalSpec
from ..event import UIEvent
from .. import registry
from .. import images


class Window(Control):
    "A window that contains controls" 
    # in PythonCard model.Background
    _wx_class = wx.Frame
    _style = wx.NO_FULL_REPAINT_ON_RESIZE
    _registry = registry.WINDOWS
    _image = images.frame

    def __init__(self, parent=None, **kwargs):
        "Initialize this instance."
        
        # sane defaults (do not overwrite them if rebuilding):
        if not hasattr(self, "_menubar"):
            self._menubar = None
            self._statusbar = None
        
        # call generic component initialization:
        Control.__init__(self, parent, **kwargs)
        self.app = wx.GetApp()
        
        # AJT 20.11.2001
        # Add icon creation
        #self._setIcon(aBgRsrc)

        # 2001-11-08
        # hack to preserve the statusbar text
        #if self.statusbar is not None and self.menubar is not None:
        #    wx.EVT_MENU_HIGHLIGHT_ALL(self, self.menu_highlight)

        if parent is None:
            self.app.SetTopWindow(self.wx_obj)

        wx.CallAfter(self.wx_obj.InitDialog)
        wx.CallAfter(self.wx_obj.Layout)

    # 2001-11-08
    # hack to keep the statusbar text from being wiped out
    def menu_highlight(self, event):
        self.statusbar.text = self.statusbar.text
    
    def _set_statusbar(self, bar=None):
        self.wx_obj.SetStatusBar(bar and bar.wx_obj or None)
        if self._statusbar is not None and self._statusbar != bar:
            self._statusbar.destroy()
            # the statusbar changes the window size
            # so this will for it back
            #self.SetSize(self.GetSizeTuple())
            self.wx_obj.Fit()
        self._statusbar = bar

    def _set_menubar(self, bar=None):
        self.wx_obj.SetMenuBar(bar and bar.wx_obj or None)
        if self._menubar is not None and self._menubar != bar:
            self._menubar.destroy()
            self.wx_obj.Fit()
        self._menubar = bar            

    def _set_icon(self, icon=None):
        """Set icon based on resource values"""
        if icon is not None:
            try:
                wx_icon = wx.Icon(icon, wx.BITMAP_TYPE_ICO)
                self.wx_obj.SetIcon(wx_icon)
            except:
                pass            

    # # KEA 2002-07-09
    # # make sure wxSTC text, bitmaps, etc. aren't lost
    # # when the app exits
    # def OnDestroy(self, evt):
        # # KEA 2004-04-16
        # # stopLogging prevents the OleFlushClipboard message
        # # from being displayed at the console when the app quits
        # if self == evt.GetEventObject():
            # stopLogging = wx.LogNull()
            # wx.TheClipboard.Flush()
            # del stopLogging
        # evt.Skip()

    # # KEA 2004-04-24
    # # this doesn't appear to be hooked to an event
    # # did the binding get deleted or did we just
    # # never decide whether we wanted to have a separate
    # # event to denote exiting the app versus calling close
    # # on the main background to quit the app?!
    # def OnExit(self, evt):
        # self.close(True)

    # # KEA 2001-07-31
    # # we may want to put this someplace else, but we do need access
    # # to the componenet list
    # def findFocus(self):
        # # the wxPython widget that has focus
        # widgetWX = wx.Window_FindFocus()
        # if widgetWX is None:
            # return None
        # else:
            # for widget in self.component.itervalues():
                # if widgetWX == widget:
                    # return widget
        # # is this even possible? focus in another window maybe?
        # return None

    def show(self, value=True):
        self.wx_obj.Show(value)

    def fit(self):
        "Sizes the window so that it fits around its subwindows"
        self.wx_obj.Fit()
        
    def layout(self):
        "Invokes the layout algorithm for this window"
        self.wx_obj.Layout()
        
    def close(self):
        "Generates a event whose handler usually tries to close the window"
        self.wx_obj.Close()
    
    def rebuild(self, *args, **kwargs):
        # detach the menubar (if any) so it can be auto re-attached later
        self.wx_obj.SetMenuBar(None)
        # statusbar needs special care:
        if self._statusbar:
            self.wx_obj.SetStatusBar(None)
            self._statusbar.set_parent(None)    # just in case
        Control.rebuild(self, *args, **kwargs)
        if self._statusbar:
            self._statusbar.set_parent(self)
        
    
    # non-inherited properties:
    title = InitSpec(lambda self: self.wx_obj.GetTitle(), 
                     lambda self, value: self.wx_obj.SetTitle(value),
                     optional=False, default="", type="string")
    maximized = Spec(lambda self: self.wx_obj.IsMaximized(), 
                     lambda self, value: self.wx_obj.Maximize(value),
                     doc="whether the window is maximized", 
                     default=False, type="boolean") 
    minimized = Spec(lambda self: self.wx_obj.IsIconized(), 
                     lambda self, value: self.wx_obj.Iconize(value), 
                     doc="whether the window is minimized", 
                     default=False,type="boolean") 

    # styles:
    caption = StyleSpec(wx.CAPTION, doc="Puts a caption (title)", default=True)
    minimize_box = StyleSpec(wx.MINIMIZE_BOX, doc="Displays a minimize box", 
                        default=True)
    maximize_box = StyleSpec(wx.MAXIMIZE_BOX, doc="Displays a maximize box",
                        default=True)
    close_box = StyleSpec(wx.CLOSE_BOX, doc="Displays a close box",
                          default=True)
    stay_on_top = StyleSpec(wx.STAY_ON_TOP, doc="Stay on top of all windows")
    system_menu = StyleSpec(wx.SYSTEM_MENU, doc="Displays a system menu",
                            default=True)
    resizable = StyleSpec(wx.RESIZE_BORDER, doc="Allow resize")
    tool_window = StyleSpec(wx.FRAME_TOOL_WINDOW, doc="Small titlebar")
    no_taskbar = StyleSpec(wx.FRAME_NO_TASKBAR, doc="Not appear in the taskbar")
    float_on_parent = StyleSpec(wx.FRAME_FLOAT_ON_PARENT, 
                        doc="Always be on top of its parent (parent=None)")
    shaped = StyleSpec(wx.FRAME_SHAPED, doc="Allow shape change (set_shape)")
    border = Control.border
    # ex_metal wx.FRAME_EX_METAL  # On Mac OS X, frames with this style will be 
                        #shown with a metallic look. This is an extra style.

    menubar = InternalSpec(lambda self: self._menubar,
                   lambda self, value: self._set_menubar(value), default=None,
                   doc="Tells the frame to show the given menu bar")
    statusbar = InternalSpec(lambda self: self._statusbar,
                   lambda self, value: self._set_statusbar(value), default=None,
                   doc="Associates a status bar with the frame.")

    # events:
    onload = EventSpec('load', binding=wx.EVT_INIT_DIALOG, kind=UIEvent)
    onunload = EventSpec('unload', binding=wx.EVT_CLOSE, kind=UIEvent)
    ##wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)


# update metadata for the add context menu at the designer:

Window._meta.valid_children = [ctr for ctr in registry.CONTROLS.values()
                                 if ctr._image]   # TODO: better filter
 

if __name__ == "__main__":
    # basic test until proper unit_test
    from ..controls import Button
    app = wx.App(redirect=False)
    w = Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False)
    b = Button(parent=w, name="btnTest", label="click me!", default=True)
    assert w.get_parent() is None
    assert w.name == "frmTest"
    print "style", w._style
    assert w.title == "hello world"
    from pprint import pprint
    # assign some event handlers:
    w.onload = "print 'load', event.timestamp"
    w.onunload = "print 'unload', event.timestamp; event.prevent_default()"
    w.onblur = w.onfocus = lambda event: pprint(event.name)
    # remove an event handler:
    #w.onfocus = None
    w.show()
    app.MainLoop()
