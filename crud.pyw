#!/usr/bin/python
# -*- coding: utf-8 -*-

"Experimental CRUD sample gui2py application demo"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2015- Mariano Reingart"
__license__ = "LGPL 3.0"

import datetime
import decimal
import os

# disable ubuntu unified menu
os.environ['UBUNTU_MENUPROXY'] = '0'

import gui

# --- gui2py designer generated code starts ---

with gui.Window(name='mywin', title=u'gui2py CRUD demo', resizable=True, 
                height='585px', left='180', sizer='wrap', top='24', 
                width='327px', bgcolor=u'#E0E0E0', image='', tiled=True, ):
    with gui.Panel(name='panel',  sizer='wrap', width="100%", height="100%"):
        gui.Label(name='label_140_120', sizer_align='center', sizer_border=4, 
                  width='100%', text=u'Sample Record', )
        with gui.Panel(label=u'', name='record', sizer='gridbag', width='100%', 
                       image='', sizer_border=5):
            gui.Label(name='l_id', width='100px', text=u'ID', )
            gui.TextBox(name='id', sizer_col=1, text=u'1234', value=u'1234', )
            gui.Label(name='_name', sizer_row=1, text=u'Name', )
            gui.TextBox(name='name', sizer_col=1, sizer_row=1, 
                        sizer_expand=True, text=u'Mariano', value=u'Mariano', )
            gui.Label(name='_address', sizer_row=2, text=u'Address', )
            gui.TextBox(name='address', sizer_col=1, sizer_row=2, 
                        text=u'Argentina', value=u'Argentina', )
        gui.Button(label=u'Create', name='create', sizer_border=4, )
        gui.Button(label=u'Retrieve', name='retrieve', sizer_border=4, )
        gui.Button(label=u'Update', name='update', sizer_border=4, )
        gui.Button(label=u'Delete', name='delete', sizer_border=4, )
        gui.Button(label=u'Search', name='search', sizer_border=4, )

# --- gui2py designer generated code ends ---


mywin = gui.get("mywin")

mywin['panel']['record'].set_sizer_grow_col(1, 1)

if __name__ == "__main__":
    
    mywin.show()
    
    gui.main_loop()
