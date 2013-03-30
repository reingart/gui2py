#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Controls package"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

# Most controls where forked from PythonCard's components package, altought
# most of they were redesigned and overhauled a lot

# Note: import order is important for toolbox and inspector context menu

from .label import Label
from .button import Button
from .textbox import TextBox
from .checkbox import CheckBox
from .radiobutton import RadioButton
from .listbox import ListBox
from .combobox import ComboBox
from .image import Image
from .line import Line
from .gauge import Gauge
from .slider import Slider
from .listview import ListView, ListColumn
from .treeview import TreeView
from .gridview import GridView, GridColumn
from .htmlbox import HtmlBox

# this should be the last as look for registered controls (valid children)
from .panel import Panel
from .notebook import Notebook, TabPanel


