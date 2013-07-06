#!/usr/bin/python
# -*- coding: utf-8 -*-

"PythonCard to gui2py resources conversion tool"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

import gui


CTRL_MAP = {
    'Widget': None,
    'Button': gui.Button,
    'CheckBox': gui.CheckBox,
    'Choice': gui.ComboBox,             # DEPRECATED
    'ComboBox': gui.ComboBox,
    'Gauge': gui.Gauge,
    'Image': gui.Image,
    'ImageButton': gui.Button,          # integrated
    'List': gui.ListBox,
    'Slider': gui.Slider,
    'Spinner': gui.TextBox,             # not implemented yet
    'StaticBox': gui.Panel,             # DEPRECATED
    'StaticLine': None,                 # not implemented yet
    'StaticText': gui.Label,
    'TextField': gui.TextBox,
    'TextArea': gui.TextBox,            # set multiline=True
    'PasswordField': gui.TextBox,       # set password=True
    'ToggleButton': None,               # not implemented yet
    'MultiColumnList': gui.ListView,
    'MenuBar': gui.MenuBar,
    'Menu': gui.Menu,
    'MenuItem': gui.MenuItem,
}

WIN_MAP = {
    'Background': gui.Window,
    'Dialog': None,
    }

SPEC_MAP = {
    'Widget':  {
        'id': 'id',
        'enabled': 'enabled',
        'visible': 'visible',
        'foregroundColor': 'fgcolor',
        'backgroundColor': 'bgcolor',
        'helpText' : 'helptext',
        'toolTip' : 'tooltip',
        'font': 'font',
        'position': 'pos',
        'size': 'size',
        'userdata': 'userdata', 
        },
    'BitmapCanvas': {}, # TODO  
    'Button': {
        'label': 'label',
        'default': 'default',
        },
    'CheckBox': {
        'label': 'label',
        'checked': 'value',
        },
    'Choice': {
        'items': 'items',
        'stringSelection': 'stringselection',
        },
    'ComboBox': {
        'text': 'text',
        'items': 'items',
        'stringSelection': 'stringselection',
        },
    'Gauge': {
        'layout': 'layout',
        'max': 'max',
        'value': 'value',
        },
    'Image': {
        'backgroundColor': 'bgcolor', 
        'bitmap': 'bitmap', 
        'file': 'file', 
        'size': 'size',
        },
    'ImageButton': {
        'file': 'file', 
        'border': None, 
        'size': 'size',
        },
    'List': {
        'items': 'items',
        'stringSelection': 'stringselection',
        },
    'Slider': {
        'layout': 'layout',
        'labels': 'labels',
        'ticks': 'ticks',
        'tickFrequency': 'freq',
        'min': 'min',
        'max': 'max',
        'value': 'value',
        'default': 'default',
        },
    'Spinner': {
        'min': 'min',
        'max': 'max',
        'value': 'value',
        },
    'StaticBox': {
        'label': 'label',
        'size': 'size',
        },
    'StaticLine': {
        'layout': 'layout',
        'size': 'size',
        },
    'StaticText': {
        'text': 'text',
        'alignment': 'alignment',
        },
    'TextField': {
        'text' : 'value',
        'editable' : 'editable',
        'alignment' : 'alignment',
        'border' : None,
    },
    'TextArea': {
        'text' : 'value',
        'editable' :  'editable',
        'alignment' : 'alignment',
        'border' :  None,
        'horizontalScrollbar' :  'hscroll',
        'size' :  'size',
        },
    'PasswordField': {
        'text' : 'value',
        'editable' : 'editable',
        'alignment' : 'alignment',
        'border' : None,
        },
    'ToggleButton': {
        'label': 'label',
        'checked': 'value',
        },
    }


def migrate_window(bg):
    "Take a pythoncard background resource and convert to a gui2py window"
    ret = {}
    for k, v in bg.items():
        if k == 'type':
            v = WIN_MAP[v]._meta.name
        elif k == 'menubar':
            menus = v['menus']
            v = [migrate_control(menu) for menu in menus]
        elif k == 'components':
            v = [migrate_control(comp) for comp in v]
        else:
            k = SPEC_MAP['Widget'].get(k, k)
        ret[k] = v
    return ret


def migrate_control(comp):
    "Take a pythoncard background resource and convert to a gui2py window"
    ret = {}
    for k, v in comp.items():
        if k == 'type':
            v = CTRL_MAP[v]._meta.name
        elif k == 'menubar':
            pass
        elif k == 'components':
            v = [migrate_control(comp) for comp in v]
        else:
            k = SPEC_MAP['Widget'].get(k, k)
            if comp['type'] in SPEC_MAP:
                k = SPEC_MAP[comp['type']].get(k, k)
        ret[k] = v
    return ret
    

if __name__ == '__main__':
    
    import sys
    import os
    import pprint
    
    if len(sys.argv) > 1:
        # use the provided resource file:
        s = open(sys.argv[1]).read()
        ##s.decode("latin1").encode("utf8")
        rsrc = eval(s)        
    else:    
        # use a test resource file (see minimal.rsrc.py sample):
        rsrc = {'application': { 
                'type':'Application', 'name':'Minimal', 
                'backgrounds': [ 
                      { 'type':'Background',
                        'name':'bgMin',
                        'title':'Minimal PythonCard Application',
                        'size':( 200, 100 ),
                        'menubar': { 
                            'type':'MenuBar',
                            'menus': [
                                { 'type':'Menu',
                                  'name':'menuFile',
                                  'label':'&File',
                                  'items': [ 
                                    { 'type':'MenuItem', 'name':'menuFileExit',
                                      'label':'E&xit\tAlt+X',
                                      'command':'exit' } ] }
                                    ]       
                                }, 
                        'components': [ 
                            { 'type':'TextField', 'name':'field1',
                              'position':(5, 5), 'size':(150, -1),
                            'text':'Hello PythonCard' },
                        ]
                       } ] } }
    
    # do the conversion:
    
    new_rsrc = []
    app = rsrc['application']
    for bg in app['backgrounds']:
        new_rsrc.append(migrate_window(bg))
    
    if len(sys.argv) > 2:
        # save to the provided file
        s = pprint.pformat(new_rsrc)
        ## s = s.encode("utf8")
        open(sys.argv[2], "w").write(s)
    else:
        # pretty-print the output
        pprint.pprint(new_rsrc)

