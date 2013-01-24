#!/usr/bin/env python
# coding:utf-8

"Queues(Pipe)-based independent remote client-server Python Debugger"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2011 Mariano Reingart"
__license__ = "LGPL 3.0"
__version__ = "1.03a"

import wx
import wx.html

WIDGETS = {}

class ObjectTagHandler(wx.html.HtmlWinTagHandler):

    # static inner form tag attribute names
    attributes = ["type", "data", "class",
                  "height", "width", "id", ]
    events = [    "onload", "onresize", "onunload",
                  "onfocus", "onblur", "onselect", "onchange",
                  "onkeypress", "onkeydown", "onkeyup",
                  "onclick", "ondblclick", "onmousedown", "onmousemove",
                  "onmouseout", "onmouseover", "onmouseup", "onscroll",
                  ]
    
    def __init__(self):
        wx.html.HtmlWinTagHandler.__init__(self)
    
    def GetSupportedTags(self):
        return "OBJECT"
        
    def HandleTag(self, tag):
        if tag.HasParam("class"):
            _class = tag.GetParam("class").lower()
        else:
            _class = "window"
        self.ctrl = HTMLForm(tag, 
                    self.GetParser().GetWindowInterface().GetHTMLWindow())
        self.cell = self.GetParser().OpenContainer()
        self.ParseInner(tag)
        self.GetParser().CloseContainer()
        self.form = None
        self.optionList = []
        return True
    
    def HandleINPUT(self, tag):
        if tag.HasParam("type"):
            ttype = tag.GetParam("type").upper()
        else:
            ttype = "TEXT"
        klass = self.typeregister[ttype]
        self.createControl(klass, tag)
        return False
        
    def HandleTEXTAREA(self, tag):
        klass = self.typeregister["TEXTAREA"]
        self.createControl(klass, tag)
        #Don't actually call ParseInner, but lie and said we did.
        #This should skip us ahead to the next tag, and let us 
        #retrieve the text verbatem from the text area
        return True
    
    def HandleSELECT(self, tag):
        if tag.HasParam("MULTIPLE"):
            pass
        from .select import SingleSelectControl
        self.optionList = []
        #gather any/all nested options
        self.ParseInner(tag)
        parent = self.GetParser().GetWindowInterface().GetHTMLWindow()
        if 'wxMSW' in wx.PlatformInfo:
            #HAX: wxChoice has some bizarre SetSize semantics that
            #interact poorly with HtmlWidgetCell. Most notably, resizing the control
            #triggers a paint event (in the parent, I guess?) which in turn calls Layout()
            #which calls SetSize again and so on. An extra "layer" between the control
            #and the window keeps the recursion from happening.
            object = wx.Panel(parent)
            select = SingleSelectControl(object, self.form, tag, self.GetParser(), self.optionList)
            sz = wx.BoxSizer()
            sz.Add(select, 1, wx.EXPAND)
            object.SetSizer(sz)
            object.SetSize(select.GetSize())
        else:
            object = SingleSelectControl(parent, self.form, tag, self.GetParser(), self.optionList)

        self.setObjectTag(object, tag)
        cell = self.GetParser().GetContainer()
        cell.InsertCell(
            wx.html.HtmlWidgetCell(object)
        )
        self.optionList = []
        return True
        
    def HandleOPTION(self, tag):
        self.optionList.append(tag)
        return True
        
    def createControl(self, klass, tag):
        parent = self.GetParser().GetWindowInterface().GetHTMLWindow()
        object = klass(parent, self.form, tag, self.GetParser())
        self.setObjectTag(object, tag)
        if not isinstance(object, wx.Window):
            return
        cell = self.GetParser().GetContainer()
        cell.InsertCell(
            wx.html.HtmlWidgetCell(object)
        )

    def setObjectTag(self, object, tag):
        """ Add a tag attribute to the wx window """
        object._attributes = {}
        object._name = tag.GetName().lower()
        for name in self.attributes:
            object._attributes["_%s" % name] = tag.GetParam(name)
            if object._attributes["_%s" % name] == "":
                object._attributes["_%s" % name] = None
