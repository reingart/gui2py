#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py resource (python lists/dicts ui definition) support"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

# Implementation resembles PythonCard's resource file structure (resource and 
# model modules) but it was simplified even further and rewritten from scratch


import os
import pprint
from . import util


def parse(filename=""):
    "Open, read and eval the resource from the source file"
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


def load(rsrc="", name=None, controller=None):
    "Create the GUI objects defined in the resource (filename or python struct)"
    # if no rsrc is given, search for the rsrc.py with the same module name:
    if not rsrc:
        if controller:
            mod_dict = util.get_class_module_dict(controller)
        else:
            mod_dict = util.get_caller_module_dict()
            # do not use as controller if it was explicitly False or empty
            if controller is None:
                controller = mod_dict
        if util.main_is_frozen():
            # running standalone
            filename = os.path.split(mod_dict['__file__'])[1]
            filename = os.path.join(util.get_app_dir(), filename)
        else:
            # figure out the .rsrc.py filename based on the module name
            filename = mod_dict['__file__']
        # chop the .pyc or .pyo from the end
        base, ext = os.path.splitext(filename)
        rsrc = base + ".rsrc.py"
    # when rsrc is a file name, open, read and eval it:
    if isinstance(rsrc, basestring):
        rsrc = parse(rsrc)
    ret = []
    # search over the resource to create the requested object (or all)
    for win in rsrc:
        if not name or win['name'] == name:
            ret.append(build_window(win))
    # associate event handlers
    if ret and controller:
        connect(ret[0], controller)        
        # return the first instance created (if any):
        return ret[0]
    else:
        # return all the instances created -for the designer- (if any):
        return ret


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
        mb = gui.MenuBar(name="menu", parent=win)
        for menu in menubar:
            build_component(menu, parent=mb)
    return win
        

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
    com = comclass(parent=parent, **kwargs)
    
    for comp in components:
        build_component(comp, parent=com)

    return com
    

def dump(obj):
    "Recursive convert a live GUI object to a resource list/dict"
    
    from .spec import InitSpec, DimensionSpec, StyleSpec, InternalSpec
    import decimal, datetime
    from .font import Font
    from .graphic import Bitmap, Color
    from . import registry

    ret = {'type': obj.__class__.__name__}
    
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
        if ret['type'] in registry.MENU:
            ret.setdefault('items', []).append(dump(ctl))
        else:
            res = dump(ctl)
            if 'menubar' in res:
                ret.setdefault('menubar', []).append(res.pop('menubar'))
            else:
                ret.setdefault('components', []).append(res)
    
    return ret


def connect(component, controller=None):
    "Associate event handlers "
    
    # get the controller functions and names (module or class)
    if not controller or isinstance(controller, dict):
        if not controller:
            controller = util.get_caller_module_dict()
        controller_name = controller['__name__']
        controller_dict = controller
    else:
        controller_name = controller.__class__.__name__
        controller_dict = dict([(k, getattr(controller, k)) for k 
                                in dir(controller) if k.startswith("on_")])

    for fn in [n for n in controller_dict if n.startswith("on_")]:
        # on_mypanel_mybutton_click -> ['mypanel']['mybutton'].onclick 
        names = fn.split("_")
        event_name = names.pop(0) + names.pop(-1)
        # find the control
        obj = component
        for name in names:
            try:
                obj = obj[name]
            except KeyError:
                obj = None
                break
        if not obj:
            from .component import COMPONENTS
            for key, obj in COMPONENTS.items():
                if obj.name == name:
                    print "WARNING: %s should be %s" % (name, key.replace(".", "_"))
                    break
            else:
                raise NameError("'%s' component not found (%s.%s)" % 
                                    (name, controller_name, fn))
        # check if the control supports the event:
        if not hasattr(obj, event_name):
            raise NameError("'%s' event not valid (%s.%s)" % 
                                (event_name, controller_name, fn))
        # bind the event (assign the method to the on... spec)
        setattr(obj, event_name, controller_dict[fn])


class Controller(object):
    "Default controller (loads resource and bind events)"
    
    # mix of PythonCard model.Application & model.Background
    
    def __init__(self, name='', rsrc=None):

        # load the resource:
        if not name:
            self.component = load(rsrc=rsrc, controller=self)
        else:
            self.component = load(rsrc, name, controller=self)
        

