# -*- coding: utf-8 -*-
#
# gui2py documentation build configuration file, created by
# Txema Vicente <txema@nabla.net>
#

import os
import sys
import time
import datetime
import pprint

_PrettyPrinter = pprint.PrettyPrinter(indent=4)
def pretty(text):
    _PrettyPrinter.pprint(text)
    return _PrettyPrinter.pformat(text)

# patched extensions base path.
sys.path.insert(0, os.path.abspath('.'))
from ext.sphinx_mod import EventDocumenter, find_modules

# gui base path.
_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
print "Searching %s" % _path
sys.path.insert(0, _path)

try:
    import gui    
except:
    print "ERROR: gui2py not found"
    sys.exit(1)

print "Generating gui2py %s Documentation" % "alpha"#(gui.version)


# Do not try to import these modules
skip_modules = {"gui": {
                     "gui": ["samples"],
                     "gui.doc": None
                     }
               }


# Skip members
def skip_member(member, obj):
    #module = obj.__name__
    #if "gui.hidden" in module: return True
    if member.startswith("XXX"): return True
    return False

autosummary_generate = True

sys.skip_member = skip_member

for mod in skip_modules.keys():
    sys.all_submodules = find_modules(os.path.join(_path, mod),
                                         skip_modules[mod])

pretty(sys.all_submodules)

extensions = ['sphinx.ext.autodoc',
              'ext.autosummary',
              'sphinx.ext.inheritance_diagram', 
              'sphinx.ext.todo',
              #'sphinx.ext.viewcode',
              ]

inheritance_graph_attrs = dict(rankdir="TB", size='""')

autodoc_member_order='groupwise'
templates_path = ['_templates']
source_suffix = '.txt'
master_doc = 'index'
project = u'gui2py'
copyright = u'2013, Mariano Reingart'
version = '0.1'
release = "alpha" #gui.version
exclude_patterns = ['_build', '_templates']
add_module_names = False
pygments_style = 'sphinx'
modindex_common_prefix = ['gui.']
html_theme = 'default'
html_theme_path = ["ext/theme"]
html_title = "gui version %s" % "alpha" #(gui.version)
html_short_title = "gui v. %s " % "alpha" #(gui.version)
html_favicon = 'favicon.ico'
html_static_path = ['_static']
html_domain_indices = True
html_use_index = True
html_split_index = True
html_show_sourcelink = False
htmlhelp_basename = 'guidoc'
latex_elements = {}
latex_documents = [
  ('index', 'gui.tex', u'gui2py Documentation',
   u'Mariano Reingart', 'manual'),
]
man_pages = [
    ('index', 'gui', u'gui2py Documentation',
     [u'Mariano Reingart'], 1)
]

texinfo_documents = [
  ('index', 'gui', u'gui2py Documentation',
   u'Mariano Reingart', 'gui', 'One line description of project.',
   'Miscellaneous'),
]


# Generated contents

now = datetime.datetime.fromtimestamp(time.time())
with open('build.rst', 'w') as f:
    f.write(".. list-table::\n")
    f.write("   :widths: 50 50\n")
    f.write("\n")
    for var, val in (("Date", now.strftime("%Y/%m/%d %H:%M:%S")),
                     ("gui version", "alpha")):
        f.write("   * - "+var+"\n     - "+val+"\n")

