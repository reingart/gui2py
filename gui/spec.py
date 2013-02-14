import wx

from .event import FocusEvent, MouseEvent, KeyEvent
from .font import Font
from . import registry

DEBUG = False
DEF_ORDER_COUNTER = 0       # used to init spec in definition order

def new_id(id=None):
    if id is None or id == -1:
        return wx.NewId()
    else:
        return id


class Spec(property):
    "Spec contains meta type information about components"
    
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, group=None,
                 optional=True, default=None, mapping=None, type="", _name=""):
        if fget is None:
            if not mapping:
                fget = lambda obj: getattr(obj, _name)
                fset = lambda obj, value: setattr(obj, _name, value)
            else:
                # enums (mapping) stores value internally and returns its key
                rev_mapping = dict([(v, k) for k, v in mapping.items()])
                fget = lambda obj: rev_mapping[getattr(obj, _name)]
                fset = lambda obj, value: setattr(obj, _name, mapping[value] 
                                                if value in mapping else value)
        property.__init__(self, fget, fset, fdel, doc)
        self.optional = optional
        self.default = default
        self.mapping = mapping
        self.read_only = fset is None
        self.type = type
        self._name = _name              # internal name (usually, wx kwargs one)
        self.__doc__ = doc
        self.group = group              # parent for tree-like struc (propedit)
        global DEF_ORDER_COUNTER
        DEF_ORDER_COUNTER += 1
        self.order = DEF_ORDER_COUNTER
    

class EventSpec(Spec):
    "Generic Event Handler: maps a wx.Event to a gui.Event"
    
    def __init__(self, event_name, binding, kind, doc=None):
        getter = lambda obj: getattr(obj, "_" + event_name)
        def setter(obj, action):
            # check if there is an event binded previously:
            if hasattr(obj, "_" + event_name):
                # disconnect the previous binded events
                for binding in self.bindings:
                    obj.wx_obj.Unbind(binding)
            if action:
                # create the event_handler for this action
                def handler(wx_event):
                    event = self.kind(name=self.name, wx_event=wx_event)
                    if isinstance(action, basestring):
                        # execute the user function with the event as context:
                        exec action in {'event': event, 
                                        'window': event.target.get_parent()}
                    else: 
                        action(event)   # just call the user function
                    # check if default (generic) event handlers are allowed:
                    if not event.cancel_default:
                        wx_event.Skip()
                # connect the new action to the event:
                for binding in self.bindings:
                    obj.wx_obj.Bind(binding, handler)
            # store the event handler
            setattr(obj, "_" + event_name, action)

        Spec.__init__(self, getter, setter, doc=doc, type="code")
        self.name = event_name
        if not isinstance(binding, (list, tuple)):
            binding = (binding, )   # make it an iterable
        self.bindings = binding  # wx.Event object
        self.kind = kind                # Event class
    

class InitSpec(Spec):
    "Spec that is used in wx object instantiation (__init__)"


class DimensionSpec(Spec):
    "Special Spec to manage position and size"


class InternalSpec(Spec):
    "Special Spec to manage designer and other internal handlers"
    # use only for handlers that must automatically rebound on rebuild


class StyleSpec(Spec):
    "Generic style specification to map wx windows styles to properties"

    def __init__(self, wx_style_map, doc=None, default=False):
        # wx_style_map should be a dict ({'left':wx.ALIGN_CENTER})
        if not isinstance(wx_style_map, dict):
            # for boolean styles, convert it to a dict:
            self.wx_style_map = {True: wx_style_map, False: 0}
        else:
            self.wx_style_map = wx_style_map
        if 'True' in self.wx_style_map and not 'False' in self.wx_style_map:
            self.wx_style_map[False] = 0    # sane default
        
        def getter(obj): 
            # reverse search the prop value for the wx_style:
            wx_value = getattr(obj, "_style")
            zero = None     # key when not setted (zero value)
            for key, value in self.wx_style_map.items():
                if wx_value & value:
                    return key
                elif not value:
                    zero = key
            return zero

        def setter(obj, value):
            if value is None:
                raise ValueError("this style spec is mandatory!")
            if value not in self.wx_style_map \
                 and not value in self.wx_style_map.values():
                raise ValueError("%s is not a valid value!" % value)
            # convert the value to the wx style (if not already converted)
            if value in self.wx_style_map:
                if DEBUG: print "new value", value, self.wx_style_map[value]
                value = self.wx_style_map[value]
            # clean posible styles
            if DEBUG: print "current style", obj._style
            for reset_value in self.wx_style_map.values():
                obj._style &= ~ reset_value
            if DEBUG: print "cleaned style", obj._style
            obj._style |= value
            if obj.wx_obj:
                # fset is ignored by now, if object was created throw and error:
                obj.wx_obj.SetWindowStyle(obj._style)          
                if DEBUG: print "changed style!! to ", obj._style
                #raise AttributeError("style is read-only!")
        # select the property editor: 
        if True in self.wx_style_map:
            type_ = 'boolean'
        else:
            type_ = 'enum'
        Spec.__init__(self, getter, setter, doc=doc, default=default, 
                      mapping=self.wx_style_map, type=type_)



