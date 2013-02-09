import wx

from .event import FocusEvent, MouseEvent, KeyEvent
from .font import Font
from . import registry

DEBUG = False

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
            fget = lambda obj: getattr(obj, _name)
            fset = lambda obj, value: setattr(obj, _name, value)
        property.__init__(self, fget, fset, fdel, doc)
        self.optional = optional
        self.default = default
        self.mapping = mapping
        self.read_only = fset is None
        self.type = type
        self._name = _name              # internal name (usually, wx kwargs one)
        self.__doc__ = doc
        self.group = group              # parent for tree-like struc (propedit)
    

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


class ComponentMeta():
    "Component Metadata"
    def __init__(self, name, specs):
        self.name = name
        self.specs = specs

    
class ComponentBase(type):
    "Component class constructor (creates metadata and register the component)"
    def __new__(cls, name, bases, attrs):
        super_new = super(ComponentBase, cls).__new__
    
        # Create the class.
        new_class = super_new(cls, name, bases, attrs)
        
        specs = {}
        # get specs of the base classes
        for base in bases:
            if hasattr(base, "_meta"):
                specs.update(base._meta.specs)
        # get all the specs
        specs.update(dict([(attr_name, attr_value) 
                        for attr_name, attr_value in attrs.items() 
                        if isinstance(attr_value, Spec)]))
        # insert a _meta attribute with the specs
        new_class._meta = ComponentMeta(name, specs)

        # registry and return the new class:
        if hasattr(new_class, "_registry"):
            new_class._registry[name] = new_class
        return new_class

  
class Component(object):
    "The base class for all of our GUI elements"
    
    # Each Component must bind itself to the wxPython event model.  
    # When it receives an event from wxPython, it will convert the event
    # to a gui.event.Event ( UIEvent, MouseEvent, etc ) and call the handler
    
    # This is the base class wich all GUI Elements should derive 
    # (TopLevelWindows -Frame, Dialog, etc.- and Controls)
    # This object maps to wx.Window, but avoid that name as it can be confusing.
    
    __metaclass__ = ComponentBase
    _wx_class = wx.Window       # wx object constructor
    _style = 0                  # base style
    _image = None               # default icon for toolbox
    
    def __init__(self, parent=None, **kwargs):
        self._font = None
        self._children = {}    # container to hold children
    
        # create the wxpython kw arguments (based on specs and defaults)
        wx_kwargs = dict(id=new_id(kwargs.get('id')))
        
        # check if we are recreating the object (i.e., to apply a new style)
        rebuild = hasattr(self, "wx_obj")
        
        # get current spec values (if we are re-creating the wx object)
        if rebuild:
            for spec_name, spec in self._meta.specs.items():
                if spec_name in kwargs:
                    continue    # use provided new value
                if not isinstance(spec, (StyleSpec, InitSpec)):
                    # get the current value and store it in kwargs
                    kwargs[spec_name]  = getattr(self, spec_name)
            self.wx_obj.Visible = False
            self.wx_obj.obj = None
            self.wx_obj.Destroy()
            del self.wx_obj
            if DEBUG: print "kwargs", kwargs
            if isinstance(self._parent, Component):
                del self._parent[self._name]    # remove old child reference
        else:
            self._parent = parent       # store parent
        if isinstance(self._parent, Component) and 'name' in kwargs:
            self._parent[kwargs['name']] = self     # add child reference
        
        self.wx_obj = None      # set up a void wx object (needed by setters)
        
        for spec_name, spec in self._meta.specs.items():
            value = kwargs.get(spec_name, spec.default)
            # no not apply a spec if we are re-creating the wx object:
            if rebuild and spec_name not in kwargs:
                continue    # use previously _style
            if isinstance(spec, InitSpec):
                if DEBUG: print "INIT: setting ", spec_name, value
                if not spec.optional and value is None:
                    raise ValueError("%s: %s is not optional" % 
                                        (self._meta.name, spec_name))
                if spec._name:
                    name = spec._name[1:]   # use the internal name
                    setattr(self, spec._name, value)
                else:
                    name = spec_name        # use the spec attribute name
                wx_kwargs[name] = value
                if spec_name in kwargs:
                    del kwargs[spec_name]
            if isinstance(spec, StyleSpec):
                if DEBUG: print "setting", spec_name, value, spec
                setattr(self, spec_name, value)
                if spec_name in kwargs:
                    del kwargs[spec_name]
        self._wx_kwargs = wx_kwargs
        
        # create the actual wxpython object
        self._wx_kwargs['style'] = style=self._style
        if DEBUG: print "WX KWARGS: ", self._wx_kwargs
        if DEBUG: print "creating", self._wx_class
        if self._parent is None or isinstance(self._parent, wx.Object):
            wx_parent = self._parent
        else:
            wx_parent = self._parent.wx_obj
        self.wx_obj = self._wx_class(wx_parent, **self._wx_kwargs)
        # load specs from kwargs, use default if available
        for spec_name, spec in self._meta.specs.items():
            if spec.read_only or isinstance(spec, (StyleSpec, InitSpec)):
                continue
            # get the spec value for kwargs, if it is optional, get the default
            value = kwargs.get(spec_name)
            if not value and not spec.optional:
                raise ValueError("%s: %s is not optional" % (self._meta.name,
                                                             spec_name))
            elif value is None:
                value = spec.default
            if DEBUG: print "setting", spec_name, value
            setattr(self, spec_name, value)
                
        # store gui reference inside of wx object
        self.wx_obj.obj = self

    def _set_style(self, **kwargs):
        for spec_name, spec in self._meta.specs.items():
            if isinstance(spec, StyleSpec):
                setattr(self, spec_name, value)

    # Container methods:

    def __iter__(self):
        return self._children.itervalues()
    
    def __setitem__(self, key, val):
        self._children[key] = val
        
    def __getitem__(self, key):
        return self._children[key]
    
    def __delitem__(self, key):
        del self._children[key]
        
    # Public methods:
    
    def redraw(self):
        "Force an immediate redraw without waiting for an event handler to finish."
        self.wx_obj.Refresh()
        self.wx_obj.Update()

    def set_focus(self):
        self.wx_obj.SetFocus()
    
    def get_parent(self):
        return self.wx_obj.GetParent()

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ', '.join(["%s=%s" % 
                (k, repr(v)) for (k,v) in self.__dict__.items()]))

    # properties:
    
    def _getId(self):
        "return the id is generated using NewId by the base wxPython control"
        return self.wx_obj.GetId()

    def _setId(self, id):
        pass
        #raise AttributeError("id attribute is read-only")
    
    def _getToolTip(self):
        try:
            return self.wx_obj.GetToolTip().GetTip()
        except:
            return ""
    
    def _get_font(self):
        if self._font is None:
            self._font = Font(parent=self)
        self._font.set_wx_font(self.wx_obj.GetFont())
        return self._font

    def _setForegroundColor( self, color ) :
        color = self._getDefaultColor( color )
        self.wx_obj.SetForegroundColour( color )
        self.wx_obj.Refresh()   # KEA wxPython bug?
    
    def _setBackgroundColor( self, color ) :
        color = self._getDefaultColor( color )
        self.wx_obj.SetBackgroundColour( color )
        self.wx_obj.Refresh()   # KEA wxPython bug?
        
    def _setToolTip(self, aString):
        toolTip = wx.ToolTip(aString)
        self.wx_obj.SetToolTip(toolTip)
    
    def _set_font(self, value):
        if value is None:
            self._font = None
            return
        if isinstance(value, dict):
            self._font = Font(parent=self, **value)
        else: # Bind the font to this component.
            self._font = value
            value._parent = self
        self.wx_obj.SetFont( self._font.get_wx_font() )

    def _getUserdata(self):
        return self._userdata 

    def _setUserdata(self, aString):
        self._userdata = aString

    def _getDefaultColor( self, color ) :
        if color is None :
            return wx.NullColour
        else :
            # KEA 2001-07-27
            # is the right place for this check?
            if isinstance(color, tuple) and len(color) == 3:
                return wx.Colour(color[0], color[1], color[2])
            else:
                return color

    # Dimensions:
    
    def _get_pos(self):
        # get the actual position, not (-1, -1)
        return self.wx_obj.GetPositionTuple()  

    def _set_pos(self, point):
        if point[0] is None:
            point[0] = self.wx_obj.GetPositionTuple()[0]
        if point[1] is None:
            point[1] = self.wx_obj.GetPositionTuple()[1]
        if not isinstance(point[0], int):
            point[0] = point[0] is not None and int(point[0]) or -1
        if not isinstance(point[1], int):
            point[1] = point[1] is not None and int(point[1]) or -1
        self.wx_obj.Move(point)

    def _get_size(self):
        # return the actual size, not (-1, -1)
        return self.wx_obj.GetSizeTuple()

    def _set_size(self, size):
        if size[0] is None:
            size[0] = self.wx_obj.GetSizeTuple()[0]
        if size[1] is None:
            size[1] = self.wx_obj.GetSizeTuple()[1]
        if not isinstance(size[0], int):
            size[0] = size[0] is not None and int(size[0]) or -1
        if not isinstance(size[1], int):
            size[1] = size[1] is not None and int(size[1]) or -1
        self.wx_obj.SetSize(size)

    def _getEnabled(self):
        return self.wx_obj.IsEnabled()

    def _setEnabled(self, aBoolean):
        self.wx_obj.Enable(aBoolean)

    def _getVisible(self):
        return self.wx_obj.IsShown()

    def _setVisible(self, aBoolean):
        self.wx_obj.Show(aBoolean)

    def _getForegroundColor(self):
        return self.wx_obj.GetForegroundColour()

    def _getBackgroundColor(self):
        return self.wx_obj.GetBackgroundColour()
    
    def get_char_width(self):
        "Returns the average character width for this window."
        return self.wx_obj.GetCharWidth()
    
    def get_char_height(self):
        "Returns the character height for this window."
        return self.wx_obj.GetCharHeight()

    name = InitSpec(optional=False, default="", _name="_name", type='string')
    bgcolor = Spec(_getBackgroundColor, _setBackgroundColor, type='colour')
    font = Spec(_get_font, _set_font, type='font')
    fgcolor = Spec(_getForegroundColor, _setForegroundColor, type='colour')
    enabled = Spec(_getEnabled, _setEnabled, default=True, type='boolean')
    id = InitSpec(_getId, _setId,  default=-1, type="integer")
    pos = InitSpec(_get_pos, _set_pos, default=[ -1, -1])
    size = InitSpec(_get_size, _set_size, default=[ -1, -1])
    client_size = Spec(lambda self: self.wx_obj.GetClientSize(),
                       lambda self, value: self.wx_obj.SetClientSize(value))
    helptext = Spec(optional=True, type="string"),
    tooltip = Spec(_getToolTip, _setToolTip, default='', type="string")
    visible = Spec(_getVisible, _setVisible, default=True, type='boolean')
    userdata = Spec(_name='_userdata')
    width = DimensionSpec(lambda self: str(self._get_size()[0]), 
                          lambda self, value: self._set_size([value, None]),
                          type="string", group="size")
    height = DimensionSpec(lambda self: str(self._get_size()[1]), 
                           lambda self, value: self._set_size([None, value]),
                           type="string", group="size")
    left = DimensionSpec(lambda self: str(self._get_pos()[0]), 
                           lambda self, value: self._set_pos([value, None]),
                           type="string", group="position")
    top = DimensionSpec(lambda self: str(self._get_pos()[1]), 
                           lambda self, value: self._set_pos([None, value]),
                           type="string", group="position")
                    
    # Events:
    onfocus = EventSpec('focus', binding=wx.EVT_SET_FOCUS, kind=FocusEvent)
    onblur = EventSpec('blur', binding=wx.EVT_KILL_FOCUS, kind=FocusEvent)
    onmousemove = EventSpec('mousemove', binding=wx.EVT_MOTION, kind=MouseEvent) 
    onmouseover = EventSpec('mouseover', binding=wx.EVT_ENTER_WINDOW, kind=MouseEvent) 
    onmouseout = EventSpec('mouseout', binding=wx.EVT_LEAVE_WINDOW, kind=MouseEvent) 
    onmousewheel = EventSpec('mousewheel', binding=wx.EVT_MOUSEWHEEL, kind=MouseEvent) 
    onmousedown = EventSpec('mousedown', binding=(wx.EVT_LEFT_DOWN, 
                                                  wx.EVT_MIDDLE_DOWN, 
                                                  wx.EVT_RIGHT_DOWN), 
                                        kind=MouseEvent)
    onmouseup = EventSpec('mousedclick', binding=(wx.EVT_LEFT_DCLICK, 
                                                  wx.EVT_MIDDLE_DCLICK,
                                                  wx.EVT_RIGHT_DCLICK),
                                         kind=MouseEvent)
    onmouseup = EventSpec('mouseup', binding=(wx.EVT_LEFT_UP,
                                              wx.EVT_MIDDLE_UP,
                                              wx.EVT_RIGHT_UP), 
                                     kind=MouseEvent)
    onkeypress = EventSpec('keypress', binding=wx.EVT_CHAR, kind=KeyEvent)
    onkeydown = EventSpec('keydown', binding=wx.EVT_KEY_DOWN, kind=KeyEvent)
    onkeyup = EventSpec('keyup', binding=wx.EVT_KEY_UP, kind=KeyEvent)


class Control(Component):
    "This is the base class for a control"

    # A control is generally a small window which processes user input and/or 
    # displays one or more item of data (for more info see wx.Control)
    # Avoid the term 'widget' as could be confusing (and it is already used in 
    # web2py)
    
    _registry = registry.CONTROLS



if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    w = Component(frame, name="test")
    assert w.get_parent() is frame
    assert w.id != -1       # wx should have assigned a new id!
    assert w.name == "test"
    w.font = dict(face="ubuntu")
    assert w.font.face == "ubuntu"
    # check container methods:
    ct1 = Control(w, name="test_ctrl1")
    ct2 = Control(w, name="test_ctrl2")
    ct2.__init__(name="chau!")      # recreate the control (!= name)
    names = []
    for c in w:
        names.append(c.name)
    assert names == ["test_ctrl1", "chau!"]

