#!/usr/bin/python
# -*- coding: utf-8 -*-

"Sample gui2py application"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

# images were taken from Pythoncard's proof and widgets demos
# for more complete examples, see each control module

import datetime     # base imports, used by some controls and event handlers
import decimal
import time

import gui          # import gui2py package (shortcuts)

# --- here goes your event handlers ---

def load(evt):
    
     # load the list items with sample data:
    lv = mywin['listview']
    lv.items = [[str(i), chr(i)*5] for i in range(65, 92)]

    # load the tree with sample data:
    tv = mywin['treeview']
    root = tv.items.add(text="Root")
    child1 = tv.items.add(parent=root, text="Child 1")
    child2 = tv.items.add(parent=root, text="Child 2 virtual!")
    child3 = tv.items.add(parent=root, text="Child 3")
    child11 = tv.items.add(parent=child1, text="Child 11")
    child11.ensure_visible()
    child2.set_has_children()   # "virtual" tree node
    
    # load the grid with sample data:
    gv = mywin['notebook']['tab1']['gridview']
    gv.items = [[chr(i+32)*5, i, 3.141516] for i in range(100)]
    
    # load a sample html page
    htmlbox = mywin['notebook']['tab2']['htmlbox']
    htmlbox.set_page("<b>hello</b> <a href='http://www.wxpython.org/'>wx!</a>")

def button_press(evt):
    gui.alert("button clicked! %s" % evt.target.name, "Alert!!!")
    mywin['txtTest'].value = "hello world!!!!!"

def expand_item(event):
    "tree lazy evaluation example: virtually add children at runtime"
    tv = event.target
    if not event.detail.get_children_count():
        for i in range(5):
            it = tv.items.add(parent=event.detail, text="lazy child %s" % i)
            it.set_has_children()  # allow to lazy expand this child too

def slider_click(evt):
    # move the progress bar according the slider ("scroll bar")
    print("Slider value: %s" % evt.target.value)
    mywin['gauge'].value = mywin['slider'].value

def add_an_item(evt):
    # list item model is similar to a dict, to insert an item do:
    new_key = 'my_key_%s' % time.time()     # generate a unique key
    mywin['listview'].items[new_key] = {'col_a': '00', 'col_b': 'inserted!'}

def del_an_item(evt):
    # list item model is similar to dict, to remove an item do:
    for it in mywin['listview'].get_selected_items():
        del mywin['listview'].items[it.key]

def update_items(evt):
    # list item model is similar to dict (of dicts), to update an item do:
    for it in mywin['listview'].items:
        it['col_a'] = it['col_a'] * 2

def add_a_row(evt):
    # grid model is similar to list, to add a row do:
    gv = mywin['notebook']['tab1']['gridview']
    gv.items.insert(0, [10, 11, time.time()])   # insert a row at first pos (0)

def del_sel_rows(evt):
    gv = mywin['notebook']['tab1']['gridview']
    # get the selection & reverse it to start deleting from the end
    selected_rows = reversed([it.index for it in gv.items if it.selected])
    for row in selected_rows:
        # grid model is similar to list, to remove a row do:
        del gv.items[row]
    
def clear_rows(evt):
    "remove all rows"
    mywin['notebook']['tab1']['gridview'].items.clear()
    print("clearing...")

def update_rows(evt):
    # grid model is similar to list (of lists), to update a row do:
    for it in  mywin['notebook']['tab1']['gridview'].items:
        it[2] = time.time()   # update the third column value of each row
    
def edit_buton_pressed(evt):
    msg = []
    for ctrl_name in 'masked', 'numeric', 'date_picker':
        msg.append(repr(mywin['notebook']['tab0'][ctrl_name].value))
    gui.alert('\n'.join(msg), "Input values:", scrolled=True)

t0 = time.time()    # user for basic timing


# --- gui2py designer generated code starts ---

gui.Window(name='mywin', title='gui2py sample app', resizable=True, 
           height='610px', left='180', top='24', width='396px', 
           bgcolor='#E0E0E0', image='tile.bmp', tiled=True, )
gui.Label(name='lblTest', alignment='right', transparent=True, left='38', 
          top='37', width='48', parent='mywin', text='hello!', )
gui.Button(label='Quit', name='btnClose', left='232', top='156', width='85', 
           parent='mywin', onclick='exit()', )
gui.TextBox(name='txtTest', left='100', top='31', width='152', parent='mywin', 
            value='mariano', )
gui.Button(label='click me!', name='btnTest', left='126', top='157', 
           width='85', default=True, parent='mywin', )
gui.ListBox(name='lstTest', height='96', left='277', top='28', width='103', 
            data_selection='two', items=['one', 'two', 'tree'], 
            parent='mywin', selection=1, string_selection='two', )
gui.MenuBar(name='menubar', fgcolor='#000000', parent='mywin', )
gui.Menu(name='menu_114', fgcolor='#000000', parent='mywin.menubar', )
gui.MenuItem(help='MenuItem', id=127, name='menuitem_127', 
             parent='mywin.menubar.menu_114', )
gui.MenuItemCheckable(help='MenuItemCheck', id=120, label='MenuItemCheck', 
                      name='menuitemcheckable_120', checked=True, 
                      parent='mywin.menubar.menu_114', )
gui.MenuItemSeparator(help='MenuItem', id=130, name='menuitemseparator_130', 
                      parent='mywin.menubar.menu_114', )
gui.MenuItem(help='MenuItem', id=140, name='menuitem_140', 
             parent='mywin.menubar.menu_114', )
gui.Menu(label='List', name='list', parent='mywin.menubar', )
gui.MenuItem(help='Add an item to the list', id=225, label='Add item', 
             name='add', parent='mywin.menubar.list', )
gui.MenuItem(help='Remove the selected items in the list', id=235, 
             label='Remove items', name='del', parent='mywin.menubar.list', )
gui.MenuItem(help='Update a values of an entire column', id=201, 
             label='Update items', name='update', 
             parent='mywin.menubar.list', )
gui.Menu(label='Grid', name='grid', parent='mywin.menubar', )
gui.MenuItem(help='Add a row to the grid', label='Add item', name='add', 
             parent='mywin.menubar.grid', )
gui.MenuItem(help='Remove the selected rows in the grid', 
             label='Remove rows', name='del', parent='mywin.menubar.grid', )
gui.MenuItem(help='Update the rows in the grid', label='Update items', 
             name='update', parent='mywin.menubar.grid', )
gui.MenuItem(help='Remove all the rows in the grid', label='Clear', 
             name='clear', parent='mywin.menubar.grid', )
gui.Gauge(name='gauge', height='18', left='13', top='130', width='367', 
          parent='mywin', value=50, )
gui.StatusBar(name='statusbar', parent='mywin', )
gui.ListView(name='listview', height='99', left='23', top='211', width='192', 
             item_count=27, parent='mywin', sort_column=0, 
             onitemselected="print ('sel %s' % event.target.get_selected_items())", )
gui.ListColumn(name='col_a', text='Col A', parent='listview', )
gui.ListColumn(name='col_b', text='Col B', parent='listview', )
gui.Notebook(name='notebook', height='211', left='21', top='330', width='355', 
             parent='mywin', selection=0, )
gui.TabPanel(id=133, name='tab0', parent='mywin.notebook', selected=True, 
             text='Misc.', )
gui.Button(id=197, label='', name='edit_button', height='17', left='245', 
           top='113', width='55', filename='edit.gif', 
           parent='mywin.notebook.tab0', )
gui.TextBox(mask='##-########-#', name='masked', alignment='right', 
            left='220', top='19', width='111', parent='mywin.notebook.tab0', 
            value='20-26756539-3', )
gui.TextBox(mask='###.##', name='numeric', alignment='right', left='230', 
            top='46', width='101', parent='mywin.notebook.tab0', value=98.76, )
gui.TextBox(mask='date', name='date_picker', left='210', top='73', 
            width='121', parent='mywin.notebook.tab0', 
            value=datetime.date(2013, 3, 26), )
gui.Label(name='label_159_27', left='147', top='23', 
          parent='mywin.notebook.tab0', text='masked:', )
gui.Label(name='label_153_56', left='147', top='50', 
          parent='mywin.notebook.tab0', text='numeric:', )
gui.Label(name='label_152_84', left='147', top='78', 
          parent='mywin.notebook.tab0', text='date:', )
gui.Panel(label='Group: ', name='panel_40_46', height='138', left='15', 
          top='10', width='116', image='', parent='mywin.notebook.tab0', )
gui.RadioButton(id=298, label='Option 3', name='opt3', left='14', top='71', 
                width='86', parent='mywin.notebook.tab0.panel_40_46', )
gui.RadioButton(id=148, label='Option 2', name='opt2_148', left='14', 
                top='47', width='85', 
                parent='mywin.notebook.tab0.panel_40_46', )
gui.RadioButton(id=274, label='Option 1', name='opt1', left='14', top='23', 
                width='85', parent='mywin.notebook.tab0.panel_40_46', 
                value=True, )
gui.CheckBox(label='Check', name='checkbox_29_80', left='14', top='95', 
             parent='mywin.notebook.tab0.panel_40_46', )
gui.Image(name='image', height='24', left='148', top='110', width='24', 
          filename='trash.gif', parent='mywin.notebook.tab0', 
          onmousedown="print('clicked the image')", )
gui.TabPanel(id=163, name='tab1', parent='mywin.notebook', selected=False, 
             text='Grid', visible=True, )
gui.GridView(name='gridview', height='100%', left='0', top='0', width='100%', 
             parent='mywin.notebook.tab1', )
gui.GridColumn(name='col1', text='Col A', type='text', width=75, 
               parent='gridview', )
gui.GridColumn(name='col2', text='Col 2', type='long', width=75, 
               parent='gridview', )
gui.GridColumn(name='col3', text='Col B', type='float', width=75, 
               parent='gridview', )
gui.TabPanel(id=157, name='tab2', parent='mywin.notebook', selected=False, 
             text='Html', visible=True, )
gui.HtmlBox(id=222, name='htmlbox', height='100%', left='0', top='0', 
            width='100%', location='', parent='mywin.notebook.tab2', )
gui.TreeView(name='treeview', default_style=True, has_buttons=True, 
             height='98', left='223', top='212', width='154', parent='mywin', 
             onitemselected="print('selected TreeItem: %s' % event.detail.text)", )
gui.ComboBox(name='cboTest', left='100', top='58', width='152', 
             items=['option 1', 'option 2', 'option 3'], parent='mywin', 
             string_selection='', )
gui.Line(name='line_25_556', height='3', left='25', top='194', width='349', 
         parent='mywin', )
gui.Slider(name='slider', left='18', top='96', width='249', parent='mywin', )

# --- gui2py designer generated code ends ---


t1 = time.time()
print("basic creation timing: t1 - t0: %s" % (t1 - t0))

# get a reference to the Top Level Window (used by designer / events handlers):
mywin = gui.get("mywin")

# assign (bind) some event handlers 
# (move to "__main__" block if you don't want to be executed in design mode):

mywin.onload = load
mywin['btnTest'].onclick = button_press
mywin['slider'].onclick = slider_click
mywin['treeview'].onitemexpanding = expand_item
mywin['menubar']['list']['add'].onclick = add_an_item
mywin['menubar']['list']['del'].onclick = del_an_item
mywin['menubar']['list']['update'].onclick = update_items
mywin['menubar']['grid']['add'].onclick = add_a_row
mywin['menubar']['grid']['del'].onclick = del_sel_rows
mywin['menubar']['grid']['clear'].onclick = clear_rows
mywin['menubar']['grid']['update'].onclick = update_rows
mywin['notebook']['tab0']['edit_button'].onclick = edit_buton_pressed

if __name__ == "__main__":
    mywin.show()
    # update the status bar text with python and wxpython version info:
    import wx, sys, platform
    mywin['statusbar'].text = "wx%s - py%s %s %s %s" % (wx.version(), 
                        platform.python_version(), platform.platform(terse=1),
                        platform.machine(), platform.python_compiler())    
    gui.main_loop()
