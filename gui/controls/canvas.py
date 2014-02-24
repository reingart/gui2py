#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's basic Image control (uses wx.StaticBitmap)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2014- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's BitmapCanvas component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)

import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from ..graphic import Bitmap
from .. import images

try:
    import Image
    # necessary to avoid name collision with Image class
    from Image import fromstring
    PIL_FOUND = True
except ImportError:
    PIL_FOUND = False

try:
    from Numeric import ArrayType
    NUMERIC_FOUND = True
except ImportError:
    NUMERIC_FOUND = False


# are NOR and NAND descriptions reversed?!
# double-check wxWidgets docs and/or wxPython source again
LogicalCopyModes = {
        "AND"           : wx.AND,           # src AND dst
        "AND_INVERT"    : wx.AND_INVERT,    # (NOT src) AND dst
        "AND_REVERSE"   : wx.AND_REVERSE,   # src AND (NOT dst)
        "CLEAR"         : wx.CLEAR,         # 0
        "COPY"          : wx.COPY,          # src
        "EQUIV"         : wx.EQUIV,         # (NOT src) XOR dst
        "INVERT"        : wx.INVERT,        # NOT dst
        "NAND"          : wx.NAND,          # (NOT src) OR (NOT dst)
        "NOR"           : wx.NOR,           # (NOT src) AND (NOT dst)
        "NO_OP"         : wx.NO_OP,         # dst
        "OR"            : wx.OR,            # src OR dst
        "OR_INVERT"     : wx.OR_INVERT,     # (NOT src) OR dst
        "OR_REVERSE"    : wx.OR_REVERSE,    # src OR (NOT dst)
        "SET"           : wx.SET,           # 1
        "SRC_INVERT"    : wx.SRC_INVERT,    # NOT src
        "XOR"           : wx.XOR,           # src XOR dst
        }

BrushFillStyleList = {
        "TRANSPARENT"    : wx.TRANSPARENT,
        "SOLID"          : wx.SOLID,
        "BDIAGONAL_HATCH": wx.BDIAGONAL_HATCH,
        "CROSSDIAG_HATCH" : wx.CROSSDIAG_HATCH,
        "FDIAGONAL_HATCH": wx.FDIAGONAL_HATCH,
        "CROSS_HATCH"     : wx.CROSS_HATCH,
        "HORIZONTAL_HATCH": wx.HORIZONTAL_HATCH,
        "VERTICAL_HATCH"  : wx.VERTICAL_HATCH
        }

class Canvas(Control):
    """
    A double-bufferd bitmap drawing area.
    """

    _wx_class = wx.Window
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.image
        
    def __init__(self, parent=None, **kwargs):
        self.auto_refresh = True
        self._drawing_in_progress = False
        self._buf_image = None
        
        self._size = kwargs['size']
        # create offscreen buffer where drawing occurs
        bitmap = wx.EmptyBitmap(self._size[0], self._size[1])
        self._buf_image = wx.MemoryDC()
        self._buf_image.SelectObject(bitmap)
        del bitmap

        Control.__init__(
            self,
            parent,
            **kwargs 
            )

        self._size = self.wx_obj.GetClientSize()
        
        self.wx_obj.Bind(wx.EVT_PAINT, self._OnPaint)
        self.wx_obj.Bind(wx.EVT_SIZE, self._OnSize)
        self.wx_obj.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroy)

        self.backgroundColor = (255, 255, 255)  # 'white'
        self.clear()
        self._set_fgcolor((0,0,0))       # 'black'
        # these are the defaults for a new MemoryDC
        self._fill_color = 'WHITE'
        self._fill_mode = 'SOLID'
        self._logical_copy_mode = 'COPY'


    def _OnDestroy(self, event):
        # memory leak cleanup
        self._buf_image = None
        self._pen_color = None
        self._pen = None
        event.Skip()

    def _get_logical_copy_mode(self):
        return self._logical_copy_mode
        
    def _set_logical_copy_mode(self, logical_copy_mode):
        if logical_copy_mode:
            self._buf_image.SetLogicalFunction(LogicalCopyModes[logical_copy_mode.upper()])

    def _get_bgcolor(self):
        if self._buf_image is not None:
            brush = self._buf_image.GetBackground()
            return brush.GetColour()

    def _set_bgcolor(self, color):
        color = self._get_default_color(color)
        if self._buf_image is not None and color:
            brush = self._buf_image.GetBackground()
            brush.SetColour(color)
            self._buf_image.SetBackground(brush)

    def _get_fill_color(self):
        return self._fill_color

    def _set_fill_color(self, color):
        aColor = self._get_default_color(color)
        if self._buf_image is not None and color:
            # KEA 2004-03-01
            # updated to work with wxPython 2.4.x
            # and wxPython 2.5.x
            # need to double-check other places copies of pen and brush
            # are manipulated in the rest of the framework and samples!!!
            nb = wx.Brush(color)
            ob = self._buf_image.GetBrush()
            if ob.Ok():
                nb.SetStyle(ob.GetStyle())
                s = ob.GetStipple()
                if s.Ok():
                    nb.SetStipple(s)
            self._buf_image.SetBrush(nb)

    def _get_fill_mode(self):
        return self._fill_mode

    def _set_fill_mode(self, fill_style):
        brush = self._buf_image.GetBrush()
        if fill_style:
            brush.SetStyle(BrushFillStyleList[fill_style.upper()])
            self._buf_image.SetBrush(brush)            

    def _get_fgcolor(self):
        return self._pen_color

    def _set_fgcolor(self, color):
        color = self._get_default_color(color)
        self._pen_color = color
        #self._pen.SetCap(wx.CAP_PROJECTING)
        if self._buf_image is not None and color:
            self._pen = wx.Pen(self._pen_color, self._thickness, wx.SOLID)
            self._buf_image.SetPen(self._pen)
            self._buf_image.SetTextForeground(self._pen_color)

    def _get_thickness(self):
        return self._thickness

    def _set_thickness(self, thickness):
        self._thickness = thickness
        if self._buf_image is not None and thickness and self._pen_color:
            self._pen = wx.Pen(self._pen_color, self._thickness, wx.SOLID)
            self._buf_image.SetPen(self._pen)
        else:
            self._pen = None

    def _get_font(self):
        if self._font is None:
            desc = font.fontDescription(self.wx_obj.GetFont())
            self._font = font.Font(desc)
        return self._font

    def _set_font(self, font):
        if isinstance(font, dict):
            font = font.Font(font, parent=self)
        elif font is not None: # Bind the font to this widget.
            font._parent = self
        self._font = font
        if font:
            self._buf_image.SetFont(font.get_wx_font())


    # when we Blit to the "window", we're actually blitting to the
    # offscreen bitmap and then that is blitted onscreen in the same
    # operation
    def blit(self, destXY, widthHeight, source, srcXY,
             logicalFunc=wx.COPY, useMask=False): #, xsrcMask=-1, ysrcMask=-1):
        self._buf_image.BlitPointSize(destXY, widthHeight, source, srcXY,
                            logicalFunc, useMask) #, xsrcMask, ysrcMask)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def clear(self):
        self._buf_image.Clear()
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    # this is poorly named, it should be DrawAxis
    def draw_axis(self, xy):
        self._buf_image.CrossHairPoint(xy)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_arc(self, x1y1, x2y2, xcyc):
        """
        Draws an arc of a circle, centered on (xc, yc), with starting
        point (x1, y1) and ending at (x2, y2). The current pen is used
        for the outline and the current brush for filling the shape.

        The arc is drawn in an anticlockwise direction from the start
        point to the end point.
        """

        self._buf_image.DrawArcPoint(x1y1, x2y2, xcyc)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    # doesn't exist in wxMemoryDC
    #def DrawCheckMark(self, xy, widthHeight):
    #    self._buf_image.DrawCheckMark(xy, widthHeight)
    #    if self.auto_refresh: self.refresh()

    def draw_bitmap(self, aBitmap, xy=(0, 0), transparency=1):
        if isinstance(aBitmap, graphic.Bitmap):
            bmp = aBitmap.getBits()
        elif isinstance(aBitmap, wx.Bitmap):
            bmp = aBitmap            
        elif isinstance(aBitmap, wx.Image):
            bmp = wx.BitmapFromImage(aBitmap)
        elif PIL_FOUND and isinstance(aBitmap, Image.Image):
            bmp = wx.BitmapFromImage(graphic.PILToImage(aBitmap))
        elif NUMERIC_FOUND and isinstance(aBitmap, ArrayType):
            bmp = wx.BitmapFromImage(graphic.numericArrayToImage(aBitmap))
        else:
            return

        self._buf_image.DrawBitmapPoint(bmp, xy, transparency)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_bitmap_scaled(self, aBitmap, xy, size, transparency=1):
        if isinstance(aBitmap, graphic.Bitmap):
            img = wx.ImageFromBitmap(aBitmap.getBits())
        elif isinstance(aBitmap, wx.Bitmap):
            img = wx.ImageFromBitmap(aBitmap)
        elif isinstance(aBitmap, wx.Image):
            img = aBitmap
        elif PIL_FOUND and isinstance(aBitmap, Image.Image):
            img = graphic.PILToImage(aBitmap)
        elif NUMERIC_FOUND and isinstance(aBitmap, ArrayType):
            img = graphic.numericArrayToImage(aBitmap)
        else:
            return

        bmp = wx.BitmapFromImage(img.Scale(size[0], size[1]))
        self._buf_image.DrawBitmapPoint(bmp, xy, transparency)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_circle(self, xy, radius):
        self._buf_image.DrawCirclePoint(xy, radius)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_ellipse(self, xy, widthHeight):
        self._buf_image.DrawEllipsePointSize(xy, widthHeight)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_elliptic_arc(self, xy, widthHeight, startEnd):
        self._buf_image.DrawEllipticArcPointSize(xy, widthHeight, startEnd)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_icon(self, aIcon, xy):
        self._buf_image.DrawIconPoint(aIcon, xy)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_line(self, startXY, endXY):
        self._buf_image.DrawLinePoint(startXY, endXY)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_lines(self, pointsList):
        self._buf_image.DrawLines(pointsList)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_point(self, xy):
        self._buf_image.DrawPointPoint(xy)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_polygon(self, pointsList):
        self._buf_image.DrawPolygon(pointsList)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_rectangle(self, xy, widthHeight):
        self._buf_image.DrawRectanglePointSize(xy, widthHeight)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_point_list(self, points, pens=None):
        self._buf_image.DrawPointList(points, pens)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    # KEA 2003-03-14
    # need to add other DrawXXXList methods once we are
    # requiring wxPython 2.4.0.6 or higher
    def draw_rectangle_list(self, rects, pens=None, brushes=None):
        self._buf_image.DrawRectangleList(rects, pens, brushes)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_rotated_text(self, aString, xy, angle):
        self._buf_image.DrawRotatedTextPoint(aString, xy, angle)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_rounded_rectangle(self, xy, widthHeight, radius):
        self._buf_image.DrawRoundedRectanglePointSize(xy, widthHeight, radius)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_spline(self, pointsList):
        self._buf_image.DrawSpline(pointsList)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_line_list(self, lines, pens=None):
        self._buf_image.DrawLineList(lines, pens)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def draw_text(self, aString, xy):
        self._buf_image.DrawTextPoint(aString, xy)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    # KEA 2002-03-31 this doesn't seem to work
    def flood_fill(self, xy, colour, style=wx.FLOOD_SURFACE):
        self._buf_image.FloodFillPoint(xy, colour, style)
        if self.auto_refresh:
            dc = wx.ClientDC(self.wx_obj)
            dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))

    def get_pixel(self, xy):
        return self._buf_image.GetPixelPoint(xy)

    def get_text_extent(self, aString):
        return self._buf_image.GetTextExtent(aString)

    def get_full_text_extent(self, aString):
        return self._buf_image.GetFullTextExtent(aString)

    def refresh(self, enableAutoRefresh=False):
        if enableAutoRefresh:
            self.auto_refresh = True
        dc = wx.ClientDC(self.wx_obj)
        dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))
        # KEA 2005-03-26
        # this is necessary to force a screen update on the Mac
        if wx.Platform == '__WXMAC__':
            #self.canvas.Refresh()
            self.wx_obj.Update()

    def _OnPaint(self, evt):
        #starttime = time.time()
        rect = self.wx_obj.GetUpdateRegion().GetBox()
        #print "OnPaint", rect
        dc = wx.PaintDC(self.wx_obj)
        #dc.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))
        dc.BlitPointSize((rect[0], rect[1]), (rect[2], rect[3]), self._buf_image, (rect[0], rect[1]))
        #stoptime = time.time()
        #elapsed = stoptime - starttime
        #print "OnPaint time: %f seconds" % (elapsed)

    def resize_buffer(self, size):
        brush = self._buf_image.GetBackground()
        bitmap = wx.EmptyBitmap(size[0], size[1])
        _buf_image = wx.MemoryDC()
        _buf_image.SelectObject(bitmap)
        del bitmap
        _buf_image.SetBackground(brush)
        _buf_image.SetPen(self._pen)
        aWxFont = self._getFont()._getFont()
        _buf_image.SetFont(aWxFont)
        _buf_image.SetTextForeground(self._pen_color)
        _buf_image.Clear()
        _buf_image.BlitPointSize((0, 0), (self._size[0], self._size[1]), self._buf_image, (0, 0))
        
        self._size = size

        #self._buf_image.SelectObject(wx.NullBitmap)
        self._buf_image = _buf_image

    # need to copy the old bitmap
    # before resizing
    # plus the various pen attributes
    # there is probably a memory leak in the code below
    def _OnSize(self, evt):
        size = self.wx_obj.GetClientSizeTuple()
        #print "OnSize", size, self._size
        if size == (0, 0) or not self._pen.GetColour().Ok():
            evt.Skip()
            return

        try:
            # in case self._buf_image hasn't been initialized
            brush = self._buf_image.GetBackground()
        except:
            evt.Skip()
            return

        # KEA 2002-03-30
        # only resize the offscreen bitmap when the onscreen window gets
        # larger than the offscreen bitmap
        #minX = min(size[0], self._size[0])
        #minY = min(size[1], self._size[1])
        maxX = max(size[0], self._size[0])
        maxY = max(size[1], self._size[1])
        #print minX, minY, maxX, maxY
        if (self._size[0] < maxX) or (self._size[1] < maxY):
            self.resize_buffer((maxX, maxY))
            evt.Skip()

    def get_bitmap(self, xy=(0, 0), widthHeight=(-1, -1)):
        w, h = self.wx_obj.GetClientSizeTuple()
        if widthHeight[0] != -1:
            w = widthHeight[0]
        if widthHeight[1] != -1:
            h = widthHeight[1]
        memory = wx.MemoryDC()
        bitmap = wx.EmptyBitmap(w, h)
        memory.SelectObject(bitmap)
        memory.BlitPointSize((0, 0), (w, h), self._buf_image, xy)
        memory.SelectObject(wx.NullBitmap)
        return bitmap

    bgcolor = Spec(_get_bgcolor, _set_bgcolor, type='colour')
    fill_color = Spec(_get_fill_color, _set_fill_color)
    fill_mode = Spec(_get_fill_mode, _set_fill_mode)
    font = Spec(_get_font, _set_font)
    fgcolor = Spec(_get_fgcolor, _set_fgcolor, type='colour')
    logical_copy_mode = Spec(_get_logical_copy_mode, _set_logical_copy_mode)
    thickness = Spec(_get_thickness, _set_thickness, default=1, type="integer")


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)    
    c = Canvas(frame, name='canvas', size=(30,30))
    c.draw_line((10, 10), (20, 20))
    c.onmousemove = "print 'moving...'"
    frame.Show()
    app.MainLoop()
