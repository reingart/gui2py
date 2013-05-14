rem Convert gui2py to Python 3.x (on windows)

c:\python33\tools\Scripts\2to3.py -w gui
c:\python33\tools\Scripts\2to3.py -w -x import sample.pyw
c:\python33\tools\Scripts\2to3.py -w -x import minimal.pyw
c:\python33\tools\Scripts\2to3.py -w -x import sizers.pyw

c:\python33\python.exe sample.pyw
