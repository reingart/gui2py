

import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from ..graphic import Bitmap
from .. import images 


USE_GENERIC = False ## wx.Platform == '__WXGTK__'

if USE_GENERIC:
    from wx.lib.statbmp import GenStaticBitmap as StaticBitmap
else:
    StaticBitmap = wx.StaticBitmap
        

class Image(Control):
    "A static image."

    _wx_class = StaticBitmap
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.image


    def __init__(self, parent=None, **kwargs):
        # set safe default for construction (if designer is not rebuilding!)
        if not hasattr(self, "_filename"):
            self._auto_size = self._stretch = None
            self._filename = kwargs.get('filename')
            # do not create bitmap if no filename is given
            if self._filename:
                self._size = kwargs.get('size', (-1, -1))
                self._bitmap = Bitmap(filename=self._filename, size=self._size)
            else:
                self._bitmap = None

        if 'auto_size' in kwargs and kwargs['auto_size'] and self._bitmap:
            self._auto_size = kwargs['auto_size']
            kwargs['width'] = self._bitmap.get_width()
            kwargs['height'] = self._bitmap.get_height()
        
        if 'stretch' in kwargs:
            _stretch = kwargs['stretch']
            del kwargs['stretch']
        else:
            _stretch = None
        
        ##if kwargs['border'] == 'transparent':
        ##    mask = wx.MaskColour(self._bitmap, wxBLACK)
        ##    self._bitmap.SetMask(mask)
        
        if self._bitmap:
            kwargs['bitmap'] = self._bitmap.get_bits()

        #del kwargs['label']
        Control.__init__(
            self,
            parent,
            **kwargs 
            )

        if _stretch is not None and self._bitmap:
            self.stretch = _stretch
        self.wx_obj.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroy)
        
    def _OnDestroy(self, event):
        # memory leak cleanup
        self._bitmap = None
        event.Skip()

    # KEA added getBitmap, setBitmap
    def _get_bitmap(self):
        return self._bitmap

    def _set_bitmap(self, bmp):
        self._bitmap = bmp
        self.wx_obj.SetBitmap(bmp.get_bits())

        # update dimension
        self.auto_size = self.auto_size
        self.stretch = self.stretch
        
        # may actually need to refresh the panel as well
        # depending on the size of the new bitmap compared
        # to the old one
        # in addition, the size of the image or imagebutton needs
        # to be set appropriately after changing the bitmap so
        # there are still a few issues to work out
        self.wx_obj.Refresh()
    
    def _set_auto_size(self, value):
        self._auto_size = value
        if value and self._bitmap:
            w = self._bitmap.get_width()
            h = self._bitmap.get_height()
            self.size = (w, h)    

    def _set_stretch(self, value):
        self._stretch = value
        if value:
            self._bitmap.rescale(*self.size)

    """
    # KEA do we query the Bitmap to find the actual dimensions
    # _size can contain -1, and -2
    # or provide a special getBitmapSize method?
    # this getSize is actually the same as its parent
    def _getSize( self ) :
        return self.GetSizeTuple()   # get the actual size, not (-1, -1)
    """

    # KEA special handling for -2 size option
    def _set_size(self, size):
        if self._bitmap:
            self._size = size or (-1, -1)
            w = self._size[0]
            if w == -2:
                w = self._bitmap.getWidth()
            h = self._size[1]
            if h == -2:
                h = self._bitmap.getHeight()
            ##print "Size", (w, h), self._name, self._filename
            Control._set_size(self, (w, h))
        elif size:
            Control._set_size(self, size)

    # KEA 2001-08-02
    # right now the image is loaded from a filename
    # during initialization
    # but later these might not make any sense
    # if setBitmap is used directly in user code
    def _get_filename( self ) :
        return self._filename

    # KEA 2001-08-14
    # if we're going to support setting the file
    # after initialization, then this will need to handle the bitmap loading
    # overhead
    def _set_filename(self, filename):
        self._filename = filename
        if filename:
            self._set_bitmap(Bitmap(filename))
        else:
            self._bitmap = None

    def _set_bgcolor(self, color):
        color = self._get_default_color(color)
        if self._filename == '':
            bmp = self._bitmap.get_bits()
            dc = wx.MemoryDC()
            dc.SelectObject(bmp)
            dc.SetBackground(wx.Brush(color))
            dc.Clear()
            dc.SelectObject(wx.NullBitmap)
        self.wx_obj.SetBackgroundColour(color)
        self.wx_obj.Refresh()   # KEA wxPython bug?

    bgcolor = Spec(Control._get_bgcolor, _set_bgcolor, type="color")
    bitmap = InitSpec(_get_bitmap, _set_bitmap, default=None)
    filename = Spec(_get_filename, _set_filename, default="", type="image_file")
    size = Spec(Control._get_size, _set_size)
    auto_size = Spec(lambda self: self._auto_size,
                     lambda self, value: self._set_auto_size(value), 
                     doc="Automatically resize to match the loaded image", 
                     default=True, type='boolean')
    stretch = Spec(lambda self: self._stretch,
                   lambda self, value: self._set_stretch(value),
                   doc="Automatically resize the image to match control", 
                   default=False, type='boolean')
    #image = 'presence' : 'optional', 'default':'' },


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    i = Image(frame, filename="splash.png", name='imgtest')
    i.onmousemove = "print 'moving...'"
    frame.Show()
    app.MainLoop()
