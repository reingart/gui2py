from . import GetParam, input
from .input import FormControlMixin

import wx
import wx.combo


class SingleSelectControl(wx.Choice, FormControlMixin):
    def __init__(self, parent, form, tag, parser, optionList, **kwargs):
        FormControlMixin.__init__(self, form, tag)
        self.values = []
        contents = []
        selection = 0
        for idx, option in enumerate(optionList):
            contents.append(parser.GetSource()[option.GetBeginPos():option.GetEndPos1()])
            self.values.append(GetParam(option, 'VALUE', ''))
            if option.HasParam("SELECTED") and not selection:
                selection = idx
        wx.Choice.__init__(self, parent, 
            choices = contents,
        )
        self.SetSelection(selection)
        
    def GetValue(self):
        sel = self.GetSelection()
        value = self.values[sel]
        return value
        
        
