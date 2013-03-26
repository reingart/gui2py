import datetime
import decimal
import wx

app = wx.GetApp()
if app is None:
    app = wx.App(False)

import gui

# --- gui2py designer generated code starts ---

gui.Window(name='mywin', title=u'hello world', resizable=True, height='601px', 
           left='180', top='24', width='418px', bgcolor=u'#E0E0E0', )
gui.Button(label=u'Quit', name=u'btnClose', left='232', top='156', width='85', 
           parent='mywin', )
gui.CheckBox(label=u'Check me!', name='chkTest', left='98', top='99', 
             width='94', parent='mywin', )
gui.Label(name='lblTest', alignment='right', left='38', top='37', width='48', 
          parent='mywin', text=u'hello!', )
gui.TextBox(name='txtTest', left='100', top='31', width='152', parent='mywin', )
gui.Button(label=u'click me!', name='btnTest', left='126', top='157', 
           width='85', default=True, parent='mywin', )
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
gui.ListView(name='listview', height='99', left='23', top='211', width='192', 
             item_count=0, parent='mywin', sort_column=-1, )
gui.ListColumn(index=0, name='listcolumn_129', text=u'Col A', 
               parent='listview', )
gui.ListColumn(index=1, name='listcolumn_140', text=u'Col B', 
               parent='listview', )
gui.Notebook(name='notebook', height='179', left='21', top='330', width='355', 
             parent='mywin', selection=0, )
gui.TabPanel(id=133, name=u'tab0', index=0, parent='mywin.notebook', 
             selected=True, text=u'Misc.', )
gui.Button(id=197, name='button_197', left='245', top='103', 
           parent=u'mywin.notebook.tab0', )
gui.TextBox(mask=u'##-########-#', name=u'masked', alignment='right', 
            left='220', top='19', width='111', parent=u'mywin.notebook.tab0', 
            value=u'20-26756539-3', )
gui.TextBox(mask='###.##', name=u'numeric', alignment='right', left='230', 
            top='46', width='101', parent=u'mywin.notebook.tab0', value=98.76, )
gui.TextBox(mask='date', name=u'date_picker', left='210', top='73', 
            width='121', parent=u'mywin.notebook.tab0', 
            value=datetime.date(2013, 3, 26), )
gui.Label(name='label_159_27', left='147', top='23', 
          parent=u'mywin.notebook.tab0', text=u'masked:', )
gui.Label(name='label_153_56', left='147', top='50', 
          parent=u'mywin.notebook.tab0', text=u'numeric:', )
gui.Label(name='label_152_84', left='147', top='78', 
          parent=u'mywin.notebook.tab0', text=u'date:', )
gui.Panel(label=u'Group: ', name='panel_40_46', height='130', left='15', 
          top='10', width='116', parent=u'mywin.notebook.tab0', )
gui.RadioButton(id=298, label=u'Option 3', name=u'opt3', left='14', top='71', 
                width='86', parent=u'mywin.notebook.tab0.panel_40_46', )
gui.RadioButton(id=148, label=u'Option 2', name=u'opt2_148', left='14', 
                top='47', width='85', 
                parent=u'mywin.notebook.tab0.panel_40_46', )
gui.RadioButton(id=274, label=u'Option 1', name=u'opt1', left='14', top='23', 
                width='85', parent=u'mywin.notebook.tab0.panel_40_46', 
                value=True, )
gui.CheckBox(name='checkbox_29_80', left='14', top='95', 
             parent=u'mywin.notebook.tab0.panel_40_46', )
gui.TabPanel(id=163, name=u'tab1', index=1, parent='mywin.notebook', 
             selected=False, text=u'Grid', )
gui.GridView(name='gridview', height='100%', left='0', top='0', width='100%', 
             parent=u'mywin.notebook.tab1', )
gui.GridColumn(index=0, name=u'col1', text=u'Col A', type='text', width=75, 
               parent='gridview', )
gui.GridColumn(index=1, name=u'col2', text=u'Col 2', type='datetime', 
               width=75, parent='gridview', )
gui.GridColumn(index=2, name=u'col3', text=u'Col B', type='float', width=75, 
               parent='gridview', )
gui.TabPanel(id=157, name=u'tab2', index=2, parent='mywin.notebook', 
             selected=False, text=u'Html', )
gui.HtmlBox(id=222, name='htmlbox_222', height='100%', left='0', top='0', 
            width='100%', location=u'', parent=u'mywin.notebook.tab2', )
gui.TreeView(name='treeview', height='98', left='223', top='212', width='154', 
             parent='mywin', )
gui.ComboBox(name='cboTest', left='100', top='58', width='152', 
             items=[u'option 1', u'option 2', u'option 3'], parent='mywin', 
             string_selection=u'', )

# --- gui2py designer generated code ends ---

mywin = gui.find("mywin")

def my_handler(evt):
    print "loaded!!!"

def my_handler2(evt):
    print "button clicked!", evt.target.name
    mywin['txtTest'].value = "hello world!!!!!"


if __name__ == "__main__":
    print "MAIN!"
    mywin.onload = my_handler
    mywin['btnTest'].onclick = my_handler2
    mywin['btnClose'].onclick = "exit()"

    # load the list items and bind a event handler
    lv = mywin['listview']
    lv.items = [[str(i), chr(i)*5] for i in range(65, 92)]
    lv.onitemselected = "print 'selection:', event.target.get_selected_items()"

    # load the tree and bind a event handler
    tv = mywin['treeview']
    root = tv.items.add(text="Root")
    child1 = tv.items.add(parent=root, text="Child 1")
    child2 = tv.items.add(parent=root, text="Child 2")
    child3 = tv.items.add(parent=root, text="Child 3")
    child11 = tv.items.add(parent=child1, text="Child 11")
    child11.ensure_visible()
    child2.set_has_children()   # "virtual" tree node
    tv.onitemselected = "print 'selected TreeItem:', event.detail.text"
    
    # load the grid:
    gv = mywin['notebook']['tab1']['gridview']
    gv.items = [[str(i), datetime.datetime.now(), 3.141516] for i in range(100)]
    
    mywin.show()
    
    app.MainLoop()
