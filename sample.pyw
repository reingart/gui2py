
import wx

app = wx.GetApp()
if app is None:
    app = wx.App()

import gui

# --- gui2py designer start ---

mywin = gui.Window(
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='617px', 
            id=-2017, 
            left='180', 
            name='mywin', 
            resizable=True, 
            title=u'hello world', 
            top='24', 
            width='400px')
btnClose = gui.Button(
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='29', 
            id=-2018, 
            label=u'Quit', 
            left='232', 
            name=u'btnClose', 
            parent='mywin', 
            top='156', 
            width='85')
chkTest = gui.CheckBox(
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='24', 
            id=-2019, 
            label=u'Check me!', 
            left='98', 
            name='chkTest', 
            parent='mywin', 
            top='99', 
            width='94')
lblTest = gui.Label(
            alignment='right', 
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='25', 
            id=-2020, 
            left='38', 
            name='lblTest', 
            parent='mywin', 
            text=u'hello!', 
            top='37', 
            width='48')
txtTest = gui.TextBox(
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='25', 
            id=-2021, 
            left='99', 
            name='txtTest', 
            parent='mywin', 
            text=u'greeting', 
            top='31', 
            width='152')
btnTest = gui.Button(
            default=True, 
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='29', 
            id=-2022, 
            label=u'click me!', 
            left='126', 
            name='btnTest', 
            parent='mywin', 
            top='157', 
            width='85')
cboTest = gui.ComboBox(
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='22', 
            id=-2023, 
            items=[], 
            left='100', 
            name='cboTest', 
            parent='mywin', 
            string_selection=u'', 
            top='60', 
            width='80')
lstTest = gui.ListBox(
            data_selection=u'two', 
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='96', 
            id=-2024, 
            items=[u'one', u'two', u'tree'], 
            left='277', 
            name='lstTest', 
            parent='mywin', 
            selection=1, 
            string_selection=u'two', 
            top='28', 
            width='103')
menubar_83_155 = gui.MenuBar(
            fgcolor='black', 
            font={'size': 11, 'face': u'Ubuntu'}, 
            id=-2025, 
            name='menubar_83_155', 
            parent='mywin')
menu_114 = gui.Menu(
            fgcolor='black', 
            font={'size': 11, 'face': u'Ubuntu'}, 
            name='menu_114', 
            parent='menubar_83_155')
menuitem_127 = gui.MenuItem(
            font={'size': 11, 'face': u'Ubuntu'}, 
            help=u'MenuItem', 
            id=127, 
            name='menuitem_127', 
            parent='menu_114')
menuitemcheckable_120 = gui.MenuItemCheckable(
            checked=True, 
            font={'size': 11, 'face': u'Ubuntu'}, 
            help=u'MenuItemCheck', 
            id=120, 
            label=u'MenuItemCheck', 
            name='menuitemcheckable_120', 
            parent='menu_114')
menuitemseparator_130 = gui.MenuItemSeparator(
            font={'size': 11, 'face': u'Ubuntu'}, 
            help=u'MenuItem', 
            id=130, 
            name='menuitemseparator_130', 
            parent='menu_114')
menuitem_140 = gui.MenuItem(
            font={'size': 11, 'face': u'Ubuntu'}, 
            help=u'MenuItem', 
            id=140, 
            name='menuitem_140', 
            parent='menu_114')
gauge_43_128 = gui.Gauge(
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='18', 
            id=-2026, 
            left='13', 
            name='gauge_43_128', 
            parent='mywin', 
            top='130', 
            value=50, 
            width='367')
statusbar_15_91 = gui.StatusBar(
            font={'size': 11, 'face': u'Ubuntu'}, 
            id=-2027, 
            name='statusbar_15_91', 
            parent='mywin', 
            text=u'hello world!')
listview_23_211 = gui.ListView(
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='99', 
            id=-2028, 
            item_count=0, 
            left='23px', 
            name='listview_23_211', 
            parent='mywin', 
            sort_column=1, 
            top='211px', 
            width='354')
columnheader_129 = gui.ColumnHeader(
            index=0, 
            name='columnheader_129', 
            parent='listview_23_211', 
            text=u'Col A')
columnheader_140 = gui.ColumnHeader(
            index=1, 
            name='columnheader_140', 
            parent='listview_23_211', 
            text=u'Col B')
notebook_121 = gui.Notebook(
            font={'size': 11, 'face': u'Ubuntu'}, 
            height='179', 
            id=-2031, 
            left='21', 
            name='notebook_121', 
            parent='mywin', 
            selection=0, 
            top='330', 
            width='355')
tabpanel_133 = gui.TabPanel(
            font={'size': 11, 'face': u'Ubuntu'}, 
            id=133, 
            index=0, 
            name='tabpanel_133', 
            parent='notebook_121', 
            selected=True, 
            text=u'tab 0')
button_197 = gui.Button(
            font={'size': 11, 'face': u'Ubuntu'}, 
            id=197, 
            left='10', 
            name='button_197', 
            parent='tabpanel_133', 
            top='10')
tabpanel_163 = gui.TabPanel(
            font={'size': 11, 'face': u'Ubuntu'}, 
            id=163, 
            index=1, 
            name='tabpanel_163', 
            parent='notebook_121', 
            selected=False, 
            text=u'tab 1')

# --- gui2py designer end ---

def my_handler(evt):
    print "loaded!!!"

def my_handler2(evt):
    txtTest.text = "hello world!!!!!"


if __name__ == "__main__":
    print "MAIN!"
    mywin.onload = my_handler
    btnTest.onclick = my_handler2
    btnClose.onclick = "exit()"
    mywin.show()
    
    app.MainLoop()
