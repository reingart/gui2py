import wx

from . import event

def new_id(id=None):
    if id is None or id == -1:
        return wx.NewId()
    else:
        return id


class Spec:
    "Spec contains meta type information about widgets"
    
    def __init__(self, name, optional=False, default=None):
        self.name = name
        self.optional = optional
        self.default = default


class Widget(object):
    "The base class for all of our GUI controls"
    # Each Widget must bind itself to the wxPython event model.  
    # When it receives an event from wxPython, it will convert the event
    # to a gui2py.event.Event ( UIEvent, MouseEvent, etc ) and call the handler
    
    specs = [ 
            Spec('id', optional=True, default=-1),
            Spec('name', optional=True, default=""),
            Spec('enabled', optional=True, default=True),
            Spec('visible', optional=True, default=True),
            Spec('foregroundcolor', optional=True, default=None),
            Spec('backgroundcolor', optional=True, default=None),
            Spec('helptext', optional=True, default=''),
            Spec('tooltip', optional=True, default=''),
            Spec('font', optional=True, default=None),
            Spec('position', optional=True, default=[ -1, -1]),
            Spec('size', optional=True, default=[ -1, -1]),
            Spec('userdata', optional=True, default=''),
            ]
    
    handlers = [] # {'click': (wx.EVT_BUTTON, event.FormEvent)}
    
    def __init__(self):
        self.wx_obj = None            # wx object (i.e. wx.Button)
        self._font = None

    def __call__(self, field, value):
        "Returns a HTML string representation of the widget (used by web2py)"
        ## DAL usage: Field('comment', 'string', widget=my_string_widget)
        return INPUT(_name=field.name,
                 _id="%s_%s" % (field._tablename, field.name),
                 _class=field.type,
                 _value=value,
                 requires=field.requires)
 
    # methods:
    
    def create(self, parent=None, **kwargs):
        "Acutally create the GUI Button for 2-phase creation."
        # create dummy wxpython object (for testing)
        if parent:
            self.wx_obj = wx.Window(parent)
        # load specs from kwargs, use default if available
        for spec in self.specs:
            if True or DEBUG:
                print "setting", spec.name, kwargs.get(spec.name, spec.default)
            setattr(self, spec.name, kwargs.get(spec.name, spec.default))
        # store gui2py reference inside of wx object
        self.wx_obj.reference = self
    
    def attach(self, event_name, action):
        "Add an event listener (map a event handler with the action)"
        for handler in self.handlers:
            if handler.name == event_name:
                self.wx_obj.Bind(handler.binding, handler(action))
                break
        else:
            raise RuntimeError("%s is not a valid event name!" % event_name)
        
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
            desc = font.fontDescription(self.GetFont())
            self._font = font.Font(desc)
        return self._font

    def _setForegroundColor( self, color ) :
        color = self._getDefaultColor( color )
        self.wx_obj.SetForegroundColour( color )
        self.wx_obj.Refresh()   # KEA wxPython bug?
    
    def _setBackgroundColor( self, color ) :
        color = _setBackgroundColor._getDefaultColor( color )
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
        
    background_color = property(_getBackgroundColor, _setBackgroundColor)
    font = property(_getFont, _setFont)
    foreground_color = property(_getForegroundColor, _setForegroundColor)
    enabled = property(_getEnabled, _setEnabled)
    id = property(_getId, _setId)
    position = property(_getPosition, _setPosition)
    size = property(_getSize, _setSize)
    tooltip = property(_getToolTip, _setToolTip)
    userdata = property(_getUserdata, _setUserdata)
    visible = property(_getVisible, _setVisible)
    

if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    w = Widget()
    w.create(frame)
    assert w.get_parent() is frame
    assert w.id != -1       # wx should have assigned a new id!
    assert w.name == ""