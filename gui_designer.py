#!/usr/bin/env python
# coding:utf-8

"Integrated Simple GUI Designer (using gui2py -wx.HTML-)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2011 Mariano Reingart"
__license__ = "GPL 3.0"
 
import os
import sys
import wx
import wx.lib.agw.flatnotebook as fnb
import wx.html
import wx.py

from gui.controls import HtmlBox
import gui.html.object


SAMPLE_GUI_WXHTML = """
hola!
<object module="wx" class="Button" width="50%">
    <param name="label" value="'It works!'">
    <!--- param name="id"    value="ID_OK" -->
</object>

"""

class GUIPanel(wx.Panel):
 
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        bookstyle = fnb.FNB_NODRAG | fnb.FNB_SMART_TABS
        self.book = fnb.FlatNotebook(self, wx.ID_ANY, agwStyle=bookstyle)

        sizer.Add(self.book,1, wx.ALL | wx.EXPAND)

        # Add some pages to the second notebook

        self.text = wx.TextCtrl(self.book, -1, SAMPLE_GUI_WXHTML, style=wx.TE_MULTILINE)
        self.book.AddPage(self.text, "Edition")

        self.html = HtmlBox(self, name="html", design=True)
        self.book.AddPage(self.html.wx_obj,  "Preview")

        self.pycrust = wx.py.crust.Crust(self, intro="")
        self.book.AddPage(self.pycrust,  "Shell")

        sizer.Layout()
        self.SendSizeEvent()
        
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        #self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
        self.html.oncellclick = self.OnClick
    
    def OnClick(self, evt):
        print "click!", evt, 
        det = evt.detail
        print "widget", det
    
    def OnPageChanging(self, event):
        page = event.GetOldSelection()
        if page==0:
            # save current cursor position
            self.sel = self.text.GetSelection()
        if page==1:
            # restore previous selection (really needed?)
            self.text.SetSelection(*self.sel)
        event.Skip()

    def OnPageChanged(self, event):
        page = event.GetSelection()
        if page==0:
            wx.CallAfter(self.text.SetFocus)
        if page==1:
           self.html.set_page(self.text.GetValue())
        event.Skip()


class SimpleGUI(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None)

        self.panel = GUIPanel(self)
        self.Show()
        ##p = self.panel.html.GetParser()
        
        pass
        

if __name__ == '__main__':
    app = wx.App(redirect=False)
    browser = SimpleGUI()
    #browser.panel.Open(url)
    ##import wx.lib.inspection
    ##wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()

       


