import sys, time, math, os, os.path

import wx
_ = wx.GetTranslation
import wx.propgrid as wxpg

from gui.component import InitSpec, StyleSpec, Spec, EventSpec, DimensionSpec
from gui.font import Font

DEBUG = False

class PropertyEditorPanel(wx.Panel):

    def __init__( self, parent, log ):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.log = log

        self.panel = panel = wx.Panel(self, wx.ID_ANY)
        topsizer = wx.BoxSizer(wx.VERTICAL)

        # Difference between using PropertyGridManager vs PropertyGrid is that
        # the manager supports multiple pages and a description box.
        self.pg = pg = wxpg.PropertyGrid(panel,
                        style=wxpg.PG_SPLITTER_AUTO_CENTER |
                              wxpg.PG_AUTO_SORT |
                              wxpg.PG_TOOLBAR)

        # Show help as tooltips
        pg.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)

        pg.Bind( wxpg.EVT_PG_CHANGED, self.OnPropGridChange )
        pg.Bind( wxpg.EVT_PG_PAGE_CHANGED, self.OnPropGridPageChange )
        pg.Bind( wxpg.EVT_PG_SELECTED, self.OnPropGridSelect )
        pg.Bind( wxpg.EVT_PG_RIGHT_CLICK, self.OnPropGridRightClick )

        ##pg.AddPage( "Page 1 - Testing All" )
        # store the property grid for future reference
        self.pg = pg
        
        # load empty object (just draws categories)
        self.load_object(None)
        
        # sizing stuff:        
        topsizer.Add(pg, 1, wx.EXPAND)
        panel.SetSizer(topsizer)
        topsizer.SetSizeHints(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def load_object(self, obj):
        pg = self.pg    # get the property grid reference
        
        # delete all properties
        pg.Clear()
        
        # clean references and aux structures
        appended = set()
        self.obj = obj
        self.groups = {}
        
        # loop on specs and append each property (categorized):
        for i, cat, class_ in ((1, 'Init Specs', InitSpec), 
                               (2, 'Dimension Specs', DimensionSpec),
                               (3, 'Style Specs', StyleSpec), 
                               (5, 'Events', EventSpec),
                               (4, 'Basic Specs', Spec),
                              ): 
            
            pg.Append(wxpg.PropertyCategory("%s - %s" % (i, cat)))
            if obj is None:
                continue
            specs = sorted(obj._meta.specs.items(), key=lambda it: it[0])
            for name, spec in specs:
                if DEBUG: print "setting prop", spec, class_, spec.type
                if isinstance(spec, class_):
                    prop = {'string': wxpg.StringProperty,
                            'integer': wxpg.IntProperty,
                            'float': wxpg.FloatProperty,
                            'boolean': wxpg.BoolProperty,
                            'text': wxpg.LongStringProperty,
                            'code': wxpg.LongStringProperty,
                            'enum': wxpg.EnumProperty,
                            'edit_enum': wxpg.EditEnumProperty,
                            'array': wxpg.ArrayStringProperty,
                            'font': wxpg.FontProperty,
                            'image_file': wxpg.ImageFileProperty,
                            'colour': wxpg.ColourProperty}.get(spec.type)
                    if prop and name not in appended:
                        value = getattr(obj, name)
                        if DEBUG: print "name", name, value
                        if spec.type == "code" and value is None:
                            value = "" 
                        if spec.type == "boolean" and value is None:
                            value = False
                        if spec.type == "integer" and value is None:
                            value = -1
                        if spec.type == "font":
                            if value is None:
                                value = wx.NullFont
                            else:
                                value = value.get_wx_font()
                        if callable(value):
                            # event binded at runtime cannot be modified:
                            value = str(value)
                            readonly = True
                        else:
                            readonly = False
                        if spec.type == "enum":
                            prop = prop(name, name, 
                                           spec.mapping.keys(), 
                                           spec.mapping.values(),
                                           value=spec.mapping[value])
                        elif spec.type == "edit_enum":
                            prop = prop(name, name, 
                                           spec.mapping.keys(), 
                                           range(len(spec.mapping.values())),
                                           value=spec.mapping[value])
                        else:
                            try:
                                prop = prop(name, value=value)
                            except Exception, e:
                                print "CANNOT LOAD PROPERTY", name, value, e
                        
                        prop.SetPyClientData(spec)
                        
                        if spec.group is None:
                            pg.Append(prop)
                            if readonly:
                                pg.SetPropertyReadOnly(prop)
                        else:
                            if spec.group in self.groups:
                                prop_parent = self.groups[spec.group]
                            else:
                                prop_parent = wxpg.StringProperty(spec.group,
                                        value="<composed>")
                                self.groups[spec.group] = prop_parent
                                pg.Append(prop_parent)
                                pg.SetPropertyReadOnly(spec.group)
                            pg.AppendIn(spec.group, prop)
                            pg.Collapse(spec.group)
                                          
                        if spec.type == "boolean":
                            pg.SetPropertyAttribute(name, "UseCheckbox", True)
                        doc = spec.__doc__ 
                        if doc:
                            pg.SetPropertyHelpString(name, doc)
                        appended.add(name)

    def edit(self, name=""):
        "Programatically select a (default) property to start editing it"
        # for more info see DoSelectAndEdit in propgrid.cpp
        for name in (name, "label", "text", "title", "filename", "name"):        
            prop = self.pg.GetPropertyByName(name)
            if prop is not None:
                break
        self.Parent.SetFocus()
        self.Parent.Raise()
        self.pg.SetFocus()
        # give time to the ui to show the prop grid and set focus:
        wx.CallLater(250, self.select, prop.GetName())

    def select(self, name, flags=0):
        "Select a property (and start the editor)"
        # do not call this directly from another window, use edit() instead
        # // wxPropertyGrid::DoSelectProperty flags (selFlags) -see propgrid.h-
        wxPG_SEL_FOCUS=0x0001  # Focuses to created editor
        wxPG_SEL_FORCE=0x0002  # Forces deletion and recreation of editor
        flags |= wxPG_SEL_FOCUS # | wxPG_SEL_FORCE
        prop = self.pg.GetPropertyByName(name)
        self.pg.SelectProperty(prop, flags)
        print "selected!"
    
    def OnPropGridChange(self, event):
        p = event.GetProperty()
        print "change!", p
        if p:
            name = p.GetName()
            spec = p.GetPyClientData()
            if spec and 'enum' in spec.type:
                value = p.GetValueAsString()
            else:
                value = p.GetValue()
            #self.log.write(u'%s changed to "%s"\n' % (p,p.GetValueAsString()))
            # if it a property child (parent.child), extract its name
            if "." in name:
                group, name = name.split(".")
            if not name in self.groups:                
                if name == 'font':  # TODO: detect property type
                    # create a gui font from the wx.Font
                    font = Font()
                    font.set_wx_font(value)
                    value = font
                # re-create the wx_object with the new property value
                # (this is required at least to apply new styles and init specs)
                if DEBUG: print "changed", self.obj.name
                kwargs = {str(name): value}
                wx.CallAfter(self.obj.rebuild,  **kwargs)

    def OnPropGridSelect(self, event):
        p = event.GetProperty()
        if p:
            self.log.write(u'%s selected\n' % (event.GetProperty().GetName()))
        else:
            self.log.write(u'Nothing selected\n')

    def OnDeleteProperty(self, event):
        p = self.pg.GetSelectedProperty()
        if p:
            self.pg.DeleteProperty(p)
        else:
            wx.MessageBox("First select a property to delete")

    def OnReserved(self, event):
        pass

    def OnPropGridRightClick(self, event):
        p = event.GetProperty()
        if p:
            self.log.write(u'%s right clicked\n' % (event.GetProperty().GetName()))
        else:
            self.log.write(u'Nothing right clicked\n')
        #self.obj.get_parent().Refresh()

    def OnPropGridPageChange(self, event):
        index = self.pg.GetSelectedPage()
        self.log.write('Page Changed to \'%s\'\n' % (self.pg.GetPageName(index)))



if __name__ == '__main__':
    import sys,os
    app = wx.App()
    f = wx.Frame(None)
    
    from gui.controls import Button, Label, TextBox, CheckBox, ListBox, ComboBox
    frame = wx.Frame(None)
    #o = Button(frame, name="btnTest", label="click me!", default=True)
    #o = Label(frame, name="lblTest", alignment="right", size=(-1, 500), text="hello!")
    o = TextBox(frame, name="txtTest", border=False, text="hello world!")
    #o = CheckBox(frame, name="chkTest", border='none', label="Check me!")
    #o = ListBox(frame, name="lstTest", border='none', 
    #            items={'datum1': 'a', 'datum2':'b', 'datum3':'c'},
    #            multiselect="--multiselect" in sys.argv)
    #o = ComboBox(frame, name="cboTest",
    #            items={'datum1': 'a', 'datum2':'b', 'datum3':'c'},
    #            readonly='--readonly' in sys.argv,
    #            )
    frame.Show()

    log = sys.stdout
    w = PropertyEditorPanel(f, log)
    w.load_object(o)
    f.Show()
    app.MainLoop()

