import wx

from .event import FocusEvent, MouseEvent
from . import registry

def new_id(id=None):
    if id is None or id == -1:
        return wx.NewId()
    else:
        return id


class Spec(property):
    "Spec contains meta type information about widgets"
    
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
                handler = lambda wx_event: action(self.kind(name=self.name, 
                                                 wx_event=wx_event))
                # connect the new action to the event:
                obj.wx_obj.Bind(self.binding, handler)
                # store the event handler
            setattr(obj, "_" + event_name, action)

        Spec.__init__(self, getter, setter, doc=doc)
        self.name = event_name
        self.binding = binding          # wx.Event object
        self.kind = kind                # Event class
    

class WidgetMeta():
    "Widget Metadata"
    def __init__(self, name, specs):
        self.name = name
        self.specs = specs

    
def widget_metaclass(name, bases, attrs):
    "Widget class constructor (creates metadata and register the widget)"
    
    specs = {}
    # get specs of the base class
    for base in bases:
        if hasattr(base, "_meta"):
            specs.update(base._meta.specs)
    # get all the specs
    specs.update(dict([(attr_name, attr_value) 
                    for attr_name, attr_value in attrs.items() 
                    if isinstance(attr_value, Spec)]))
    # insert a _meta attribute with the specs
    attrs["_meta"] = WidgetMeta(name, specs)

    # registry and return the new class:
    new_class = type(name, bases, attrs)
    registry.WIDGETS[name] = new_class
    return new_class

  
class Widget(object):
    "The base class for all of our GUI controls"
    # Each Widget must bind itself to the wxPython event model.  
    # When it receives an event from wxPython, it will convert the event
    # to a gui2py.event.Event ( UIEvent, MouseEvent, etc ) and call the handler
    
    __metaclass__ = widget_metaclass
    
    def __init__(self, parent=None, **kwargs):
        self._font = None

        # create dummy wxpython object (for testing)
        if parent:
            self.wx_obj = wx.Window(parent)
        # load specs from kwargs, use default if available
        for spec_name, spec in self._meta.specs.items():
            if spec.read_only:
                print "Cont", spec_name
                continue
            if True or DEBUG:
                print "setting", spec_name, kwargs.get(spec_name, spec.default)
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
        else: # Bind the font to this widget.
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
    
    name = Spec(optional=False, _name="_name")
    background_color = Spec(_getBackgroundColor, _setBackgroundColor)
    font = Spec(_getFont, _setFont)
    foreground_color = Spec(_getForegroundColor, _setForegroundColor)
    enabled = Spec(_getEnabled, _setEnabled, default=True)
    id = Spec(_getId, _setId,  default=-1)
    position = Spec(_getPosition, _setPosition, default=[ -1, -1])
    size = Spec(_getSize, _setSize, default=[ -1, -1])
    helptext = Spec(optional=True),
    tooltip = Spec(_getToolTip, _setToolTip, default='')
    userdata = Spec(_getUserdata, _setUserdata)
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


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    w = Widget(frame, name="test")
    assert w.get_parent() is frame
    assert w.id != -1       # wx should have assigned a new id!
    assert w.name == "test"