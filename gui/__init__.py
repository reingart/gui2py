##import wxversion
##wxversion.select("2.9")

# useful shortcuts:

from .controls import Label, Button, TextBox, CheckBox, ListBox, ComboBox, \
                      HtmlBox, Image, Gauge, ListView, ListColumn, \
                      TreeView, Notebook, TabPanel, Panel, RadioButton, Line, \
                      GridView, GridColumn
from .windows import Window, HtmlWindow
from .menu import MenuBar, Menu, MenuItem, MenuItemCheckable, MenuItemSeparator
from .statusbar import StatusBar

from .component import get
from .dialog import alert, prompt, confirm, select_font, select_color, \
                    open_file, save_file, choose_directory, \
                    single_choice, multiple_choice, find

#from . import tools

