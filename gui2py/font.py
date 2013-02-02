
import wx


# KEA 2004-04-15
# have to subclass Python object base class so that property() works below
class Font(object):

    def __init__(self, parent=None, **kwargs ) :
        self._parent = parent
        self._family = ''
        self._face = ''
        self._size = wx.NORMAL_FONT.GetPointSize()
        self._style = wx.NORMAL
        self._weight = wx.NORMAL
        self.underline = False
        for name, value in kwargs.items():
            setattr(self, name, value) 

    def get_wx_font(self):
        return wx.Font(self._size,
                      self._family,
                      self._style,
                      self._weight,
                      self.underline,
                      self._face)

    def set_wx_font(self, aFont):
        raise AttributeError("font attribute is read-only")

    def _get_size(self):
        return self._size

    def _set_size(self, size):
        #self._font = self._newFont()
        #self._font.SetPointSize(size)
        self._size = size

    def _get_style(self):
        if self._style == wx.ITALIC:
            return 'italic'
        elif self._style == wx.SLANT:
            return 'slant'
        else:
            return 'regular'

    def _set_style(self, name):
        if name.endswith('italic'):
            self._style = wx.ITALIC
        elif name.endswith('slant'):
            self._style = wx.SLANT
        else:
            self._style = wx.NORMAL

    def _get_face(self):
        return self._face

    def _set_face(self, face):
        self._face = face

    def _get_family(self):
        if self._family == wx.ROMAN:
            return 'serif'
        elif self._family == wx.SWISS:
            return 'sans serif'
        elif self._family == wx.MODERN:
            return 'monospace'
        else:
            return ""

    def _set_family(self, name):
        if name == 'serif':
            self._family = wx.ROMAN
        elif name == 'sans serif':
            self._family = wx.SWISS
        elif name == 'monospace':
            self._family = wx.MODERN
        else:
            self._family = wx.DEFAULT

    def _set_weight(self, name):
        if name.startswith('bold'):
            self._weight = wx.BOLD
        elif name.startswith('light'):
            self._weight = wx.LIGHT
        else:
            self._weight = wx.NORMAL

    def _get_weight(self):
        if self._weight == wx.BOLD:
            return 'bold'
        elif self._weight == wx.LIGHT:
            return 'light'
        else:
            return 'normal'


    def description(self):
        desc = {}
        if self._family != '':
            desc['family'] = self._family
        if self._face != '':
            desc['face'] = self._face
        desc['size'] = self._size
        if self._style != wx.NORMAL:
            desc['style'] = self.style
        if self._weight != wx.NORMAL:
            desc['style'] = self.weight
        return desc

    def __repr__(self):
        return str(self.description())

    face = property(_get_face, _set_face)
    family = property(_get_family, _set_family)
    size = property(_get_size, _set_size)
    style = property(_get_style, _set_style)
    weight = property(_get_weight, _set_weight)

if __name__ == "__main__":
    # basic test until unit_tests
    app = wx.App(redirect=False)
    #frame = wx.Frame(None)
    f = Font(family="serif", style="italic", weight="bold")
    assert f.family=="serif"
    assert f.style=="italic"
    assert f.weight=="bold"
    print f.get_wx_font()

