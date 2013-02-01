"""
    Implementations of form input controls
"""

from . import GetParam, form
from .input import FormControlMixin
from ..controls import Label

import wx
import wx.html

        
class FormLabel(Label, FormControlMixin):
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
