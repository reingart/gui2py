#----------------------------------------------------------------------------
# Name:         flowsizer.py
# Purpose:      Implements a Flow Sizer
#
# Author:       Peter Damoc (peter at gmail.com)
#               
# Created:      January 2006
# Version:      0.1 
# Licence:      wxWindows license

import wx

class FlowSizer(wx.PySizer):
    def __init__(self, minHSpace=0, minVSpace=0):        
        wx.PySizer.__init__(self)
        self.snp = []
        self.minHSpace = minHSpace
        self.minVSpace = minVSpace
        
    def _calcSizeAndPos(self):
        w, h = self.GetSize()
        self.snp = []
        currentRow = [0,0]
        self.snp.append(currentRow)
        items = self.GetChildren()
        for item in items:
            mw, mh = item.CalcMin()
                
            if currentRow[0]+mw+self.minHSpace*len(currentRow) >= w:
                currentRow = [0,0]
                self.snp.append(currentRow)
            currentRow[1] = max(currentRow[1], mh)
            currentRow[0] += mw
            currentRow.append(item)
        
    def CalcMin(self):
        w, h = self.GetSize()
        w, h = w-20, h-20
        
        items = self.GetChildren()
        if not items:
            return wx.Size(10, 10)
        self._calcSizeAndPos()
        minW = 0
        for item in items:
            wi, hi = item.CalcMin()
            minW = max(minW, wi)
        minH = reduce(lambda x, y: x+y+self.minVSpace, [r[1] for r in self.snp], 2*self.minVSpace)
        return wx.Size(minW+2*self.minHSpace, minH)
        
    def RecalcSizes(self):
        curWidth, curHeight  = self.GetSize()
        px, py = self.GetPosition()
        ph = self.minVSpace
        for row in self.snp:
            aw, ah, items = row[0], row[1], row[2:]
            offw = (curWidth-aw)/(len(items)+1)
            pw = offw            
            for item in items:
                w, h = item.GetMinSize()
                self.SetItemBounds(item, px+pw, py+ph, w, h)
                pw +=w+offw
            ph += ah+self.minVSpace
            
    def SetItemBounds(self, item, x, y, w, h):
        ipt = wx.Point(x, y)
        isz = item.CalcMin()
        item.SetDimension(ipt, isz)
        
if __name__ == "__main__":
    ''' 
    Test code
    '''
    class ColorPanel(wx.Window):
        def __init__(self, parent, color):
            wx.Window.__init__(self, parent)
            self.SetBackgroundColour(color)
            self.SetSize((50,50))
            
    app = wx.App(0)
    frame = wx.Frame(None, title="FlowSizer Test")
    import  wx.lib.scrolledpanel as scrolled
    scroll = scrolled.ScrolledPanel(frame)
    sizer = FlowSizer(5, 5)
    scroll.SetSizer(sizer)
    scroll.SetAutoLayout(1)
    scroll.SetupScrolling()    
    for w in range(20):
        cp = ColorPanel(scroll, "red")
        sizer.Add(cp)
        sizer.Add(wx.Button(scroll, label="A Button"))
    
    s2 = wx.BoxSizer()
    s2.Add(scroll, 1, wx.EXPAND)
    frame.SetSizer(s2)
    
    frame.Show()
    app.MainLoop()