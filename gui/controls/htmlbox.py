#!/usr/bin/env python
# coding:utf-8

"HTML control"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2011 Mariano Reingart"
__license__ = "GPL 3.0"
 
import os
import sys
import wx
import wx.html
##import wx.lib.wxpTag

from ..event import HtmlCellEvent, HtmlLinkEvent, SubmitEvent
from ..components import Control, Spec, EventSpec, StyleSpec
from ..html.form import EVT_FORM_SUBMIT
from ..html.object import HTML_CTRL_CLICK
from .. import images


class HtmlBox(Control):
    "An HTML widget to display simple markup and embeed controls."

    _wx_class = wx.html.HtmlWindow
    _style = wx.html.HW_DEFAULT_STYLE | wx.TAB_TRAVERSAL
    _image = images.html
    
    def __init__(self, parent, design=False, **kwargs):
        self.design = design   # flag to enable designer mode
        # set resizable to False to avoid gui2py auto layout on children
        # (EVT_SIZE it is already handled by wx.HtmlWindow) 
        Control.__init__(self, parent, **kwargs)
        if "gtk2" in wx.PlatformInfo:
            self.wx_obj.SetStandardFonts()
        
    def OnLinkClicked(self, linkinfo):
        print('OnLinkClicked: %s\n' % linkinfo.GetHref())
        super(MyHtmlWindow, self).OnLinkClicked(linkinfo)

    def OnSetTitle(self, title):
        print('OnSetTitle: %s\n' % title)
        super(MyHtmlWindow, self).OnSetTitle(title)

    def OnCellMouseHover(self, cell, x, y):
        print('OnCellMouseHover: %s, (%d %d)\n' % (cell, x, y))
        super(MyHtmlWindow, self).OnCellMouseHover(cell, x, y)
         
    def OnCellClicked(self, cell, x, y, evt):
        print('OnCellClicked: %s, (%d %d)\n' % (cell, x, y))
        if isinstance(cell, wx.html.HtmlWordCell):
            sel = wx.html.HtmlSelection()
            print('     %s\n' % cell.ConvertToText(sel))
        super(MyHtmlWindow, self).OnCellClicked(cell, x, y, evt)

    def _get_location(self) :
        return self.wx_obj.GetOpenedPage()

    def set_page(self, source):
        "Sets HTML page and display it"
        self.wx_obj.SetPage(source)
    
    def load_page(self, location):
        "Loads HTML page from location and then displays it"
        if not location:
            self.wx_obj.SetPage("")
        else:
            self.wx_obj.LoadPage(location)
        #self._delegate.Refresh()
    
    def load_file(self, filename):
        "Loads HTML page from file and displays it."
        self.wx_obj.LoadFile(filename)
        
    def write(self, source):
        "Appends HTML fragment to currently displayed text and refreshes it."
        self.wx_obj.AppendToPage(source)

    # properties:
    location = Spec(_get_location, load_page, doc="URL currently loaded")
    
    # styles:
    no_selection = StyleSpec(wx.html.HW_NO_SELECTION, 
                             doc="Don’t allow the user to select text.")
    scrollbars = StyleSpec({False: wx.html.HW_SCROLLBAR_NEVER,
                            True: wx.html.HW_SCROLLBAR_AUTO},
                            doc="Control how to display scrollbars",)

    # events:
    oncellclick = EventSpec('click', binding=wx.html.EVT_HTML_CELL_CLICKED, 
                        kind=HtmlCellEvent, doc="An cell was clicked")
    oncellhover = EventSpec('hover', binding=wx.html.EVT_HTML_CELL_HOVER, 
                        kind=HtmlCellEvent, doc="The mouse passed over a cell")
    onlinkclick = EventSpec('link', binding=wx.html.EVT_HTML_LINK_CLICKED,
                        kind=HtmlLinkEvent, doc="An hyperlink was clicked")
    onclick = EventSpec('click', binding=HTML_CTRL_CLICK,
                        kind=SubmitEvent, doc="A control was clicked")
    onsubmit = EventSpec('submit', binding=EVT_FORM_SUBMIT,
                        kind=SubmitEvent, doc="A form was submitted")

                            
if __name__ == '__main__':

    def on_click(evt):
        print evt.detail
        print evt.href, evt.target
        evt.prevent_default()       # abort opening the link
    
    def on_cell(evt):
        print evt.point

    app = wx.App(redirect=False)
    f = wx.Frame(None)
    html = HtmlBox(f, name="html", visible=True, width="100px")
    html.set_page("<a href='hola'>hello</a> <b>world!</b>")
    html.onlinkclick = on_click
    html.oncellhover = on_cell
    f.Show()
    app.MainLoop()

       


