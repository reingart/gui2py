#!/bin/sh

# Convert gui2py to Python 3.x (on GNU/Linux and Mac OS X)

2to3 -w gui
2to3  -w -x import *.pyw

