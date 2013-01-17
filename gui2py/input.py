"""
    Implementations of form input controls
"""

from . import GetParam, form

import wx
import wx.html

def TypeHandler(typeName):
    """ A metaclass generator. Returns a metaclass which
    will register it's class as the class that handles input type=typeName
    """
    def metaclass(name, bases, dict):
        klass = type(name, bases, dict)
        form.FormTagHandler.registerType(typeName.upper(), klass)
        return klass
    return metaclass

class FormControlMixin(object):
    """ Mixin provides some stock behaviors for
    form controls:
        Add self to the form fields
        Setting the name attribute to the name parameter in the tag
        Disabled attribute
        OnEnter and OnClick methods for binding by 
        the actual control
    """
    def __init__(self, form, tag):
        if not form:
            return
        self.__form = form
        self.name = GetParam(tag, "NAME", None)
        form.fields.append(self)
        if tag.HasParam("DISABLED"):
            wx.CallAfter(self.Disable)
    def OnEnter(self, evt):
        self.__form.hitSubmitButton()
    def OnClick(self, evt):
        self.__form.submit(self)

class SubmitButton(wx.Button, FormControlMixin):
    __metaclass__ = TypeHandler("SUBMIT")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        label = GetParam(tag, "VALUE", default="Submit Query")
        kwargs["label"] = label
        wx.Button.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.SetSize((int(GetParam(tag, "SIZE", default=-1)), -1))
        self.Bind(wx.EVT_BUTTON, self.OnClick)
    def GetValue(self):
        return None
        

class TextInput(wx.TextCtrl, FormControlMixin):
    __metaclass__ = TypeHandler("TEXT")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        style = kwargs.get("style", 0)
        if tag.HasParam("READONLY"):
                style |= wx.TE_READONLY
        if form:
            style |= wx.TE_PROCESS_ENTER
        kwargs["style"] = style
        wx.TextCtrl.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.SetValue(GetParam(tag, "VALUE", ''))
        ml = int(GetParam(tag, "MAXLENGTH", 0))
        self.SetMaxLength(ml)
        if ml and len(self.GetValue()) > ml:
            self.SetValue(self.GetValue()[:ml])
        size = int(GetParam(tag, "SIZE", 40))
        width = self.GetCharWidth() * size
        self.SetSize((width, -1))
            
            
            
class PasswordInput(TextInput):
    __metaclass__ = TypeHandler("PASSWORD")
    def __init__(self, parent, form, tag, parser):
        TextInput.__init__(self, parent, form, tag, parser, style=wx.TE_PASSWORD)
        
        
class Checkbox(wx.CheckBox, FormControlMixin):
    __metaclass__ = TypeHandler("CHECKBOX")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        wx.CheckBox.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.value = GetParam(tag, "VALUE", "1")
        if tag.HasParam("checked"):
            self.SetValue(True)
    def GetValue(self):
        if self.IsChecked():
            return self.value
        else:
            return None
            
class HiddenControl(wx.EvtHandler, FormControlMixin):
    __metaclass__ = TypeHandler("HIDDEN")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        wx.EvtHandler.__init__(self)
        FormControlMixin.__init__(self, form, tag)
        self.value = GetParam(tag, "VALUE", "")
        self.enabled = True
    def GetValue(self):
        return self.value
    def Disable(self):
        self.enabled = False
    def IsEnabled(self):
        return self.enabled
        
class TextAreaInput(wx.TextCtrl, FormControlMixin):
    __metaclass__ = TypeHandler("TEXTAREA")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        style = wx.TE_MULTILINE
        if tag.HasParam("READONLY"):
            style |= wx.TE_READONLY
        wx.TextCtrl.__init__(self, parent, style=style)
        FormControlMixin.__init__(self, form, tag)
        if tag.HasEnding():
            src = parser.GetSource()[tag.GetBeginPos():tag.GetEndPos1()]
        else:
            src = ''
        self.SetFont(wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT))
        self.SetValue(src)
        cols = int(GetParam(tag, "COLS", 22))
        width = self.GetCharWidth() * cols
        rows = int(GetParam(tag, "ROWS", 3))
        height = self.GetCharHeight() * rows
        self.SetSize((width, height))

        
class Label(wx.StaticText, FormControlMixin):
    __metaclass__ = TypeHandler("LABEL")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        label = GetParam(tag, "VALUE", default="label")
        kwargs["label"] = label
        wx.StaticText.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.SetSize((int(GetParam(tag, "SIZE", default=-1)), -1))
        if tag.HasEnding():
            src = parser.GetSource()[tag.GetBeginPos():tag.GetEndPos1()]
        else:
            src = ''
        #TODO: get actual font from HMTL Cell Parser
        #self.SetFont(wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT))
        self.SetLabel(src)
        #TODO: Bind mouse click with the real control: GetParam("for")
        ##self.Bind(wx.EVT_BUTTON, self.OnClick)
    def GetValue(self):
        return None
