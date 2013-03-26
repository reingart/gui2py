
import decimal
import datetime
import wx

from .event import FocusEvent, MouseEvent, KeyEvent
from .font import Font
from .spec import Spec, EventSpec, InitSpec, DimensionSpec, StyleSpec, InternalSpec
from . import registry

DEBUG = False
COMPONENTS = {}        # map all created objects (used to search parents) 


class ComponentMeta():
    "Component Metadata"
    def __init__(self, name, specs):
        self.name = name
        self.specs = specs
        self.valid_children = []

    
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
            if name not in registry.ALL:
                registry.ALL.append(name)
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
            old_wx_obj = self.wx_obj
            self.wx_obj.obj = None
            del self.wx_obj
            if DEBUG: print "kwargs", kwargs
            if isinstance(self._parent, Component):
                del self._parent[self._name]    # remove old child reference
        else:
            self.set_parent(parent, init=True)
            self._font = None
            self._bgcolor = self._fgcolor = False
            # container to hold children:
            self._children_dict = {}    # key and values for __setitem__
            self._children_list = []    # ordered values for __iter__
            old_wx_obj = None
        
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
                    if name == "name":
                        self._set_name(value)
                    else:
                        setattr(self, spec._name, value)
                else:
                    name = spec_name        # use the spec attribute name
                if value is not None:
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
        if hasattr(self, "_kind"):  # hack to support menu items (TODO: fix)
            self._wx_kwargs['kind'] = self._kind
        else:
            self._wx_kwargs['style'] = style = self._style
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
        for spec_name, spec in sorted(self._meta.specs.items(),
                                      key=lambda it: it[1].order):
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
                    
        # store gui reference inside of wx object
        self.wx_obj.obj = self
        if isinstance(self._parent, Component) and getattr(self, "_name", None):
            self._parent[self._name] = self     # add child reference
            COMPONENTS[self._get_fully_qualified_name()] = self  
        
        # re-associate childrens (wx objects hierachy): 
        if rebuild:
            for ctrl in self:
                ctrl.set_parent(self)

        # destroy previous wx object 
        # (after reparent so children are not destroyed)
        if old_wx_obj:
            old_wx_obj.Destroy()
                
        # finally, set special internal spec (i.e. designer)
        # (this must be done at last to overwrite other event handlers)
        for spec_name, spec in sorted(self._meta.specs.items(),
                                      key=lambda it: it[1].order):
            if isinstance(spec, InternalSpec) and not spec.read_only:
                if DEBUG: print "resetting internal specs (rebound...):", spec_name, self.name
                value = kwargs.get(spec_name, getattr(self, spec_name, spec.default))
                setattr(self, spec_name, value)

    def rebuild(self, recreate=True, **kwargs):
        "Recreate (if needed) the wx_obj and apply new properties"
        # detect if this involves a spec that needs to recreate the wx_obj:
        needs_rebuild = any([isinstance(spec, (StyleSpec, InitSpec)) 
                             for spec_name, spec in self._meta.specs.items()
                             if spec_name in kwargs])
        # validate if this gui object needs and support recreation
        if needs_rebuild and recreate:
            if DEBUG: print "rebuilding window!"
            # recreate the wx_obj! warning: it will call Destroy()
            self.__init__(**kwargs)       
        else:
            if DEBUG: print "just setting attr!"
            for name, value in kwargs.items():
                setattr(self, name, value)


    def __del__(self):
        "Destructor: clean-up all references"
        self.destroy()
    
    def destroy(self):
        "Remove event references and destroy wx object (and children)"
        # unreference the obj from the components map and parent
        if self._name:
            del COMPONENTS[self._get_fully_qualified_name()]
            if DEBUG: print "deleted from components!"
            if isinstance(self._parent, Component):
                del self._parent[self._name]
                if DEBUG: print "deleted from parent!"
        # destroy the wx_obj (only if sure that reference is not needed!)
        if self.wx_obj:
            self.wx_obj.Destroy()
            for child in self:
                print "destroying child", 
                child.destroy()
        # destroy the designer selection marker (if any)
        if hasattr(self, 'sel_marker') and self.sel_marker:
            self.sel_marker.destroy()

    def duplicate(self, new_parent=None):
        "Create a new object exactly similar to self"
        kwargs = {}
        for spec_name, spec in self._meta.specs.items():
            value = getattr(self, spec_name)
            if isinstance(value, Color):
                print "COLOR", value, value.default
                if value.default:
                    value = None
            if value is not None:
                kwargs[spec_name] = value
        del kwargs['parent'] 
        new_id = wx.NewId()
        kwargs['id'] = new_id
        kwargs['name'] = "%s_%s" % (kwargs['name'], new_id)
        new_obj = self.__class__(new_parent or self.get_parent(), **kwargs)
        # recursively create a copy of each child (in the new parent!)
        for child in self:
            child.duplicate(new_obj)
        return new_obj

    def z_order(self, z=0):
        "Raises/lower the window to the top of the window hierarchy (Z-order)"
        # z=0: lowers, z=-1: raises
        if z:
            self.wx_obj.Raise()
        else:
            self.wx_obj.Lower()
        if isinstance(self._parent, Component):
            # get the current index (z-order)
            i = self._parent._children_list.index(self)
            # delete the element reference from the list
            del self._parent._children_list[i]
            # insert as last element
            if z:
                self._parent._children_list.append(self)
            else:
                self._parent._children_list.insert(0, self)
            # rebuild in order:
            for child in self._parent:
                if isinstance(child, Control):
                    child.__init__()

            
    # Container methods:

    def __iter__(self):
        return self._children_list.__iter__()
    
    def __setitem__(self, key, val):
        self._children_dict[key] = val
        self._children_list.append(val)
        
    def __getitem__(self, key):
        return self._children_dict[key]
    
    def __delitem__(self, key):
        del self._children_list[self._children_list.index(self._children_dict[key])]
        del self._children_dict[key]
                
    # Public methods:
    
    def redraw(self):
        "Force an immediate redraw without waiting for an event handler to finish."
        self.wx_obj.Refresh()
        self.wx_obj.Update()

    def set_focus(self):
        self.wx_obj.SetFocus()
    
    def set_parent(self, new_parent, init=False):
        "Store the gui/wx object parent for this component"
        # set init=True if this is called from the constructor
        self._parent = find(new_parent, init)    # store new parent
    
    def get_parent(self):
        "Return the object parent for this component (either gui or wx)"
        if self.wx_obj:
            parent = self.wx_obj.GetParent()
            if hasattr(parent, "obj"):
                return parent.obj  # return the gui object
            else:
                return parent            # return the wx object

    def _get_parent_name(self):
        "Return parent window name (used in __repr__ parent spec)"
        parent = self.get_parent()
        parent_names = []
        while parent:
            if isinstance(parent, Component):
                parent_name = parent.name
                # Top Level Windows has no parent!
                if parent_name:
                    parent_names.insert(0, parent_name)
                parent = parent.get_parent()
            else:
                break
        if not parent_names:
            return None
        else:
            return '.'.join(parent_names) 

    def _get_fully_qualified_name(self):
        "return full parents name + self name (useful as key)"
        parent_name = self._get_parent_name()
        if not parent_name:
            return self._name
        else:
            return "%s.%s" % (parent_name, self._name)
   
    def _get_name(self):
        return getattr(self, "_name", None)
    
    def _set_name(self, value):
        # check if we're changing the previous name (ie., design time)
        if hasattr(self, "_name"):
            key = self._get_fully_qualified_name()
        else:
            key = None
        self._name = value
        # delete old reference (if exists)
        if key in COMPONENTS:
            del COMPONENTS[key]
            COMPONENTS[self._get_fully_qualified_name()] = self  

    
    def __repr__(   self, prefix="gui"):
        return represent(self, prefix)

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
            return None
        wx_font = self.wx_obj.GetFont()
        # sanity check: avoid assertion error:
        if not wx_font.IsOk():
            wx_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._font.set_wx_font(wx_font)
        return self._font

    def _set_fgcolor(self, color):
        color = self._get_default_color(color, "foreground")
        # if not color given, avoid change it to wx.NullColor (fix for OSX)
        if color is not wx.NullColour:
            self.wx_obj.SetForegroundColour(color)
            self.wx_obj.Refresh()   # KEA wxPython bug?
            self._fgcolor = True
        else:
            self._fgcolor = False
    
    def _set_bgcolor(self, color):
        color = self._get_default_color(color, "background")
        # if not color given, avoid change it to wx.NullColor (fix for OSX)
        if color is not wx.NullColour:
            self.wx_obj.SetBackgroundColour(color)
            self.wx_obj.Refresh()   # KEA wxPython bug?
            self._bgcolor = True
        else:
            self._fgcolor = False

    def _get_fgcolor(self):
        color = self.wx_obj.GetForegroundColour()
        if color:
            color = self._get_default_color(color, "foreground")
            c = Color(color.Red(), color.Green(), color.Blue(), color.Alpha())
            c.default = not self._fgcolor
            return c

    def _get_bgcolor(self):
        color = self.wx_obj.GetBackgroundColour()
        if color:
            color = self._get_default_color(color, "background")
            c = Color(color.Red(), color.Green(), color.Blue(), color.Alpha())
            c.default = not self._bgcolor
            return c
        
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

    def _get_default_color(self, color, context="background"):
        if color is None:
            # warning: NullColour is ignored as it doesn't work properly in OSX
            # use wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND) instead
            c = wx.NullColour
        else:
            # KEA 2001-07-27
            # is the right place for this check?
            if isinstance(color, tuple) and len(color) == 3:
                c = Color(color[0], color[1], color[2])
            else:
                if isinstance(color, basestring):
                    c = wx.NamedColour(color)
                else:
                    c = color
        return c

    def _getEnabled(self):
        return self.wx_obj.IsEnabled()

    def _setEnabled(self, aBoolean):
        self.wx_obj.Enable(aBoolean)

    def _getVisible(self):
        return self.wx_obj.IsShown()

    def _setVisible(self, aBoolean):
        self.wx_obj.Show(aBoolean)
    
    def _set_drop_target(self, dt):
        if dt:
            self.wx_obj.SetDropTarget(dt)
    
    name = InitSpec(_get_name, _set_name, optional=False, _name="_name", default="", type='string')
    bgcolor = Spec(_get_bgcolor, _set_bgcolor, type='colour')
    font = Spec(_get_font, _set_font, type='font')
    fgcolor = Spec(_get_fgcolor, _set_fgcolor, type='colour')
    enabled = Spec(_getEnabled, _setEnabled, default=True, type='boolean')
    id = InitSpec(_getId, _setId,  default=-1, type="integer")
    helptext = Spec(optional=True, type="string"),
    tooltip = Spec(_getToolTip, _setToolTip, default='', type="string")
    visible = Spec(_getVisible, _setVisible, default=True, type='boolean')
    userdata = Spec(_name='_userdata')
    parent = Spec(lambda self: self._get_parent_name(), 
                      optional=False, default="",
                      doc="parent window (used internally)")
    drop_target = InternalSpec(lambda self: self.wx_obj.GetDropTarget(), 
                               lambda self, value: self._set_drop_target(value), 
                               doc="drag&drop handler (used in design mode)", 
                               type='internal')
   

class DesignerMixin(object):
    "Designer support"

    __metaclass__ = ComponentBase

    def _set_designer(self, func):
        if DEBUG: print "binding designer handler...", func, self._meta.name
        if func:
            # connect the mouse event handler of the designer:
            self.wx_obj.Bind(wx.EVT_MOUSE_EVENTS, func)
            # link menu selection (click) to the designer
            self.wx_obj.Bind(wx.EVT_MENU, func)
            # link repaint event (refresh) to the designer (draw grid)
            self.wx_obj.Bind(wx.EVT_PAINT, func)
            # link key press event to the designer (move)
            self.wx_obj.Bind(wx.EVT_KEY_DOWN, func)
            self.wx_obj.Bind(wx.EVT_KEY_UP, func)
            # bind top level window resizing and closing event:
            if self._parent is None:
                self.wx_obj.Bind(wx.EVT_SIZE, func)
                self.wx_obj.Bind(wx.EVT_CLOSE, func)
            self._designer = func
            for child in self:
                child.designer = func

    designer = InternalSpec(lambda self: self._designer, 
                            lambda self, value: self._set_designer(value), 
                            doc="function to handle events in design mode", 
                            type='internal')

    sel_marker = InternalSpec(_name="_sel_marker",
                              doc="selection marker in design mode", 
                              type='internal')

   
class Control(Component, DesignerMixin):
    "This is the base class for a control"

    # A control is generally a small window which processes user input and/or 
    # displays one or more item of data (for more info see wx.Control)
    # Avoid the term 'widget' as could be confusing (and it is already used in 
    # web2py)
    
    _registry = registry.CONTROLS

    def __init__(self, parent=None, **kwargs):        
        # set safe initial dimensions
        if not hasattr(self, '_resizable'):
            self._resizable = kwargs.get('resizable', True)
            self._left = self._top = self._width = self._height = None
            self._margins = [0] * 4  # left, top, right, bottom
        # call default contructor
        Component.__init__(self, parent, **kwargs) 
        # Handle resize events to adjust absolute and relative dimensions
        if self._resizable:
            self.wx_obj.Bind(wx.EVT_SIZE, self.resize)

    def set_parent(self, new_parent, init=False):
        "Re-parent a child control with the new wx_obj parent"
        Component.set_parent(self, new_parent, init)
        # if not called from constructor, we must also reparent in wx:
        if not init:
            if DEBUG: print "reparenting", ctrl.name
            if isinstance(self.wx_obj, wx.Window):
                self.wx_obj.Reparent(self._parent.wx_obj)

    # Dimensions:

    def _calc_dimension(self, dim_val, dim_max, font_dim):
        "Calculate final pos and size (auto, absolute in pixels & relativa)"
        if dim_val is None:
            return -1   # let wx automatic pos/size
        elif isinstance(dim_val, int):
            return dim_val  # use fixed pixel value (absolute)
        elif isinstance(dim_val, basestring):
            if dim_val.endswith("%"):
                # percentaje, relative to parent max size:
                dim_val = int(dim_val[:-1])
                dim_val = dim_val / 100.0 * dim_max
            elif dim_val.endswith("em"):
                # use current font size (suport fractions):
                dim_val = float(dim_val[:-2])
                dim_val = dim_val * font_dim
            elif dim_val.endswith("px"):
                # fixed pixels
                dim_val = dim_val[:-2]
            elif dim_val == "" or dim_val == "auto":
                dim_val = -1
            return int(dim_val)                        
    
    def _get_pos(self):
        # get the actual position, not (-1, -1)
        return self.wx_obj.GetPositionTuple()

    def _set_pos(self, point):
        # check parameters (and store user values for resize)
        point = list(point)
        if point[0] is None:
            point[0] = self.wx_obj.GetPositionTuple()[0]  # no change
        else:
            self._left = str(point[0])  # use the new value
        if point[1] is None:
            point[1] = self.wx_obj.GetPositionTuple()[1]  # no change
        else:
            self._top = str(point[1])  # use the new value
        # get parent or screen size (used to calc the percent)
        if self.parent and self.wx_obj.GetParent():
            parent_size = self.wx_obj.GetParent().GetSize()
        else:
            parent_size = wx.DisplaySize()
        # get font metrics for "em" unit
        font_width = self.wx_obj.GetCharWidth()
        font_height = self.wx_obj.GetCharHeight()
        # calculate actual position (auto, relative or absolute)
        x = self._calc_dimension(point[0], parent_size[0], font_width) + self.margin_left
        y = self._calc_dimension(point[1], parent_size[1], font_height) + self.margin_top
        self.wx_obj.Move((x, y))
        # update the designer selection marker (if any)
        if hasattr(self, 'sel_marker') and self.sel_marker:
            self.sel_marker.update()

    def _get_size(self):
        # return the actual size, not (-1, -1)
        return self.wx_obj.GetSizeTuple()

    def _set_size(self, size, new_size=None):
        # check parameters (and store user values for resize)
        size = list(size)
        if size[0] is None:
            size[0] = self.wx_obj.GetSizeTuple()[0]  # no change
        else:
            self._width = str(size[0])  # use the new value
        if size[1] is None:
            size[1] = self.wx_obj.GetSizeTuple()[1]  # no change
        else:
            self._height = str(size[1])  # use the new value
        # get parent or screen size (used to calc the percent)
        if new_size:
            parent_size = new_size  # use event size instead
        elif self.parent and self.wx_obj.GetParent():
            parent_size = self.wx_obj.GetParent().GetSize()
        else:
            parent_size = wx.DisplaySize()
        # get font metrics for "em" unit
        font_width = self.wx_obj.GetCharWidth()
        font_height = self.wx_obj.GetCharHeight()
        # calculate actual position (auto, relative or absolute)
        w = self._calc_dimension(size[0], parent_size[0], font_width) - self.margin_left - self.margin_right
        h = self._calc_dimension(size[1], parent_size[1], font_height) - self.margin_top - self.margin_bottom
        # on windows set the client size (ignore title bar)
        # note: don't do on controls (it doesn't work at least for textbox)
        if DEBUG: print "NEWSIZE", w, h
        if isinstance(self.wx_obj, wx.TopLevelWindow):
            self.wx_obj.SetClientSize((w, h))
        else:
            self.wx_obj.SetSize((w, h))
        # update the designer selection marker (if any)
        if hasattr(self, 'sel_marker') and self.sel_marker:
            self.sel_marker.update()

    def _get_margin(self, index):
        return self._margins[index] or 0
    
    def _set_margin(self, value, index):
        self._margins[index] = value
        self.resize()

    def resize(self, evt=None):
        "automatically adjust relative pos and size of children controls"
        if DEBUG: print "RESIZE!", self.name, self.width, self.height
        if not isinstance(self.wx_obj, wx.TopLevelWindow):
            # check that size and pos is relative, then resize/move
            if self._left and self._left[-1] == "%" or \
               self._top and self._top[-1] == "%":
                print "RESIZING", self.name, self._width
                self._set_pos((self._left, self._top))
            if self._width and self._width[-1] == "%" or \
               self._height and self._height[-1] == "%":
                print "RESIZING", self.name, self._width
                self._set_size((self._width, self._height))
        for child in self:
            if isinstance(child, Control):
                child.resize(evt)
        # call original handler (wx.HtmlWindow)
        if evt:
            evt.Skip()
    
    def get_char_width(self):
        "Returns the average character width for this window."
        return self.wx_obj.GetCharWidth()
    
    def get_char_height(self):
        "Returns the character height for this window."
        return self.wx_obj.GetCharHeight()


    pos = InitSpec(_get_pos, _set_pos, default=[ -1, -1])
    size = InitSpec(_get_size, _set_size, default=[ -1, -1])
    client_size = Spec(lambda self: self.wx_obj.GetClientSize(),
                       lambda self, value: self.wx_obj.SetClientSize(value),
                       default=[ -1, -1])

    width = DimensionSpec(lambda self: self._width, 
                          lambda self, value: self._set_size([value, None]),
                          default="", type="string", group="size")
    height = DimensionSpec(lambda self: self._height, 
                           lambda self, value: self._set_size([None, value]),
                           default="", type="string", group="size")
    left = DimensionSpec(lambda self: self._left, 
                           lambda self, value: self._set_pos([value, None]),
                           default="", type="string", group="position")
    top = DimensionSpec(lambda self: self._top, 
                           lambda self, value: self._set_pos([None, value]),
                           default="", type="string", group="position")
    margin_left = DimensionSpec(lambda self: self._get_margin(0), 
                           lambda self, value: self._set_margin(value, 0),
                           default=0, type="integer", group="margin")
    margin_top = DimensionSpec(lambda self: self._get_margin(1), 
                           lambda self, value: self._set_margin(value, 1),
                           default=0, type="integer", group="margin")
    margin_right = DimensionSpec(lambda self: self._get_margin(2), 
                           lambda self, value: self._set_margin(value, 2),
                           default=0, type="integer", group="margin")
    margin_bottom = DimensionSpec(lambda self: self._get_margin(3),
                           lambda self, value: self._set_margin(value, 3),
                           default=0, type="integer", group="margin")

    border = StyleSpec({'default': wx.BORDER_DEFAULT,
                        'simple': wx.BORDER_SIMPLE,
                        'sunken': wx.BORDER_SUNKEN,
                        'raised': wx.BORDER_RAISED,
                        'static': wx.BORDER_STATIC,
                        'theme': wx.BORDER_THEME, # native
                        'none': wx.BORDER_NONE, },
                       doc="Kind of border to show (some will have no effect"
                           " depending on control and platform)",
                       default='default')

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


class SubComponent(object):
    "Base class to use in complex controls (like ListView)"
    
    __metaclass__ = ComponentBase
    wx_obj = None               # no wx object is related
    
    def __iter__(self):
        return [].__iter__()    # we have no children (designer!)
    
    def __init__(self, parent=None, **kwargs):
        # set up the properties:
        for spec_name, spec in self._meta.specs.items():
            if not spec.read_only:
                value = kwargs.get(spec_name, spec.default)
                setattr(self, spec_name, value)
        self.set_parent(parent, init=True)

    def set_parent(self, new_parent, init=False):
        "Associate the component to the control (it could be recreated)"
        # store gui reference inside of wx object (this will enable rebuild...)
        self._parent = find(new_parent, init=False)    # store new parent
        if init:
            self._parent[self._name] = self     # add child reference

    def rebuild(self, **kwargs):
        "Update a property value with (used by the designer)"
        for name, value in kwargs.items():
            setattr(self, name, value)

    def destroy(self, **kwargs):
        pass

    def __repr__(self, prefix="gui"):
        return represent(self, prefix)

    parent = Spec(lambda self: self._parent.name, 
                      optional=False, default="",
                      doc="parent window (used internally)")


# Auxiliary functions & classes:


class Color(wx.Colour):
    "Helper to represent the colour and detect if a colour is the default"
    
    default = True
    
    def __repr__(self):
        if not self.default:
            return repr(self.GetAsString(wx.C2S_HTML_SYNTAX))
        else:
            return 'None'

            
def new_id(id=None):
    if id is None or id == -1:
        return wx.NewId()
    else:
        return id


sort_order_map = {InitSpec: 1, DimensionSpec: 3, StyleSpec: 2, EventSpec: 5, Spec: 4}


def get_sort_key((name, spec)):
    return sort_order_map.get(spec.__class__, 6), name


def represent(obj, prefix, max_cols=80):
    "Construct a string representing the object"
    try:
        name = getattr(obj, "name", "")
        class_name = "%s.%s" % (prefix, obj.__class__.__name__)
        padding = len(class_name) + 1
        params = []
        for (k, spec) in sorted(obj._meta.specs.items(), key=get_sort_key):
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
                ):
                params.append("%s=%s" % (k, repr(v))) 
        param_lines = []
        line = ""
        for param in params:
            if len(line + param) + 3 > max_cols - padding:
                param_lines.append(line)
                line = ""
            line += param + ", "
        param_lines.append(line)
        param_str = ("\n%s" % (" " * padding)).join(param_lines)
        return "%s(%s)" % (class_name, param_str)
    except:
        raise
        # uninitialized, use standard representation to not break debuggers
        return object.__repr__(obj)


def find(obj_name, init=False):
    "Find an object already created"
    wx_parent = None
    # check if new_parent is given as string (useful for designer!)
    if isinstance(obj_name, basestring):
        # find the object reference in the already created gui2py objects
        # TODO: only useful for designer, get a better way
        obj_parent = COMPONENTS.get(obj_name)
        if not obj_parent:
            # try to find window (it can be a plain wx frame/control)
            wx_parent = wx.FindWindowByName(obj_name)
            if wx_parent:
                # store gui object (if any)
                obj_parent = getattr(wx_parent, "obj") 
            else:
                # fallback using just object name (backward compatibility)
                for obj in COMPONENTS.values():
                    if obj.name==obj_name:
                        obj_parent = obj 
    else:
        obj_parent = obj_name     # use the provided parent (as is)
    return obj_parent or wx_parent       # new parent



if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    w = Component(frame, name="test")
    # test representation:
    print w
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

