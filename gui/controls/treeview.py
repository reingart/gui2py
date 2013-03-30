#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Tree Model-View-Controller control (uses wx.TreeCtrl)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's Tree component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)
# Note: pythoncard version was trivial, Model and View code are completely new

import wx
from ..event import TreeEvent
from ..component import Control, SubComponent
from ..spec import Spec, EventSpec, InitSpec, StyleSpec, InternalSpec
from .listbox import ItemContainerControl
from .. import images 
from types import TupleType, ListType, StringTypes, NoneType, IntType, DictType


class TreeView(Control):
    "A tree (wx.TreeCtrl)"

    _wx_class = wx.TreeCtrl
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.tree_ctrl

    def __init__(self, parent=None, **kwargs):
        # default sane values (if not init'ed previously):
        if not hasattr(self, "_items"):
            self._max_columns = 99
        Control.__init__(self, parent, **kwargs)

    # Emulate some listBox methods

    def clear(self):
        self._items.clear()

    def get_selected_items(self):
        return [it for it in self.nodes if it.selected]
 
    def _get_items(self):
        return self._items

    def _set_items(self, model=None):
        if model is None:
            model = TreeModel(self)
        elif not isinstance(model, (TreeModel, )):
            raise AttributeError("unsupported type, TreeMoel expected")
        else:
            # TODO: rebuild the wx tree items
            pass

        self._items = model

    has_buttons = StyleSpec(wx.TR_HAS_BUTTONS, 
                doc="Show + and - buttons to the left of parent items.")
    no_lines = StyleSpec(wx.TR_NO_LINES, 
                doc="Hide vertical level connectors")
    row_lines = StyleSpec(wx.TR_ROW_LINES, 
                doc="Draw a contrasting border between displayed rows.")
    multiselect = StyleSpec(wx.TR_MULTIPLE, 
                default=True, doc="Allow multiple selection")
    hide_root = StyleSpec(wx.TR_HIDE_ROOT, default=False,
                        doc="Suppress the display of the root node")
    default_style = StyleSpec(wx.TR_DEFAULT_STYLE, 
                doc="Closest to the defaults for the native control")    
    
    items = InternalSpec(_get_items, _set_items)
   
    # events:
    onitemselected = EventSpec('item_selected', 
                           binding=wx.EVT_TREE_SEL_CHANGED, kind=TreeEvent)
    onitemactivated = EventSpec('item_activated', 
                           binding=wx.EVT_TREE_ITEM_ACTIVATED, kind=TreeEvent)
    onitemcollapsed = EventSpec('item_collapsed', 
                           binding=wx.EVT_TREE_ITEM_COLLAPSED, kind=TreeEvent)
    onitemcollapsing = EventSpec('item_collapsing', 
                           binding=wx.EVT_TREE_ITEM_COLLAPSING, kind=TreeEvent)
    onitemexpanded = EventSpec('item_expanded', 
                           binding=wx.EVT_TREE_ITEM_EXPANDED, kind=TreeEvent)
    onitemexpanding = EventSpec('list_expanding', 
                           binding=wx.EVT_TREE_ITEM_EXPANDING, kind=TreeEvent)



class TreeModel(dict):
    "TreeView Items (nodes) model map {wx item data: TreeItem}"
    
    def __init__(self, _tree_view):
        self._tree_view = _tree_view
        self.clear()

    def __setitem__(self, key, kwargs):
        self.add(key, kwargs)

    def add(self, parent=None, text="", key=None):

        if key is None:
            key = self._new_key()

        # create the wx item
        if parent is None:
            wx_item = self._tree_view.wx_obj.AddRoot(text)
        else:
            wx_item = self._tree_view.wx_obj.AppendItem(parent.wx_item, text)

        # associate the key so we can look for it in the future (ie, __iter__)
        data = wx.TreeItemData(key)
        self._tree_view.wx_obj.SetItemData(wx_item, data)

        # create the new item 
        item = TreeItem(self, key, wx_item, parent)
        dict.__setitem__(self, key, item)   # add the key/value to the dict

        return item

    def __delitem__(self, it):
        dict.__delitem__(self, it)
        self._tree_view.wx_obj.DeleteItem(it)

    def __call__(self, wx_item=None):
        "Look for a item based on the wx_item or return a key/value pair"
        if wx_item is not None:
            key = self._tree_view.wx_obj.GetPyData(wx_item)
            return self[key]
        else:
            return self.items()  # shortcut!
                
    def __iter__(self):
        "Return a iterable for all the nodes"
        # This is not really useful except to perform global actions
        # (i.e., reseting the selection of all items)
        # use TreeItem.__iter__ to browse the nodes hierarchy
        return self.itervalues()

    def clear(self):
        "Remove all items and reset internal structures"
        dict.clear(self)
        self._key = 0
        if hasattr(self._tree_view, "wx_obj"):
            self._tree_view.wx_obj.DeleteAllItems()

    def _new_key(self):
        "Create a unique key for this list control (currently: just a counter)"
        self._key += 1
        return self._key


class TreeItem(object):
    "Represents a item node in the TreeModel"

    def __init__(self, _tree_model, key, wx_item, parent_node):
        self._tree_model = _tree_model
        self.key = key                      # key used in model
        self.parent = parent_node
        self.wx_item = wx_item              # TreeItemId returned by Add/Append

    def _get_text(self):
        return self._tree_model._tree_view.wx_obj.GetItemText(self.wx_item)

    def _set_text(self, new_text):
        return self._tree_model._tree_view.wx_obj.SetItemText(self.wx_item, new_text)
    
    text = property(_get_text, _set_text, doc="Get or change the item label")
       
    def _is_selected(self):
        return self._tree_model._tree_view.wx_obj.IsSelected(self.wx_item)
    
    def _select(self, on):
        self._tree_model._tree_view.wx_obj.SelectItem(self.wx_item, on)

    selected = property(_is_selected, _select)

    def ensure_visible(self):
        self._tree_model._tree_view.wx_obj.EnsureVisible(self.wx_item)
        
    def focus(self):
        self._tree_model._tree_view.wx_obj.SetFocusedItem(self.wx_item)

    def get_children_count(self):
        return self._tree_model._tree_view.wx_obj.GetChildrenCount(self.wx_item)
    
    def set_has_children(self, has_children=True):
        "Force appearance of the button next to the item"
        # This is useful to allow the user to expand the items which don't have
        # any children now, but instead adding them only when needed, thus 
        # minimizing memory usage and loading time.
        self._tree_model._tree_view.wx_obj.SetItemHasChildren(self.wx_item, 
                                                              has_children)

    def __iter__(self):
        "look for children and convert them to TreeItem if any"
        tree = self._tree_model._tree_view.wx_obj
        wx_item, cookie = tree.GetFirstChild(self.wx_item)
        if wx_item.IsOk():
            key = tree.GetPyData(wx_item)
            yield self._tree_model[key]
            while True:
                wx_item, cookie = tree.GetNextChild(self.wx_item, cookie)
                if not wx_item.IsOk():
                    break
                key = tree.GetPyData(wx_item)
                yield self._tree_model[key]



if __name__ == "__main__":
    import sys
    # basic test until unit_test
    import gui
    app = wx.App(redirect=False)    
    w = gui.Window(title="hello world", name="frmTest", tool_window=False, 
               resizable=True, visible=False, pos=(180, 0))
    tv = TreeView(w, name="treeview", has_buttons=True, default_style=True)

    root = tv.items.add(text="Root")
    child1 = tv.items.add(parent=root, text="Child 1")
    child2 = tv.items.add(parent=root, text="Child 2")
    child3 = tv.items.add(parent=root, text="Child 3")
    child11 = tv.items.add(parent=child1, text="Child 11")
    child11.ensure_visible()
    child2.set_has_children()

    def expand_item(event):
        "lazy evaluation example: virtually add children at runtime"
        if not event.detail.get_children_count():
            for i in range(5):
                it = tv.items.add(parent=event.detail, text="lazy child %s" % i)
                it.set_has_children()  # allow to lazy expand this child too
            
    # assign some event handlers:
    tv.onitemexpanding = expand_item
    tv.onitemselected = "print 'selected TreeItem:', event.detail.text"
    w.show()
    
    # basic tests:
    
    # iterate on the root node:
    for i, nodx in enumerate(root):
        assert nodx.text == "Child %s" % (i + 1)
        nodx.text = "hello %s" % i
        assert nodx.text == "hello %s" % i
        if i == 0:
            assert nodx.get_children_count() == 1
    
    assert root.get_children_count() == 4
    
    from gui.tools.inspector import InspectorTool
    InspectorTool().show(w)
    app.MainLoop()

