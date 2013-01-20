"""
    Implementations of form input controls
"""

from . import GetParam, form
from ..controls import TextBox, Button, CheckBox, Label

import wx
import wx.html

def TypeHandler(type_name):
    """ A metaclass generator. Returns a metaclass which
    will register it's class as the class that handles input type=typeName
    """
    def metaclass(name, bases, dict):
        klass = type(name, bases, dict)
        form.FormTagHandler.register_type(type_name.upper(), klass)
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

class SubmitButton(Button, FormControlMixin):
    __metaclass__ = TypeHandler("SUBMIT")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        label = GetParam(tag, "VALUE", default="Submit Query")
        kwargs["label"] = label
        kwargs["name"] = GetParam(tag, "NAME", label)
        Button.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.size = (int(GetParam(tag, "SIZE", default=-1)), -1)
        self.onclick = self.OnClick
    def get_value(self):
        return None
        

class TextInput(TextBox, FormControlMixin):
    __metaclass__ = TypeHandler("TEXT")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        ##    style |= wx.TE_PROCESS_ENTER
        kwargs["name"] = GetParam(tag, "NAME")
        TextBox.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        ##self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.text = GetParam(tag, "VALUE", '')
        ml = int(GetParam(tag, "MAXLENGTH", 0))
        self.set_max_length(ml)
        if ml and len(self.text) > ml:
            self.text = self.text[:ml]
        size = int(GetParam(tag, "SIZE", 40))
        width = self.get_char_width() * size
        self.size = (width, -1)
        if tag.HasParam("READONLY"):
            self.editable = False
    def get_value(self):
        return self.text
            
class PasswordInput(TextInput):
    __metaclass__ = TypeHandler("PASSWORD")
    def __init__(self, parent, form, tag, parser):
        TextInput.__init__(self, parent, form, tag, parser, password=True)
        
        
class Checkbox(CheckBox, FormControlMixin):
    __metaclass__ = TypeHandler("CHECKBOX")
    
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        kwargs["name"] = GetParam(tag, "NAME", "")
        kwargs["label"] = "" # TODO: fix!
        CheckBox.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.value = GetParam(tag, "VALUE", "1")
        if tag.HasParam("checked"):
            self.checked = True

    def get_value(self):
        if self.checked:
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
    def get_value(self):
        return self.value
    def disable(self):
        self.enabled = False
    def is_enabled(self):
        return self.enabled
        
class TextAreaInput(TextBox, FormControlMixin):
    __metaclass__ = TypeHandler("TEXTAREA")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        kwargs["name"] = GetParam(tag, "NAME", "")
        TextBox.__init__(self, parent, multiline=True, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        if tag.HasEnding():
            src = parser.GetSource()[tag.GetBeginPos():tag.GetEndPos1()]
        else:
            src = ''
        #self.SetFont(wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT))
        self.text = src
        cols = int(GetParam(tag, "COLS", 22))
        width = self.get_char_width() * cols
        rows = int(GetParam(tag, "ROWS", 3))
        height = self.get_char_height() * rows
        size = (width, height)
    def get_value(self):
        return self.text
        
class FieldLabel(Label, FormControlMixin):
    __metaclass__ = TypeHandler("LABEL")
    def __init__(self, parent, form, tag, parser, *args, **kwargs):
        label = GetParam(tag, "VALUE", default="label")
        kwargs["name"] = GetParam(tag, "NAME", str(id(self)))
        Label.__init__(self, parent, *args, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        self.size = (int(GetParam(tag, "SIZE", default=-1)), -1)
        if tag.HasEnding():
            src = parser.GetSource()[tag.GetBeginPos():tag.GetEndPos1()]
        else:
            src = ''
        #TODO: get actual font from HMTL Cell Parser
        #self.SetFont(wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT))
        self.text = src
        #TODO: Bind mouse click with the real control: GetParam("for")
        ##self.Bind(wx.EVT_BUTTON, self.OnClick)
    def get_value(self):
        return None
