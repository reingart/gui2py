#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py resource (python lists/dicts ui definition) support"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"


def load(filename):
    # use the provided resource file:
    s = open(filename).read()
    ##s.decode("latin1").encode("utf8")
    rsrc = eval(s)
    return rsrc


def build(rsrc):
    for win in rsrc:
        build_window(win)        


def build_window(res):
    "Create a gui2py window based on the python resource"
    
    # windows specs (parameters)
    kwargs = dict(res.items())
    wintype = kwargs.pop('type')
    menubar = kwargs.pop('menubar')
    components = kwargs.pop('components')
    
    from gui import registry
    import gui
    
    winclass = registry.WINDOWS[wintype]
    win = winclass(**kwargs)

    if components:
        for comp in components:
            build_component(comp, parent=win)

    if menubar:
        mb = gui.MenuBar(parent=win)
        for menu in menubar:
            build_component(menu, parent=mb)
        

def build_component(res, parent=None):
    "Create a gui2py control based on the python resource"
    # control specs (parameters)
    kwargs = dict(res.items())
    comtype = kwargs.pop('type')
    if 'components' in res:
        components = kwargs.pop('components')
    elif comtype == 'Menu' and 'items' in res:
        components = kwargs.pop('items')
    else:
        components = []

    from gui import registry

    if comtype in registry.CONTROLS:
        comclass = registry.CONTROLS[comtype]
    elif comtype in registry.MENU:
        comclass = registry.MENU[comtype]
    com = comclass(parent=parent, **kwargs)
    
    for comp in components:
        print "building subcomponent", comp
        build_component(comp, parent=com)
            

class Controller():
    def __init__(self):
        pass
        
    
