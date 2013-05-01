rem Convert gui2py to Python 3.x (on windows)

hg revert -a
python setup.py bdist_wininst --plat-name=win32
python setup.py bdist_wininst --plat-name=win-amd64
