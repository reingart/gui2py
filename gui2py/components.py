import wx

from .event import FocusEvent, MouseEvent, KeyEvent
from .font import Font
from .spec import Spec, EventSpec, InitSpec, DimensionSpec, StyleSpec, InternalSpec
from . import registry

DEBUG = False

def new_id(id=None):
    if id is None or id == -1:
        return wx.NewId()
    else:
        return id


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
    # to a gui2py.event.Event ( UIEvent, MouseEvent, etc ) and call the handler
    
    # This is the base class wich all GUI Elements should derive 
    # (TopLevelWindows -Frame, Dialog, etc.- and Controls)
    # This object maps to wx.Window, but avoid that name as it can be confusing.
    
    __metaclass__ = ComponentBase
    _wx_class = wx.Window       # wx object constructor
    _style = 0                  # base style
    _image = None               # default icon for toolbox
    
    def __init__(self, parent=None, **kwargs):
    
        # create the wxpython kw arguments (based on specs and defaults)
        wx_kwargs = dict(id=new_id(kwargs.get('id')))
        
        # check if we are recreating the object (i.e., to apply a new style)
        rebuild = hasattr(self, "wx_obj")
        
        # get current spec values (if we are re-creating the wx object)
        if rebuild:
            for spec_name, spec in self._meta.specs.items():
                if spec_name in kwargs:
                    continue    # use provided new value
                if not isinstance(spec, (InternalSpec)):
                    # get the current value and store it in kwargs
                    kwargs[spec_name]  = getattr(self, spec_name)
            self.wx_obj.Visible = False
            self.wx_obj.reference = None
            self.wx_obj.Destroy()
            del self.wx_obj
            if DEBUG: print "kwargs", kwargs
            if isinstance(self._parent, Component):
                del self._parent[self._name]    # remove old child reference
        else:
            if isinstance(parent, basestring):
                # find the object reference
                parent = wx.FindWindowByName(parent).reference
            self._parent = parent       # store parent
            self._font = None
            self._children = {}    # container to hold children
        
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
        # sanitize parameters
        if 'id' in self._wx_kwargs and self._wx_kwargs['id'] <= 0:
            self._wx_kwargs['id'] = -1
            
        self.wx_obj = self._wx_class(wx_parent, **self._wx_kwargs)
        # load specs from kwargs, use default if available
        for spec_name, spec in self._meta.specs.items():
            if spec.read_only or isinstance(spec, (StyleSpec, InitSpec, InternalSpec)):
                continue
            # get the spec value for kwargs, if it is optional, get the default
            if spec_name in kwargs:
                # set the value passed to the constructor
                setattr(self, spec_name, kwargs[spec_name])
            elif spec.default is not None or isinstance(spec, EventSpec):
                # set the default value
                setattr(self, spec_name, spec.default)
            elif not spec.optional:
                raise ValueError("%s: %s is not optional" % (self._meta.name,
                                                             spec_name))
            else:
                # asign a empty value (just to set up internal properties)
                setattr(self, spec_name, None)
                    
        # store gui2py reference inside of wx object
        self.wx_obj.reference = self
        if isinstance(self._parent, Component) and self._name:
            self._parent[self._name] = self     # add child reference
        
        # re-associate childrens (wx objects hierachy): 
        if rebuild:
            for ctrl in self:
                if DEBUG: print "reparenting", ctrl.name 
                ctrl.wx_obj.Reparent(self.wx_obj)
                
        # finally, set special internal spec (i.e. designer)
        # (this must be done at last to overwrite other event handlers)
        for spec_name, spec in self._meta.specs.items():
            if isinstance(spec, InternalSpec):
                if DEBUG: print "resetting internal specs (rebound...):", spec_name, self.name
                value = kwargs.get(spec_name, getattr(self, spec_name, None))
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
        parent = self.wx_obj.GetParent()
        if hasattr(parent, "reference"):
            return parent.reference  # return the gui2py object
        else:
            return parent            # return the wx object

    def _get_parent_name(self):
        "Return parent window name (used in __repr__ parent spec)"
        parent = self.get_parent()
        if isinstance(parent, Component):
            return parent.name
        else:
            return None

    def __repr__(self):
        return "%s = %s(%s)" % (
                self.name, self.__class__.__name__, 
                ', '.join(["\n            %s=%s" % 
                (k, repr(getattr(self, k))) 
                for (k, spec) in sorted(self._meta.specs.items())
                if not isinstance(spec, InternalSpec) 
                   and getattr(self, k) != spec.default
                   and isinstance(getattr(self, k), 
                         (basestring, int, long, bool, dict, list, Font))                
                ]))

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

    def _set_designer(self, func):
        if DEBUG: print "binding designer handler...", func, self._meta.name
        if func:
            # remove all binded events:
            self.wx_obj.Unbind(wx.EVT_MOTION)
            self.wx_obj.Unbind(wx.EVT_LEFT_DOWN)
            self.wx_obj.Unbind(wx.EVT_LEFT_UP)
            self.wx_obj.Unbind(wx.EVT_LEFT_DCLICK)
            self.wx_obj.Unbind(wx.EVT_RIGHT_DOWN)
            self.wx_obj.Unbind(wx.EVT_RIGHT_UP)
            self.wx_obj.Unbind(wx.EVT_RIGHT_DCLICK)
            self.wx_obj.Unbind(wx.EVT_MOUSE_EVENTS)
            self.wx_obj.Unbind(wx.EVT_ENTER_WINDOW)
            self.wx_obj.Unbind(wx.EVT_LEAVE_WINDOW)
            # connect the mouse event handler of the designer:
            self.wx_obj.Bind(wx.EVT_MOUSE_EVENTS, func)
            self._designer = func
            for child in self:
                child.designer = func
   
    def _set_drop_target(self, dt):
        if dt:
            self.wx_obj.SetDropTarget(dt)
            # TODO: check if any children is a droptarget too (i.e panels)
    
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
    designer = InternalSpec(lambda self: self._designer, 
                            lambda self, value: self._set_designer(value), 
                            doc="function to handle events in design mode", 
                            type='internal')
    drop_target = InternalSpec(lambda self: self.wx_obj.GetDropTarget(), 
                               lambda self, value: self._set_drop_target(value), 
                               doc="drag&drop handler (used in design mode)", 
                               type='internal')
    parent = Spec(lambda self: self._get_parent_name(), 
                      optional=False, default="",
                      doc="parent window (used internally)")
                                            
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

