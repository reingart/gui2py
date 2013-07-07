#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py resource (python lists/dicts ui definition) support"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"


import pprint


def load(filename):
    "Load the resource from the source file"
    # use the provided resource file:
    s = open(filename).read()
    ##s.decode("latin1").encode("utf8")
    rsrc = eval(s)
    return rsrc


def save(filename, rsrc):
    "Save the resource to the source file"
    s = pprint.pformat(rsrc)
    ## s = s.encode("utf8")
    open(filename, "w").write(s)


def build(rsrc):
    "Create the GUI objects defined in the resource"
    for win in rsrc:
        build_window(win)        


def build_window(res):
    "Create a gui2py window based on the python resource"
    
    # windows specs (parameters)
    kwargs = dict(res.items())
    wintype = kwargs.pop('type')
    menubar = kwargs.pop('menubar', None)
    components = kwargs.pop('components')
    
    from gui import registry
    import gui
    
    winclass = registry.WINDOWS[wintype]
    win = winclass(**kwargs)

    if components:
        for comp in components:
            build_component(comp, parent=win)

    if menubar:
        mb = gui.MenuBar(name="menubar", parent=win)
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
    
    # Instantiate the GUI object
    print comclass, kwargs
    com = comclass(parent=parent, **kwargs)
    
    for comp in components:
        print "building subcomponent", comp
        build_component(comp, parent=com)


def dump(obj):
    "Recursive convert a live GUI object to a resource list/dict"
    
    from .spec import InitSpec, DimensionSpec, StyleSpec, InternalSpec
    import decimal, datetime
    from .font import Font
    from .graphic import Bitmap, Color

    ret = {'type': obj.__class__.__name__, 'components': []}
    
    params = []
    for (k, spec) in obj._meta.specs.items():
        if k == "index":        # index is really defined by creation order
            continue            # also, avoid infinite recursion
        v = getattr(obj, k, "")
        if (not isinstance(spec, InternalSpec) 
            and v != spec.default
            and (k != 'id' or v > 0) 
            and isinstance(v, 
                 (basestring, int, long, float, bool, dict, list, 
                  decimal.Decimal, 
                  datetime.datetime, datetime.date, datetime.time,
                  Font, Color))                
            and repr(v) != 'None'
            and k != 'parent'
            ):
            ret[k] = v 
            
    for ctl in obj:
        ret['components'].append(dump(ctl))
    
    return ret


class Controller():
    def __init__(self):
        pass
        
    
