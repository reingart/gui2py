import wx
from ..event import FormEvent
from ..widget import Widget, Spec, EventSpec, new_id


class TextBox(Widget):
    "A text field"

    def __init__(self, parent, alignment=None, border=None, password=False,
                 multiline=False, hscroll=False , **kwargs):
        # required read-only specs:
        style = 0
        self._border = border or self._meta.specs['border'].default
        self._password = password
        self._multiline = multiline
        self._hscroll = hscroll
        if self._border == 'none':
            style |= wx.NO_BORDER
        if password:
            style |= wx.TE_PASSWORD
        if multiline:
            style |= wx.TE_MULTILINE
            if hscroll:
                style |= wx.HSCROLL
            
        self._alignment = alignment or self._meta.specs['alignment'].default

        self.wx_obj = wx.TextCtrl(
            parent, 
            new_id(kwargs.get('id')),
            #style = wxTE_PROCESS_ENTER | borderStyle | wxCLIP_SIBLINGS,
            style = style | self._mapAlignment(self._alignment) | \
                wx.CLIP_SIBLINGS | wx.NO_FULL_REPAINT_ON_RESIZE,
            name = kwargs.get('name'))

        Widget.__init__(self, **kwargs)

        if self._border == 'none':
            # the erase background event doesn't appear to make the control
            # transparent, so further investigation is required
            #EVT_ERASE_BACKGROUND(delegate, lambda evt: None)
            self.wx_obj.SetBackgroundColour(parent.GetBackgroundColour())

    def _mapAlignment(self, aString):
        if aString == 'left':
            return wx.TE_LEFT
        elif aString == 'center':
            return wx.TE_CENTRE
        elif aString == 'right':
            return wx.TE_RIGHT
        else :
            raise ValueError('invalid TextBox.alignment value: %s' % aString)
        
    def _getAlignment(self):
        return self._alignment

    def clear_selection(self):
        if self.can_cut():
            # delete the current selection,
            # if we can't do a Cut we shouldn't be able to delete either
            # which is why i used the test above
            sel = self.replace_selection('')
        else:
            ins = self.get_insertion_point()
            try:
                self.replace(ins, ins + 1, '')
            except:
                pass

    # KEA the methods for retrieving and manipulating the text
    # has to be greatly expanded to match wxPython
    # capabilities or more


    # KEA new methods to mirror wxPython wxTextCtrl capabilities
    def append_text( self, aString ) :
        """Appends the text to the end of the text widget.
        After the text is appended, the insertion point will be at the end
        of the text widget. If this behavior is not desired, the programmer
        should use getInsertionPoint and setInsertionPoint."""
        self.wx_obj.AppendText( aString )

    def can_copy( self ) :
        return self.wx_obj.CanCopy()

    def can_cut( self ) :
        return self.wx_obj.CanCut()

    def can_paste( self ) :
        return self.wx_obj.CanPaste()

    def can_redo( self ) :
        return self.wx_obj.CanRedo()

    def can_undo( self ) :
        return self.wx_obj.CanUndo()

    def clear( self ) :
        self.wx_obj.Clear()

    def copy( self ) :
        self.wx_obj.Copy()

    def cut( self ) :
        self.wx_obj.Cut()

    def discard_edits( self ) :
        self.wx_obj.DiscardEdits()
    
    def get_insertion_point( self ) :
        return self.wx_obj.GetInsertionPoint()

    def get_last_position( self ) :
        return self.wx_obj.GetLastPosition()

    def get_line_length( self, aLineNumber ) :
        return self.wx_obj.GetLineLength( aLineNumber )

    def get_line_text( self, aLineNumber ) :
        return self.wx_obj.GetLineText( aLineNumber )

    def get_selection( self ) :
        return self.wx_obj.GetSelection()

    def get_number_of_lines( self ) :
        return self.wx_obj.GetNumberOfLines()

    # KEA rename to getModified?
    def is_modified( self ) :
        """Returns 1 if the text has been modified, 0 otherwise."""
        return self.wx_obj.IsModified()

    # KEA support LoadFile? If so, it only makes sense for TextArea
    # many of the other methods only make sense for the multiline TextArea
    # not TextField and PasswordField

    # KEA OnChar ties into our user code handlers and our events,
    # need to think about this one some more

    # KEA OnDropFiles is windows-specific, if you try and call it under *nix
    # what happens? just an exception?

    def paste( self ) :
        self.wx_obj.Paste()

    def position_to_xy(self, aPosition):
        result = self.wx_obj.PositionToXY(aPosition)
        if len(result) == 2:
            return result
        else:
            # workaround for wxPython 2.3.2.1
            return (result[1], result[2])

    def redo( self ) :
        self.wx_obj.Redo()

    def remove( self, aFrom, aTo ) :
        self.wx_obj.Remove( aFrom, aTo )

    def replace( self, aFrom, aTo, aString ) :
        # KEA workaround for Replace bug, has the side effect of
        # possibly changing the insertion point
        #self._delegate.Replace( aFrom, aTo, aString )
        i = self.wx_obj.GetInsertionPoint()
        self.wx_obj.Remove( aFrom, aTo )
        self.wx_obj.SetInsertionPoint( aFrom )
        self.wx_obj.WriteText( aString )
        self.wx_obj.SetInsertionPoint( i )

    def replace_selection(self, aString, select=0):
        sel = self.GetSelection()
        self.Remove(sel[0], sel[1])
        self.WriteText(aString)
        if select:
            self.SetSelection(sel[0], sel[0] + len(aString))

    # KEA support SaveFile?

    def set_insertion_point( self, aPosition ) :
        self.SetInsertionPoint( aPosition )

    def set_insertion_point_end( self ) :
        self.SetInsertionPointEnd()

    def set_selection( self, aFrom, aTo ) :
        self.SetSelection( aFrom, aTo )

    def show_position( self, aPosition ) :
        self.ShowPosition( aPosition )

    def undo( self ) :
        self.Undo()

    def write_text( self, aString ) :
        self.WriteText( aString )

    def xy_to_position( self, aX, aY ) :
        return self.XYToPosition( aX, aY )

    def _getBorder( self ) :
        return self._border

    get_string_selection = lambda self: self.wx_obj.GetStringSelection
    
    def get_string(self, aFrom, aTo):
        return self.GetValue()[aFrom:aTo]

    alignment = Spec(_getAlignment, default='left', values=['left', 'right', 'center'])
    border = Spec(_getBorder, default='3d', values=['3d', 'none'])
    editable = Spec(lambda self: self.wx_obj.IsEditable(), 
                    lambda self, value: self.wx_obj.SetEditable(value),
                    default=True)
    text = Spec(lambda self: self.wx_obj.GetValue(), 
                lambda self, value: self.wx_obj.SetValue(value))
    password = Spec(lambda self: self._password, default=False)
    multiline = Spec(lambda self: self._multiline, default=False)
    hscroll = Spec(lambda self: self._hscroll, default=True)

    onchange = EventSpec('change', binding=wx.EVT_TEXT, kind=FormEvent)
    

if __name__ == "__main__":
    import sys
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    t = TextBox(frame, name="txtTest", border='none', text="hello world!",
                password='--password' in sys.argv,
                multiline='--multiline' in sys.argv,
                hscroll=True,
                )
    assert t.get_parent() is frame
    assert t.name == "txtTest"
    print "align", t.alignment
    print "text", t.text
    print "password", t.password
    print "multiline", t.multiline
    print "hscroll", t.hscroll
    assert t.text == "hello world!"
    from pprint import pprint
    # assign some event handlers:
    t.onmousemove = lambda event: pprint("%s %s %s" % (event.name, event.x, event.y))
    t.onmouseleftdown = lambda event: pprint(event.target.append_text("click!"))
    t.onchange = lambda event: pprint("change: %s" % event.target.text)
    frame.Show()
    app.MainLoop()