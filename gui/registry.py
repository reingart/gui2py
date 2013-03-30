#!/usr/bin/python
# -*- coding: utf-8 -*-

"Maintains a regstry of the components that have been loaded into the system"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"

# Initial implementation was inspired on PythonCard's registry module, altought
# it was almost completely discarded and re-written from scratch
# Note: Singleton and similar classes where just removed
   
CONTROLS = {}
HTML = {}       # tags
WINDOWS = {}
MENU = {}
MISC = {}

ALL = []      # used to keep registration order for toolbox and avoid duplicates

# TODO: register_type html tags / input types
