
import wx

app = wx.GetApp()
if app is None:
    app = wx.App(False)

import gui

# --- gui2py designer start ---

gui.Window(name='mywin', title=u'hello world', resizable=True, height='769px', 
           left='180', top='24', width='528px', bgcolor=u'#E0E0E0', )
gui.Button(label=u'Quit', name=u'btnClose', height='29', left='232', 
           top='156', width='85', parent='mywin', )
gui.CheckBox(label=u'Check me!', name='chkTest', height='24', left='98', 
             top='99', width='94', parent='mywin', )
gui.Label(name='lblTest', alignment='right', height='25', left='38', top='37', 
          width='48', parent='mywin', text=u'hello!', )
gui.TextBox(name='txtTest', height='25', left='99', top='31', width='152', 
            parent='mywin', )
gui.Button(label=u'click me!', name='btnTest', height='29', left='126', 
           top='157', width='85', default=True, parent='mywin', )
gui.ListBox(name='lstTest', height='96', left='277', top='28', width='103', 
            data_selection=u'two', items=[u'one', u'two', u'tree'], 
            parent='mywin', selection=1, string_selection=u'two', )
gui.MenuBar(name='menubar_83_155', fgcolor=u'#000000', parent='mywin', )
gui.Menu(name='menu_114', fgcolor=u'#000000', parent='mywin.menubar_83_155', )
gui.MenuItem(help=u'MenuItem', id=127, name='menuitem_127', 
             parent='mywin.menubar_83_155.menu_114', )
gui.MenuItemCheckable(help=u'MenuItemCheck', id=120, label=u'MenuItemCheck', 
                      name='menuitemcheckable_120', checked=True, 
                      parent='mywin.menubar_83_155.menu_114', )
gui.MenuItemSeparator(help=u'MenuItem', id=130, name='menuitemseparator_130', 
                      parent='mywin.menubar_83_155.menu_114', )
gui.MenuItem(help=u'MenuItem', id=140, name='menuitem_140', 
             parent='mywin.menubar_83_155.menu_114', )
gui.Gauge(name='gauge_43_128', height='18', left='13', top='130', width='367', 
          parent='mywin', value=50, )
gui.StatusBar(name='statusbar_15_91', parent='mywin', text=u'hello world!', )
gui.ListView(name='listview_23_211', height='99', left='23px', top='211px', 
             width='354', item_count=0, parent='mywin', sort_column=1, )
gui.ListColumn(index=0, name='listcolumn_129', text=u'Col A', 
               parent='listview_23_211', )
gui.ListColumn(index=1, name='listcolumn_140', text=u'Col B', 
               parent='listview_23_211', )
gui.Notebook(name='notebook_121', height='179', left='21', top='330', 
             width='355', parent='mywin', selection=0, )
gui.TabPanel(id=133, name='tabpanel_133', index=0, 
             parent='mywin.notebook_121', selected=True, text=u'tab 0', )
gui.Button(id=197, name='button_197', left='252', top='101', 
           parent='mywin.notebook_121.tabpanel_133', )
gui.Panel(label=u'Radio Box', name='panel_40_46', height='113', left='15', 
          top='13', width='116', parent='mywin.notebook_121.tabpanel_133', )
gui.RadioButton(id=298, label=u'Option 3', name=u'opt3', left='14', top='61', 
                width='86', 
                parent='mywin.notebook_121.tabpanel_133.panel_40_46', )
gui.RadioButton(id=148, label=u'Option 2', name=u'opt2_148', left='14', 
                top='32', width='85', 
                parent='mywin.notebook_121.tabpanel_133.panel_40_46', )
gui.RadioButton(id=274, label=u'Option 1', name=u'opt1', left='14', top='5', 
                width='85', 
                parent='mywin.notebook_121.tabpanel_133.panel_40_46', 
                value=True, )
gui.TabPanel(id=163, name='tabpanel_163', index=1, 
             parent='mywin.notebook_121', selected=False, text=u'tab 1', )
gui.GridView(name='gridview_123_56', height='32px', left='0px', top='0px', 
             width='82px', parent='mywin.notebook_121.tabpanel_163', )
gui.ComboBox(name='cboTest', left='100', top='58', width='152', 
             items=[u'option 1', u'option 2', u'option 3'], parent='mywin', 
             string_selection=u'', )

# --- gui2py designer end ---

mywin = gui.find("mywin")

def my_handler(evt):
    print "loaded!!!"

def my_handler2(evt):
    mywin['txtTest'].text = "hello world!!!!!"


if __name__ == "__main__":
    print "MAIN!"
    mywin.onload = my_handler
    mywin['btnTest'].onclick = my_handler2
    mywin['btnClose'].onclick = "exit()"
    mywin.show()
    
    app.MainLoop()
