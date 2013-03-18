
import wx

app = wx.GetApp()
if app is None:
    app = wx.App(False)

import gui

# --- gui2py designer start ---

gui.Window(name='mywin', title=u'hello world', resizable=True, height='617px', 
           left='180', top='24', width='400px', 
           font={'size': 11, 'face': u'Ubuntu'}, )
gui.Button(label=u'Quit', name=u'btnClose', height='29', left='232', 
           top='156', width='85', font={'size': 11, 'face': u'Ubuntu'}, 
           parent='mywin', )
gui.CheckBox(label=u'Check me!', name='chkTest', height='24', left='98', 
             top='99', width='94', font={'size': 11, 'face': u'Ubuntu'}, 
             parent='mywin', )
gui.Label(name='lblTest', alignment='right', height='25', left='38', top='37', 
          width='48', font={'size': 11, 'face': u'Ubuntu'}, parent='mywin', 
          text=u'hello!', )
gui.TextBox(name='txtTest', height='25', left='99', top='31', width='152', 
            font={'size': 11, 'face': u'Ubuntu'}, parent='mywin', 
            text=u'greeting', )
gui.Button(label=u'click me!', name='btnTest', height='29', left='126', 
           top='157', width='85', default=True, 
           font={'size': 11, 'face': u'Ubuntu'}, parent='mywin', )
gui.ComboBox(name='cboTest', height='22', left='100', top='60', width='80', 
             font={'size': 11, 'face': u'Ubuntu'}, items=[], parent='mywin', 
             string_selection=u'', )
gui.ListBox(name='lstTest', height='96', left='277', top='28', width='103', 
            data_selection=u'two', font={'size': 11, 'face': u'Ubuntu'}, 
            items=[u'one', u'two', u'tree'], parent='mywin', selection=1, 
            string_selection=u'two', )
gui.MenuBar(name='menubar_83_155', fgcolor='black', 
            font={'size': 11, 'face': u'Ubuntu'}, parent='mywin', )
gui.Menu(name='menu_114', fgcolor='black', 
         font={'size': 11, 'face': u'Ubuntu'}, parent='mywin.menubar_83_155', )
gui.MenuItem(help=u'MenuItem', id=127, name='menuitem_127', 
             font={'size': 11, 'face': u'Ubuntu'}, 
             parent='mywin.menubar_83_155.menu_114', )
gui.MenuItemCheckable(help=u'MenuItemCheck', id=120, label=u'MenuItemCheck', 
                      name='menuitemcheckable_120', checked=True, 
                      font={'size': 11, 'face': u'Ubuntu'}, 
                      parent='mywin.menubar_83_155.menu_114', )
gui.MenuItemSeparator(help=u'MenuItem', id=130, name='menuitemseparator_130', 
                      font={'size': 11, 'face': u'Ubuntu'}, 
                      parent='mywin.menubar_83_155.menu_114', )
gui.MenuItem(help=u'MenuItem', id=140, name='menuitem_140', 
             font={'size': 11, 'face': u'Ubuntu'}, 
             parent='mywin.menubar_83_155.menu_114', )
gui.Gauge(name='gauge_43_128', height='18', left='13', top='130', width='367', 
          font={'size': 11, 'face': u'Ubuntu'}, parent='mywin', value=50, )
gui.StatusBar(name='statusbar_15_91', font={'size': 11, 'face': u'Ubuntu'}, 
              parent='mywin', text=u'hello world!', )
gui.ListView(name='listview_23_211', height='99', left='23px', top='211px', 
             width='354', font={'size': 11, 'face': u'Ubuntu'}, item_count=0, 
             parent='mywin', sort_column=1, )
gui.ListColumn(index=0, name='listcolumn_129', text=u'Col A', 
               parent='listview_23_211', )
gui.ListColumn(index=1, name='listcolumn_140', text=u'Col B', 
               parent='listview_23_211', )
gui.Notebook(name='notebook_121', height='179', left='21', top='330', 
             width='355', font={'size': 11, 'face': u'Ubuntu'}, 
             parent='mywin', selection=0, )
gui.TabPanel(id=133, name='tabpanel_133', 
             font={'size': 11, 'face': u'Ubuntu'}, index=0, 
             parent='mywin.notebook_121', selected=True, text=u'tab 0', )
gui.Button(id=197, name='button_197', left='8', top='13', 
           font={'size': 11, 'face': u'Ubuntu'}, 
           parent='mywin.notebook_121.tabpanel_133', )
gui.TabPanel(id=163, name='tabpanel_163', 
             font={'size': 11, 'face': u'Ubuntu'}, index=1, 
             parent='mywin.notebook_121', selected=False, text=u'tab 1', )
gui.GridView(name='gridview_123_56', height='32px', left='0px', top='0px', 
             width='82px', font={'size': 11, 'face': u'Ubuntu'}, 
             parent='mywin.notebook_121.tabpanel_163', )

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
