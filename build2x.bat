rem generate the installers (windows)

rem hg revert -a
del dist\*.*
python setup.py bdist_wininst --plat-name=win32
python setup.py bdist_wininst --plat-name=win-amd64
