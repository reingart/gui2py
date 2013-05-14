rem Convert gui2py to Python 3.x (on windows) and generate the installers

rem hg revert -a
rem py3k.bat
del dist\*.*
c:\python33\python setup.py bdist_wininst --plat-name=win32
c:\python33\python setup.py bdist_wininst --plat-name=win-amd64
