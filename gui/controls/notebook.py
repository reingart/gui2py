#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Notebook control and TabPanel (uses wx.Notebook and wx.Panel)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's Notebook component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)
# Note: Pythoncard's code was trivial, so it was almost reimplemented completely

import wx
from ..event import FormEvent
from ..component import Control, Component, DesignerMixin
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .. import registry
from .. import images


class Notebook(Control):
    "A container which manages multiple windows with associated tabs"
    
    _wx_class = wx.Notebook
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.notebook
    
    def get_count(self):
        "Get the pages (tab) count"
        return self.wx_obj.GetPageCount()
   
    def _get_pages(self):
        return [child for child in self if isinstance(child, TabPanel)]

    pages = InternalSpec(_get_pages,
                         doc="Return a list of current pages")
                  
    selection = Spec(lambda self: self.wx_obj.GetSelection(), 
                     lambda self, index: index is not None and 
                            wx.CallAfter(self.wx_obj.SetSelection, index),
                     doc="Currently selected page (zero based)", type="integer")

    # events:
    onpagechanged = EventSpec('page_changed', 
                         binding=wx.EVT_NOTEBOOK_PAGE_CHANGED, kind=FormEvent)
    onpagechanging = EventSpec('page_changing', 
                         binding=wx.EVT_NOTEBOOK_PAGE_CHANGING, kind=FormEvent)
                            


class TabPanel(Component, DesignerMixin):
    "Represents a tab (page) in the Notebook"

    _wx_class = wx.Panel
    _registry = registry.MISC

    def __init__(self, *args, **kwargs):
        # caption is handled specially:
        if 'text' in kwargs:
            text = kwargs['text']
            del kwargs['text']
        else:
            text = None
        Component.__init__(self, *args, **kwargs)
        # set index TODO: better support for insert/remove/etc
        self.index = self._parent.get_count()
        # sane default for tab caption (in designer)
        text = text or 'tab %s' % self.index
        # add the page to the notebook
        self._parent.wx_obj.AddPage(self.wx_obj, text, self.index)
        # Handle resize events to adjust absolute and relative dimensions
        self.wx_obj.Bind(wx.EVT_SIZE, self.resize)


    index = Spec(optional=False, default="", _name="_index", type='integer')

    def _get_text(self):
        return self._parent.wx_obj.GetPageText(self.index)

    def _set_text(self, new_text):
        if self.index is not None and new_text:
            self._parent.wx_obj.SetPageText(self.index, new_text)
    
    text = Spec(_get_text, _set_text, doc="Tab (page) caption", type='string')
       
    def _get_selection(self):
        return self._parent.wx_obj.GetSelection() == self.index
    
    def _set_selection(self, on):
        if on and self._index:
            wx.CallAfter(self._parent.wx_obj.SetSelection, self.index)

    selected = Spec(_get_selection, _set_selection, type='boolean')

    def destroy(self):
        # remove the page to the notebook
        self._parent.wx_obj.RemovePage(self.index)
        # reindex (maybe this should be moved to Notebook)
        for page in self._parent.pages[self.index+1:]:
            print "reindexing", page.name
            page.index = page.index - 1
        Component.destroy(self)
    
    def resize(self, evt=None):
        "automatically adjust relative pos and size of children controls"
        for child in self:
            if isinstance(child, Control):
                child.resize(evt)
        # call original handler (wx.HtmlWindow)
        if evt:
            evt.Skip()


# update metadata for the add context menu at the designer:

Notebook._meta.valid_children = [TabPanel]
TabPanel._meta.valid_children = [ctr for ctr in registry.CONTROLS.values()
                                 if ctr._image]   # TODO: better filter
 

if __name__ == "__main__":
    import sys
    # basic test until unit_test
    import gui
    app = wx.App(redirect=False)    
    w = gui.Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
    nb = Notebook(w, name="notebook")
    
    p1 = TabPanel(nb, name="tab1", text="panel 1")
    p2 = TabPanel(nb, name="tab2", text="panel 2")
    p3 = TabPanel(nb, name="tab3", text="panel 3")
       
    # assign some event handlers:
    nb.onpagechanged = "print 'selected page:', event.target.selection"
    w.show()
    
    # basic tests:
    assert nb.get_count() == 3
    
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    app.MainLoop()

