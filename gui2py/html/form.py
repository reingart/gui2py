import wx
import wx.html


from . import GetParam

FormSubmitEventType = wx.NewEventType()

EVT_FORM_SUBMIT = wx.PyEventBinder(FormSubmitEventType)

class FormSubmitEvent(wx.PyEvent):
    """
        Event indication a form was submitted.
        form is the form object being submitted
        args is a dict of form arguments
    """
    def __init__(self, form, args):
        wx.PyEvent.__init__(self)
        self.SetEventType(FormSubmitEventType)
        self.form = form
        self.args = args
    
class HTMLForm(object):
    def __init__(self, tag, container):
        self.container = container
        self.fields = []
        self.action = GetParam(tag, "ACTION", default=None)
        self.method = GetParam(tag, "METHOD", "GET")
        if self.method not in ("GET", "POST"):
            self.method = "GET"
            
    def hit_submit_button(self):
        from . import input
        for field in self.fields:
            if isinstance(field, input.SubmitButton):
                field.OnClick(None)
                return
                
    def submit(self, btn=None):
        args = self.create_arguments()
        if btn and btn.name:
            args[btn.name] = btn.name
        evt = FormSubmitEvent(self, args)
        self.container.ProcessEvent(evt)
        
    def create_arguments(self):
        args = {}
        for field in self.fields:
            if field.name:# and field.enabled: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                val = field.get_value()
                if val is None:
                    continue
                elif isinstance(val, unicode):
                    # web2py string processing
                    # requires utf-8 encoded text
                    val = val.encode("utf-8")                    
                args[field.name] = val
        return args



class FormTagHandler(wx.html.HtmlWinTagHandler):
    typeregister = {}

    # static inner form tag attribute names
    attributes = ["href", "value", "class", "onclick",
                  "type", "name", "id", "src", "action",
                  "method"]
    
    @classmethod
    def register_type(klass, type, control_class):
        klass.typeregister[type] = control_class
    
    def __init__(self):
        self.form = None
        self.control_padding = 2    # this should be disabled inside tables
        wx.html.HtmlWinTagHandler.__init__(self)
    
    def GetSupportedTags(self):
        return "FORM,INPUT,TEXTAREA,SELECT,OPTION,LABEL"
        
    def HandleTag(self, tag):
        try:
            handler = getattr(self, "Handle"+tag.GetName().upper())
            return handler(tag)
        except:
            import traceback
            traceback.print_exc()
        
    def HandleFORM(self, tag):
        self.form = HTMLForm(tag, self.GetParser().GetWindowInterface().GetHTMLWindow())
        # to use the current container (same line) do:
        ##self.cell = self.GetParser().GetContainer()
        # to create a sibling container (same level) current one must be closed:
        ##self.GetParser().CloseContainer()
        # create a new child container (if current was not closed):
        self.cell = self.GetParser().OpenContainer()
        # experimental highlight (to view final layout), sadly BR resets this
        self.GetParser().SetActualColor("gray")
        self.GetParser().GetContainer().InsertCell(wx.html.HtmlColourCell("gray"))
        # Alignment does not work here (BR fault), so it is set in create_control
        ##self.cell.SetAlignVer(wx.html.HTML_ALIGN_TOP)
        self.ParseInner(tag)
        self.GetParser().CloseContainer()
        # OpenContainer and CloseContainer calls should be the same quantity
        ##self.GetParser().OpenContainer()
        self.form = None
        self.option_list = []
        return True
    
    def HandleINPUT(self, tag):
        if tag.HasParam("type"):
            ttype = tag.GetParam("type").upper()
        else:
            ttype = "TEXT"
        klass = self.typeregister[ttype]
        self.create_control(klass, tag)
        return False
        
    def HandleTEXTAREA(self, tag):
        klass = self.typeregister["TEXTAREA"]
        self.create_control(klass, tag)
        #Don't actually call ParseInner, but lie and said we did.
        #This should skip us ahead to the next tag, and let us 
        #retrieve the text verbatem from the text area
        return True
    
    def HandleSELECT(self, tag):
        if tag.HasParam("MULTIPLE"):
            pass
        from .select import SingleSelectControl
        self.option_list = []
        #gather any/all nested options
        self.ParseInner(tag)
        self.create_control(SingleSelectControl, tag,
                            option_list=self.option_list,)
        self.option_list = []
        return True
        
    def HandleOPTION(self, tag):
        self.option_list.append(tag)
        return True
    
    def HandleLABEL(self, tag):
        klass = self.typeregister["LABEL"]
        self.create_control(klass, tag)
        #Don't actually call ParseInner, but lie and said we did.
        #This should skip us ahead to the next tag, and let us 
        #retrieve the text verbatem from the text area
        return True
    
    def create_control(self, klass, tag, **kwargs):
        parent = self.GetParser().GetWindowInterface().GetHTMLWindow()
        # create a panel for sizing:
        panel = wx.Panel(parent)
        # instantiate the actual control:
        control = klass(panel, self.form, tag, self.GetParser(), **kwargs)
        if hasattr(control, "wx_obj"):
            object = control.wx_obj
        else:
            object = control  # remove!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.setObjectTag(object, tag)
        # if it isn't a window (i.e. OPTION), do not add it to the html cell
        if not isinstance(object, wx.Window):
            return
        # create a sizer to fit the control with some padding
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(object, 1, wx.ALL, self.control_padding)
        panel.SetSizer(box)
        panel.Fit()
        # get floatwidth
        if tag.HasParam("WIDTH"):
            w = tag.GetParam("WIDTH")
            if w[-1] == '%':
                w = int(w[:-1], 0)
            else:
                w = int(w)
        else:
            w = -1
        cell = self.GetParser().GetContainer()
        # middle-align controls (affects the whole line, up to the FORM)
        cell.SetAlignVer(wx.html.HTML_ALIGN_CENTER)
        # if no float width, don't use -1 as it seems to break layout
        if w > 0:
            wcell = wx.html.HtmlWidgetCell(panel, w)   # w should be int!
        else:
            wcell = wx.html.HtmlWidgetCell(panel)
        cell.InsertCell(wcell)

    def setObjectTag(self, object, tag):
        """ Add a tag attribute to the wx window """
        object._attributes = {}
        object._name = tag.GetName().lower()
        for name in self.attributes:
            object._attributes["_%s" % name] = tag.GetParam(name)
            if object._attributes["_%s" % name] == "":
                object._attributes["_%s" % name] = None

        
wx.html.HtmlWinParser_AddTagHandler(FormTagHandler)


