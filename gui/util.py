#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Graphic facilities (encapsulate wx.Bitmap and wx.Color)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart" # where applicable

# Initial implementation was copied from PythonCard's util module


import os
import sys
import imp
import re
import fnmatch

# Thomas Heller's function for determining
# if a module is running standalone
def main_is_frozen():
    if sys.platform == 'darwin':
        # this is a temporary hack for bundlebuilder
        return not (sys.executable == '/System/Library/Frameworks/Python.framework/Versions/2.3/Resources/Python.app/Contents/MacOS/Python' or \
                    sys.executable == '/Library/Frameworks/Python.framework/Versions/2.4/Resources/Python.app/Contents/MacOS/Python' or \
                    sys.executable == '/Library/Frameworks/Python.framework/Versions/2.5/Resources/Python.app/Contents/MacOS/Python')
    else:
        return (hasattr(sys, "frozen") or # new py2exe, McMillan
                hasattr(sys, "importers") # old py2exe
                or imp.is_frozen("__main__")) # tools/freeze, cx_freeze

def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])

# this is how I expected os.path.dirname to work
# it might be better to name this directoryName instead?!
def dirname(path):
    if os.path.isdir(path):
        return path
    else:
        return os.path.split(path)[0]


def get_caller_module():
    f = sys._current_frames().values()[0]
    return f.f_back.f_back.f_globals

def get_app_dir():
    return dirname(os.path.abspath(sys.argv[0]))


if __name__ == '__main__':
    print "Frozen: ", main_is_frozen()
    print "Main dir: ", get_main_dir()
    def test():
        return get_caller_module()
    print test()
    print get_app_dir()

