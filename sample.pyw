#!/usr/bin/python
# -*- coding: utf-8 -*-

"Sample gui2py application"

from __future__ import with_statement   # for python 2.5 compatibility

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

# images were taken from Pythoncard's proof and widgets demos
# for more complete examples, see each control module

import datetime     # base imports, used by some controls and event handlers
import decimal
import time

import gui          # import gui2py package (shortcuts)

# set default locale to handle correctly numeric format (maskedit):
import wx, locale
#locale.setlocale(locale.LC_ALL, u'es_ES.UTF-8')
loc = wx.Locale(wx.LANGUAGE_DEFAULT, wx.LOCALE_LOAD_DEFAULT)

# --- here go your event handlers ---

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

with gui.Window(name='mywin', title=u'gui2py sample app', resizable=True, 
                height='565px', left='180', top='24', width='396px', 
                bgcolor=u'#E0E0E0', image='tile.bmp', tiled=True, ):
    gui.Label(name='lblTest', alignment='right', transparent=True, left='38', 
              top='37', width='48', text=u'hello!', )
    gui.Button(label=u'Quit', name='btnClose', left='232', top='156', 
               width='85', onclick='exit()', )
    gui.TextBox(name='txtTest', left='100', top='31', width='152', 
                value=u'mariano', )
    gui.Button(label=u'click me!', name='btnTest', left='126', top='157', 
               width='85', default=True, )
    gui.ListBox(name='lstTest', height='96', left='277', top='28', 
                width='103', data_selection='two', 
                items=[u'one', u'two', u'tree'], selection=1, 
                string_selection=u'two', )
    with gui.MenuBar(name='menubar', fgcolor=u'#000000', ):
        with gui.Menu(name='menu_114', fgcolor=u'#000000', ):
            gui.MenuItem(help=u'MenuItem', id=127, name='menuitem_127', )
            gui.MenuItemCheckable(help=u'MenuItemCheck', id=120, 
                                  label=u'MenuItemCheck', 
                                  name='menuitemcheckable_120', checked=True, )
            gui.MenuItemSeparator(id=130, name='menuitemseparator_130', )
            gui.MenuItem(help=u'MenuItem', id=140, name='menuitem_140', )
        with gui.Menu(label=u'List', name='list', ):
            gui.MenuItem(help=u'Add an item to the list', id=225, 
                         label=u'Add item', name='add', )
            gui.MenuItem(help=u'Remove the selected items in the list', 
                         id=235, label=u'Remove items', name='del', )
            gui.MenuItem(help=u'Update a values of an entire column', id=201, 
                         label=u'Update items', name='update', )
        with gui.Menu(label=u'Grid', name='grid', ):
            gui.MenuItem(help=u'Add a row to the grid', label=u'Add item', 
                         name='add', )
            gui.MenuItem(help=u'Remove the selected rows in the grid', 
                         label=u'Remove rows', name='del', )
            gui.MenuItem(help=u'Update the rows in the grid', 
                         label=u'Update items', name='update', )
            gui.MenuItem(help=u'Remove all the rows in the grid', 
                         label=u'Clear', name='clear', )
    gui.Gauge(name='gauge', height='18', left='13', top='130', width='367', 
              value=50, )
    gui.StatusBar(name='statusbar', )
    with gui.ListView(name='listview', height='99', left='23', top='211', 
                      width='192', item_count=27, sort_column=0, 
                      onitemselected="print ('sel %s' % event.target.get_selected_items())", ):
        gui.ListColumn(name='col_a', text='Col A', )
        gui.ListColumn(name='col_b', text='Col B', )
    with gui.Notebook(name='notebook', height='211', left='21', top='330', 
                      width='355', selection=0, ):
        with gui.TabPanel(id=133, name='tab0', selected=True, text=u'Misc.', ):
            gui.Button(id=197, label=u'', name='edit_button', height='17', 
                       left='245', top='113', width='55', filename='edit.gif', )
            gui.TextBox(mask='##-########-#', name='masked', 
                        alignment='right', left='220', top='19', width='111', 
                        value=u'20-26756539-3', )
            gui.TextBox(mask='###.##', name='numeric', alignment='right', 
                        left='230', top='46', width='101', value=98.76, )
            gui.TextBox(mask='date', name='date_picker', left='210', top='73', 
                        width='121', value=datetime.date(2013, 3, 26), )
            gui.Label(name='label_159_27', left='147', top='23', 
                      text=u'masked:', )
            gui.Label(name='label_153_56', left='147', top='50', 
                      text=u'numeric:', )
            gui.Label(name='label_152_84', left='147', top='78', 
                      text=u'date:', )
            with gui.Panel(label=u'Group: ', name='panel_40_46', height='138', 
                           left='15', top='10', width='116', image='', ):
                gui.RadioButton(id=298, label=u'Option 3', name='opt3', 
                                left='14', top='71', width='86', )
                gui.RadioButton(id=148, label=u'Option 2', name='opt2_148', 
                                left='14', top='47', width='85', )
                gui.RadioButton(id=274, label=u'Option 1', name='opt1', 
                                left='14', top='23', width='85', value=True, )
                gui.CheckBox(label=u'Check', name='checkbox_29_80', left='14', 
                             top='95', )
            gui.Image(name='image', height='24', left='148', top='110', 
                      width='24', filename='trash.gif', 
                      onmousedown="print('clicked the image')", )
        with gui.TabPanel(id=163, name='tab1', selected=False, text=u'Grid', ):
            with gui.GridView(name='gridview', height='100%', left='0', 
                              top='0', width='100%', ):
                gui.GridColumn(name='col1', text='Col A', type='text', 
                               width=75, )
                gui.GridColumn(name='col2', text='Col 2', type='long', 
                               width=75, )
                gui.GridColumn(name='col3', text='Col B', type='float', 
                               width=75, )
        with gui.TabPanel(id=157, name='tab2', selected=False, text=u'Html', ):
            gui.HtmlBox(id=222, name='htmlbox', height='100%', left='0', 
                        top='0', width='100%', location=u'', )
    gui.TreeView(name='treeview', default_style=True, has_buttons=True, 
                 height='98', left='223', top='212', width='154', 
                 onitemselected="print('selected TreeItem: %s' % event.detail.text)", )
    gui.ComboBox(name='cboTest', left='100', top='58', width='152', 
                 items=[u'option 1', u'option 2', u'option 3'], 
                 string_selection=u'', )
    gui.Line(name='line_25_556', height='3', left='25', top='194', 
             width='349', )
    gui.Slider(name='slider', left='18', top='96', width='249', freq=0, )

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
    mywin.title = "gui2py %s sample app" % gui.__version__
    # update the status bar text with python and wxpython version info:
    import wx, sys, platform
    mywin['statusbar'].text = "wx%s - py%s %s %s %s" % (wx.version(), 
                        platform.python_version(), platform.platform(terse=1),
                        platform.machine(), platform.python_compiler())    
    gui.main_loop()
