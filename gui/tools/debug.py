#!/usr/bin/python
# -*- coding: utf-8 -*-

"Shell, Namespace viewer and other debugging facilities"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"


# inspired byPythonCard debug module, but completely rewritten


import wx
import wx.py


TOOL_WINDOW_STYLE = wx.DEFAULT_FRAME_STYLE | wx.FRAME_NO_TASKBAR


class Shell(wx.Frame):
    
    def __init__(self, parent=None, title="shell", intro="welcome to gui2py!"):
        pos = size = None
        wx.Frame.__init__(self, parent, -1, title, pos, size, TOOL_WINDOW_STYLE)
        self.sh = wx.py.shell.Shell(self, -1, introText=intro)
        
    def show(self):
        self.Show(True)


if __name__ == '__main__':
    
    import gui
    gui.shell()
    gui.main_loop()
