
#CallAfter
#set_timeout = wx.CallLater

# Basic events

# References
# https://developer.mozilla.org/en-US/docs/Mozilla_event_reference
# http://wxpython.org/docs/api/wx.Event-class.html

class EventHandler:
    "Generic Event Handler: maps a wx.Event to a gui2py.Event"
    
    def __init__(self, name, binding, kind):
        self.name = name                # name (type), i.e.: "click"
        self.binding = binding          # wx.Event object
        self.kind = kind                # Event class
    
    def __call__(self, wx_event):
        "Actual handler, binded and called by wxPython, returns an Event"
        return self.kind(name=self.name, wx_event=wx_event)


class Event:
    "Generic Event Object: holds actual event data (created by EventHandler)"
    
    def __init__(self, target=None, timestamp=None, name="", wx_event=None):
        self.wx_event = wx_event
        # retrieve wxPython event properties if not given
        if wx_event:
            wx_obj = self.wx_event.GetEventObject()
        if not target and wx_obj:
            target = wx_obj.reference
        if not timestamp:
            timestamp = wx_event.GetTimestamp()
        self.target = target
        self.timestamp = timestamp
        self.name = name                  # name (type), i.e.: "click"
        if wx_event:
            self.wx_event.Skip(True)      # keep event processing (default)

    def prevent_default(self):
        self.wx_event.Skip(False)

    def stop_propagation(self):
        self.wx_event.StopPropagation()


class UIEvent(Event):
    "General -window- related events (detail can hold additional data)"   
    names = ["load", "resize", "scroll", "paint", "unload"]

    def __init__(self, target=None, timestamp=None, name="", detail=None, 
                 wx_event=None):
        Event.__init__(self, target, timestamp, name, wx_event)
        self.detail = detail

    def prevent_default(self):
        if self.name == 'unload':
            if self.wx_event.CanVeto():
                self.wx_event.Veto()
            else:
                raise RuntimeError("Cannot Veto!")
        else:
            Event.prevent_default(self)     # call default implementation


class FocusEvent(Event):
    "Focus related events"
    
    names = ["focus", "blur"]


class FormEvent(Event):
    "Form HTML-like events "
    
    names = ["select", "change", "reset", "submit", "invalid"]
    

class MouseEvent(Event):
    "Mouse related events"
    
    names = ["click", "dblclick", "mousedown", "mousemove",
            "mouseout", "mouseover", "mouseup", "scroll"]

    def __init__(self, target=None, timestamp=None, name=None, 
                 screen_x=None, screen_y=None, client_x=None, client_y=None,
                 ctrl_key=None, shift_key=None, alt_key=None, meta_key=None,
                 button=None, wx_event=None):
        Event.__init__(self, target, timestamp, name, wx_event)
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.client_x = client_x
        self.client_y = client_y
        self.ctrl_key = ctrl_key
        self.shift_key = shift_key
        self.alt_key = alt_key
        self.meta_key = meta_key
        self.button = button        # 0: left, 1: center, 2: right


class KeyboardEvent(Event):
    
    names = "onkeypress", "onkeydown", "onkeyup",
    
    def __init__(self, target=None, timestamp=None, name=None, 
                 ctrl_key=None, shift_key=None, alt_key=None, meta_key=None,
                 key=None, char=None, wx_event=None):
        Event.__init__(self, target, timestamp, name, wx_event)
        self.ctrl_key = ctrl_key
        self.shift_key = shift_key
        self.alt_key = alt_key
        self.meta_key = meta_key
        self.key = key              # virtual key code value
        self.char = char            # Unicode character associated

        
class TimingEvent(Event):
    "Time interval events"   
    names = ["idle", "timer"]

    def __init__(self, target=None, timestamp=None, name=None, interval=None, 
                 wx_event=None):
        Event.__init__(self, target, timestamp, name, wx_event)
        self.interval = interval

    def request_more(self):
        pass        #wx.RequestMore(needMore=True)


WIDGET_EVENTS = MouseEvent, FocusEvent, TimingEvent
