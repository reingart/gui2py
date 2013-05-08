#!/usr/bin/env python
# By R.Suzi rnd@onego.ru
# Extended and expanded by Andy Todd <andy47@halfcooked.com>
# Simplified & adapted for gui2py by Mariano Reingart <reingart@gmail.com>

"""
This script is setup.py of the gui2py package.

You need to have wxPython to run gui2py
"""

WIN_DEFAULT_COMMAND = "install"
APPLICATION_NAME = "gui2py"

from distutils.core import setup
import os, sys

# get the package version (add py3k if needed)
import gui
version = gui.__version__
if sys.version_info > (3, ):
    version += "-py3k"
else:
    version += "-py2x"

# append install on windows
if len(sys.argv) == 1 and sys.platform.startswith("win"):
    sys.argv.append(WIN_DEFAULT_COMMAND)

setup(name=APPLICATION_NAME, 
      version=version,
      description="gui2py framework",
      author="Mariano Reingart",
      author_email="reingart@gmail.com",
      url='http://code.google.com/p/gui2py',
      download_url="http://gui2py.googlecode.com/files/gui2py-%s.zip" % gui.__version__,
      classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: MacOS X",
        "Environment :: MacOS X :: Carbon",
        "Environment :: MacOS X :: Cocoa",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: GTK",
        #"Framework :: web2py",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development",
        "Topic :: Software Development :: User Interfaces",
      ],
      long_description = \
            "gui2py is a GUI framework for building cross-platform " \
            "\"visual\" desktop applications on Windows, Mac OS X, and Linux," \
            " using the Python language and the wxPython toolkit.",
      platforms = "Mac OS X, Windows, Linux",
      packages=['gui', 'gui.tools', 'gui.controls', 'gui.windows', 'gui.html'],
      #package_dir={'gui': 'gui', 'gui.tools': 'gui/tools'},
      #scripts=["install-pythoncard.py"],
      license="LGPLv3",
     )

# End of setup.py
