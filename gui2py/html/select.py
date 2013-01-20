from . import GetParam, input
from .input import FormControlMixin

from ..controls import ComboBox 


class SingleSelectControl(ComboBox, FormControlMixin):
    def __init__(self, parent, form, tag, parser, option_list, **kwargs):
        kwargs["name"] = GetParam(tag, "NAME", "")
        ComboBox.__init__(self, parent, readonly=True, **kwargs)
        FormControlMixin.__init__(self, form, tag)
        items = []
        selection = 0
        for idx, option in enumerate(option_list):
            text = parser.GetSource()[option.GetBeginPos():option.GetEndPos1()]
            value = GetParam(option, 'VALUE', '')
            items.append((value, text))
            if option.HasParam("SELECTED") and not selection:
                selection = idx
        self.items = items
        self.selection = selection
        self.size = (int(GetParam(tag, "SIZE", default=-1)), -1)
        
    def get_value(self):
        return self.data_selection
        
        
