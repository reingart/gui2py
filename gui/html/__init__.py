
import wx

__SENTINEL = object()

def GetParam(tag, param, default=__SENTINEL):
    """ Convenience function for accessing tag parameters"""
    if tag.HasParam(param):
        return tag.GetParam(param)
    else:
        if default == __SENTINEL:
            raise KeyError
        else:
            return default
            

import form as form
import input as input
import object

if __name__ == '__main__':
    app = wx.App(False)
    f = wx.Frame(None)
    
    html = wx.html.HtmlWindow(f, style= wx.html.HW_DEFAULT_STYLE | wx.TAB_TRAVERSAL)
    html.SetPage(r"<object class='Button'><param name='label' value='hola'></object>")
    
    def OnFormSubmit(evt):
        print "Submitting to %s via %s with args %s"% (evt.form.action, evt.form.method, evt.args)
    html.Bind(form.EVT_FORM_SUBMIT, OnFormSubmit)
    f.Show()
    app.MainLoop()