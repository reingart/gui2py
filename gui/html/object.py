# based on wx.lib.wxpTag (Robin Dunn 1999, Jeff Grimmett 2003 wxWindows license)

from . import GetParam, input
from .input import FormControlMixin

from .. import registry 


import  wx
import  wx.html


HtmlCtrlClickEventType = wx.NewEventType()
HTML_CTRL_CLICK = wx.PyEventBinder(HtmlCtrlClickEventType)


class HtmlCtrlClickEvent(wx.PyEvent):
    "Event used in designer to"
    def __init__(self, ctrl):
        wx.PyEvent.__init__(self)
        self.SetEventType(HtmlCtrlClickEventType)
        self.ctrl = ctrl


class ObjectTagHandler(wx.html.HtmlWinTagHandler):
    def __init__(self):
        wx.html.HtmlWinTagHandler.__init__(self)
        self.params = {}

    def GetSupportedTags(self):
        return "OBJECT,PARAM"

    def HandleTag(self, tag):
        name = tag.GetName()
        if name == "OBJECT":
            return self.HandleObjectTag(tag)
        elif name == "PARAM":
            return self.HandleParamTag(tag)
        else:
            raise ValueError('unknown tag: %s' % name)


    def HandleObjectTag(self, tag):
        # create a new dict to store params
        self.params = {}
        # find and verify the class
        if not tag.HasParam('CLASS'):
            raise AttributeError("OBJECT tag requires a CLASS attribute")
        class_name = tag.GetParam('CLASS')
        if class_name not in registry.CONTROLS:
            raise TypeError("OBJECT tag attribute CLASS must be registered")
        obj_class = registry.CONTROLS[class_name]

        parent = self.GetParser().GetWindowInterface().GetHTMLWindow()

        # now look for width and height
        width = -1
        height = -1
        float_width = 0
        if tag.HasParam('WIDTH'):
            width = tag.GetParam('WIDTH')
            if width[-1] == '%':
                float_width = int(width[:-1], 0)
                width = float_width
            else:
                width = int(width)
        if tag.HasParam('HEIGHT'):
            height = tag.GetParam('HEIGHT')
            if height[-1] == '%':
                ##import pdb; pdb.set_trace()
                # float_height is not implemented by wx, use parent height
                float_height = int(height[:-1], 0)
                height = parent.Parent.GetSize()[1]*float_height/100 
            else:
                height = int(height)
        self.params['size'] = (width, height)

        # parse up to the closing tag, and gather any nested Param tags.
        self.ParseInner(tag)

        # create the object
        parent = self.GetParser().GetWindowInterface().GetHTMLWindow()
        if parent:
            
            try:
                obj = obj_class(parent, **self.params)
            except Exception, e:
                import pdb; pdb.set_trace()
            obj.visible = True
            # add it to the HtmlWindow
            cell = wx.html.HtmlWidgetCell(obj.wx_obj, float_width)
            cell.obj = obj    # store the gui object ref
            self.GetParser().GetContainer().InsertCell(cell)

            # designer-mode: "capture" mouse events and send fake click ones

            if parent.obj.design:
            
                def OnMotion(evt):
                    print "OnMotion!"
                    evt_obj = evt.GetEventObject()
                    x, y = evt_obj.Position
                    fw, fh = evt_obj.Size
                    print "Blit", x,y, fw, fh, x,y
                    dc = wx.ClientDC(obj.get_parent())
                    dc.Blit(x,y, fw, fh, dc, x,y, wx.SRC_INVERT)
                    
                    #evt.Skip()
                    dc.DrawRectanglePointSize((x, y), (fw, fh))
                    
                    # simulate the cell event (they aren't for HtmlWidgetCell):
                    if evt.GetEventType() == wx.EVT_MOTION.typeId:
                        command_type = wx.html.EVT_HTML_CELL_HOVER.typeId
                    else:
                        command_type = wx.html.EVT_HTML_CELL_CLICKED.typeId
                        #pt = x, y
                        new_evt = HtmlCtrlClickEvent(obj)
                        #new_evt.SetEventObject(evt_obj)
                        print "evt cell ref", cell.obj
                    #new_evt.SetId(cell.GetId()) 
                    parent.GetEventHandler().ProcessEvent(evt) 

                obj.wx_obj.Bind(wx.EVT_MOTION, OnMotion)
                obj.wx_obj.Bind(wx.EVT_LEFT_DOWN, OnMotion)

        return True


    def HandleParamTag(self, tag):
        ##import pdb; pdb.set_trace()
        if not tag.HasParam('NAME'):
            return False

        name = tag.GetParam('NAME')
        value = ""
        if tag.HasParam('VALUE'):
            value = tag.GetParam('VALUE')

        if not value:
            value = None
        elif value[0] == '#':
            # convert to wx.Colour
            try:
                red   = int('0x'+value[1:3], 16)
                green = int('0x'+value[3:5], 16)
                blue  = int('0x'+value[5:], 16)
                value = wx.Colour(red, green, blue)
            except:
                pass
        else:
            # check for something that should be evaluated
            try:
                value = eval(value)
            except Exception, e:
                import pdb; pdb.set_trace()

        self.params[name] = value
        return False


wx.html.HtmlWinParser_AddTagHandler(ObjectTagHandler)

        
        
