import sys, time, math, os, os.path

import wx
_ = wx.GetTranslation
import wx.propgrid as wxpg

from gui2py.components import InitSpec, StyleSpec, Spec, EventSpec, DimensionSpec
from gui2py.font import Font

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
                            'array': wxpg.ArrayStringProperty,
                            'font': wxpg.FontProperty,
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
                        if spec.type == "font" and value is not None:
                            value = value.get_wx_font()
                        if callable(value):
                            # event binded at runtime cannot be modified:
                            value = "<function %s>" % value.func_name
                            readonly = True
                        else:
                            readonly = False
                        if spec.type == "enum":
                            prop = prop(name, name, 
                                           spec.mapping.keys(), 
                                           spec.mapping.values())
                        else:
                            prop = prop(name, value=value)
                        
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
                            

                    #pg.Append( wxpg.PropertyCategory("2 - More Properties") )
                    #pg.Append( wxpg.DirProperty("Dir",value="C:\\Windows") )
                    #pg.Append( wxpg.FileProperty("File",value="C:\\Windows\\system.ini") )
                    #pg.Append( wxpg.ArrayStringProperty("ArrayString",value=['A','B','C']) )

                #pg.Append( wxpg.EnumProperty("Enum","Enum",
                #                             ['wxPython Rules',
                #                              'wxPython Rocks',
                #                             'wxPython Is The Best'],
                #                             [10,11,12],
                #                             0) )
                #pg.Append( wxpg.EditEnumProperty("EditEnum","EditEnumProperty",
                #                                 ['A','B','C'],
                #                                 [0,1,2],
                #                                 "Text Not in List") )

                #pg.Append( wxpg.PropertyCategory("3 - Advanced Properties") )
                #pg.Append( wxpg.DateProperty("Date",value=wx.DateTime_Now()) )
                #pg.Append( wxpg.FontProperty("Font",value=panel.GetFont()) )
                #pg.Append( wxpg.ColourProperty("Colour",
                ##                               value=panel.GetBackgroundColour()) )
                #pg.Append( wxpg.SystemColourProperty("SystemColour") )
                #pg.Append( wxpg.ImageFileProperty("ImageFile") )
                #pg.Append( wxpg.MultiChoiceProperty("MultiChoice",
                #            choices=['wxWidgets','QT','GTK+']) )

                #pg.Append( wxpg.PropertyCategory("4 - Additional Properties") )
                #pg.Append( wxpg.IntProperty("IntWithSpin",value=256) )
                #pg.SetPropertyEditor("IntWithSpin","SpinCtrl")

                #pg.SetPropertyAttribute( "File", wxpg.PG_FILE_SHOW_FULL_PATH, 0 )
                #pg.SetPropertyAttribute( "File", wxpg.PG_FILE_INITIAL_PATH,
                ##                         "C:\\Program Files\\Internet Explorer" )
                #pg.SetPropertyAttribute( "Date", wxpg.PG_DATE_PICKER_STYLE,
                #                         wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )

                #pg.Append( wxpg.ImageFileProperty("ImageFileWithLargeEditor") )

        # When page is added, it will become the target page for AutoFill
        # calls (and for other property insertion methods as well)
        ##pg.AddPage( "Page 2 - Results of AutoFill will appear here" )


    def OnPropGridChange(self, event):
        p = event.GetProperty()
        if p:
            name = p.GetName()
            value = p.GetValue()
            self.log.write('%s changed to "%s"\n' % (p,p.GetValueAsString()))
            # if it a property child (parent.child), extract its name
            if "." in name:
                group, name = name.split(".")
            if not name in self.groups:                
                if name == 'font':  # TODO: detect property type
                    # create a gui2py font from the wx.Font
                    font = Font()
                    font.set_wx_font(value)
                    value = font
                # re-create the wx_object with the new property value
                # (this is required at least to apply new styles and init specs)
                print "changed", self.obj.name
                if isinstance(self.obj.wx_obj, wx.Window):
                    print "window!"
                    kwargs = {str(name): value}
                    wx.CallAfter(self.obj.__init__,  **kwargs)
                else:
                    print "menu!"
                    # menues and other abstract objects no need rebuild
                    wx.CallAfter(setattr, self.obj, name, value)

    def OnPropGridSelect(self, event):
        p = event.GetProperty()
        if p:
            self.log.write('%s selected\n' % (event.GetProperty().GetName()))
        else:
            self.log.write('Nothing selected\n')

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
            self.log.write('%s right clicked\n' % (event.GetProperty().GetName()))
        else:
            self.log.write('Nothing right clicked\n')
        #self.obj.get_parent().Refresh()

    def OnPropGridPageChange(self, event):
        index = self.pg.GetSelectedPage()
        self.log.write('Page Changed to \'%s\'\n' % (self.pg.GetPageName(index)))



if __name__ == '__main__':
    import sys,os
    app = wx.App()
    f = wx.Frame(None)
    
    from gui2py.controls import Button, Label, TextBox, CheckBox, ListBox, ComboBox
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

