import wx

from .event import FocusEvent, MouseEvent
from . import registry

def new_id(id=None):
    if id is None or id == -1:
        return wx.NewId()
    else:
        return id


class Spec(property):
    "Spec contains meta type information about components"
    
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, 
                 optional=True, default=None, values=None, _name=""):
        if fget is None:
            fget = lambda obj: getattr(obj, _name)
            fset = lambda obj, value: setattr(obj, _name, value)
        property.__init__(self, fget, fset, fdel, doc)
        self.optional = optional
        self.default = default
        self.values = values
        self.read_only = fset is None
        self._name = _name              # internal name (usually, wx kwargs one)
    

class EventSpec(Spec):
    "Generic Event Handler: maps a wx.Event to a gui2py.Event"
    
    def __init__(self, event_name, binding, kind, doc=None):
        getter = lambda obj: getattr(obj, "_" + event_name)
        def setter(obj, action):
            # check if there is an event binded previously:
            if hasattr(obj, "_" + event_name):
                # disconnect the previous binded events
                obj.wx_obj.Unbind(self.binding)
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
                obj.wx_obj.Bind(self.binding, handler)
            # store the event handler
            setattr(obj, "_" + event_name, action)

        Spec.__init__(self, getter, setter, doc=doc)
        self.name = event_name
        self.binding = binding          # wx.Event object
        self.kind = kind                # Event class
    

class InitSpec(Spec):
    "Spec that is used in wx object instantiation (__init__)"


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
            for key, value in self.wx_style_map.items():
                if wx_value & value:
                    return key
            return None

        def setter(obj, value):
            if obj.wx_obj:
                # fset is ignored by now, if object was created throw and error:
                raise AttributeError("style is read-only!")
            if value is None:
                raise ValueError("this style spec is mandatory!")
            if value not in self.wx_style_map:
                raise ValueError("%s is not a valid value!" % value)
            # convert the value to the wx style
            obj._style |= self.wx_style_map[value]
        Spec.__init__(self, getter, setter, doc=doc, default=default)


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
    
    def __init__(self, parent=None, **kwargs):
        self._font = None
    
        # create the wxpython kw arguments (based on specs and defaults)
        wx_kwargs = dict(id=new_id(kwargs.get('id')))
        self.wx_obj = None
        for spec_name, spec in self._meta.specs.items():
            value = kwargs.get(spec_name, spec.default)
            if isinstance(spec, InitSpec):
                print "INIT: setting ", spec_name, value
                if spec._name:
                    name = spec._name[1:]   # use the internal name
                    setattr(self, spec._name, value)
                else:
                    name = spec_name        # use the spec attribute name
                wx_kwargs[name] = value
                if spec_name in kwargs:
                    del kwargs[spec_name]
            if isinstance(spec, StyleSpec):
                print "setting", spec_name, value, spec
                setattr(self, spec_name, value)
                if spec_name in kwargs:
                    del kwargs[spec_name]
        
        # create the actual wxpython object
        wx_kwargs['style'] = style=self._style
        print "WX KWARGS: ", wx_kwargs
        print "creating", self._wx_class
        self.wx_obj = self._wx_class(parent, **wx_kwargs)
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
            setattr(self, spec_name, value)
                
        # store gui2py reference inside of wx object
        self.wx_obj.reference = self

    def _set_style(self, **kwargs):
        for spec_name, spec in self._meta.specs.items():
            if isinstance(spec, StyleSpec):
                setattr(self, spec_name, value)

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
    
    def _getFont(self):
        if self._font is None:
            #desc = font.fontDescription(self.GetFont())
            #self._font = font.Font(desc)
            pass
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
    
    def _setFont(self, aFont):
        if aFont is None:
            self._font = None
            return
        if isinstance(aFont, dict):
            aFont = font.Font(aFont, aParent=self)
        else: # Bind the font to this component.
            aFont._parent = self
        self._font = aFont
        aWxFont = aFont._getFont()
        self.wx_obj.SetFont( aWxFont )

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
                
    def _getPosition(self):
        # get the actual position, not (-1, -1)
        return self.wx_obj.GetPositionTuple()  

    def _setPosition(self, aPosition):
        self.wx_obj.Move(aPosition)

    def _getSize(self):
        # return the actual size, not (-1, -1)
        return self.wx_obj.GetSizeTuple()

    def _setSize(self, aSize):
        self.wx_obj.SetSize(aSize)

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

    name = InitSpec(optional=False, _name="_name")
    bgcolor = Spec(_getBackgroundColor, _setBackgroundColor)
    font = Spec(_getFont, _setFont)
    fgcolor = Spec(_getForegroundColor, _setForegroundColor)
    enabled = Spec(_getEnabled, _setEnabled, default=True)
    id = InitSpec(_getId, _setId,  default=-1)
    pos = InitSpec(_getPosition, _setPosition, default=[ -1, -1])
    size = InitSpec(_getSize, _setSize, default=[ -1, -1])
    helptext = Spec(optional=True),
    tooltip = Spec(_getToolTip, _setToolTip, default='')
    visible = Spec(_getVisible, _setVisible, default=True)
    userdata = Spec(_name='_userdata')
    
    # Events:
    onfocus = EventSpec('focus', binding=wx.EVT_SET_FOCUS, kind=FocusEvent)
    onblur = EventSpec('blur', binding=wx.EVT_KILL_FOCUS, kind=FocusEvent)
    onmousemove = EventSpec('mousemove', binding=wx.EVT_MOTION, kind=MouseEvent) 
    onmouseover = EventSpec('mouseover', binding=wx.EVT_ENTER_WINDOW, kind=MouseEvent) 
    onmouseout = EventSpec('mouseout', binding=wx.EVT_LEAVE_WINDOW, kind=MouseEvent) 
    onmousewheel = EventSpec('mousewheel', binding=wx.EVT_MOUSEWHEEL, kind=MouseEvent) 
    onmouseleftdown = EventSpec('mouseleftdown', binding=wx.EVT_LEFT_DOWN, kind=MouseEvent)
    onmouseleftup = EventSpec('mouseleftup', binding=wx.EVT_LEFT_DOWN, kind=MouseEvent)
    onmouseleftdclick = EventSpec('mouseleftdclick', binding=wx.EVT_LEFT_DCLICK, kind=MouseEvent)
    onmousemiddledown = EventSpec('mousemiddledown', binding=wx.EVT_MIDDLE_DOWN, kind=MouseEvent)
    onmousemiddleup = EventSpec('mousemiddleup', binding=wx.EVT_MIDDLE_DOWN, kind=MouseEvent)
    onmousemiddledclick = EventSpec('mousemiddledclick', binding=wx.EVT_MIDDLE_DCLICK, kind=MouseEvent)
    onmouserightdown = EventSpec('mouserightdown', binding=wx.EVT_RIGHT_DOWN, kind=MouseEvent)
    onmouserightup = EventSpec('mouserightup', binding=wx.EVT_RIGHT_DOWN, kind=MouseEvent)
    onmouserightdclick = EventSpec('mouserightdclick', binding=wx.EVT_RIGHT_DCLICK, kind=MouseEvent)


class Control(Component):
    "This is the base class for a control"

    # A control is generally a small window which processes user input and/or 
    # displays one or more item of data (for more info see wx.Control)
    # Avoid the term 'widget' as could be confusing (and it is already used in 
    # web2py)
    
    _registry = registry.WIDGETS



if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    w = Component(frame, name="test")
    assert w.get_parent() is frame
    assert w.id != -1       # wx should have assigned a new id!
    assert w.name == "test"
    