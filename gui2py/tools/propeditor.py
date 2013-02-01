import sys, time, math, os, os.path

import wx
_ = wx.GetTranslation
import wx.propgrid as wxpg

class TestPanel( wx.Panel ):

    def __init__( self, parent, obj, log ):
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

        from gui2py.components import InitSpec, StyleSpec, Spec, EventSpec
        appended = set()
        self.obj = obj
        for i, (cat, class_) in enumerate((('Init Specs', InitSpec), 
                                         ('Style Specs', StyleSpec), 
                                         ('Basic Specs', Spec),
                                         ('Events', EventSpec))): 
            
            pg.Append(wxpg.PropertyCategory("%s - %s" % (i+1, cat)))
            specs = sorted(obj._meta.specs.items(), key=lambda it: it[0])
            for name, spec in specs:
                print spec, class_, spec.type
                if isinstance(spec, class_):
                    prop = {'string': wxpg.StringProperty,
                            'integer': wxpg.IntProperty,
                            'float': wxpg.FloatProperty,
                            'boolean': wxpg.BoolProperty,
                            'text': wxpg.LongStringProperty,
                            'code': wxpg.LongStringProperty,
                            #'font': wxpg.FontProperty,
                            'colour': wxpg.ColourProperty}.get(spec.type)
                    if prop and name not in appended:
                        value = getattr(obj, name)
                        if spec.type == "code" and value is None:
                            value = "" 
                        pg.Append(prop(name, value=value))
                        if spec.type == "boolean":
                            pg.SetPropertyAttribute(name, "UseCheckbox", True)
                        appended.add(name)
                            
                   # pg.Append(  )
                   # pg.Append( wxpg.IntProperty("Int",value=100) )
                   # pg.Append( wxpg.FloatProperty("Float",value=100.0) )
                    #pg.Append( wxpg.BoolProperty("Bool",value=True) )
                    #pg.Append( wxpg.BoolProperty("Bool_with_Checkbox",value=True) )
                    #pg.SetPropertyAttribute("Bool_with_Checkbox", "UseCheckbox", True)

                    #pg.Append( wxpg.PropertyCategory("2 - More Properties") )
                    #pg.Append( wxpg.LongStringProperty("LongString",
                    #    value="This is a\\nmulti-line string\\nwith\\ttabs\\nmixed\\tin."))
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

        topsizer.Add(pg, 1, wx.EXPAND)

        panel.SetSizer(topsizer)
        topsizer.SetSizeHints(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def OnPropGridChange(self, event):
        p = event.GetProperty()
        if p:
            self.log.write('%s changed to "%s"\n' % (p.GetName(),p.GetValueAsString()))
            setattr(self.obj, p.GetName(), p.GetValue())

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

    def OnPropGridPageChange(self, event):
        index = self.pg.GetSelectedPage()
        self.log.write('Page Changed to \'%s\'\n' % (self.pg.GetPageName(index)))



if __name__ == '__main__':
    import sys,os
    app = wx.App()
    f = wx.Frame(None)
    
    from gui2py.controls import Button
    frame = wx.Frame(None)
    b = Button(frame, name="btnTest", label="click me!", default=True)
    frame.Show()

    log = sys.stdout
    w = TestPanel(f, b, log)
    f.Show()
    app.MainLoop()

