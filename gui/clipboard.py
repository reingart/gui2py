#!/usr/bin/python
# -*- coding: utf-8 -*-

"Clipboard access functions"

import wx

def get_data():
    "Read from the clipboard content, return a suitable object (string or bitmap)"
    data = None
    try:
        if wx.TheClipboard.Open():
            if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                do = wx.TextDataObject()
                wx.TheClipboard.GetData(do)
                data = do.GetText()
            elif wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_BITMAP)):
                do = wx.BitmapDataObject()
                wx.TheClipboard.GetData(do)
                data = do.GetBitmap()
            wx.TheClipboard.Close()
    except:
        data = None
    return data


def set_data(data):
    "Write content to the clipboard, data can be either a string or a bitmap" 
    try:
        if wx.TheClipboard.Open():
            if isinstance(data, (str, unicode)):
                do = wx.TextDataObject()
                do.SetText(data)
                wx.TheClipboard.SetData(do)
            elif isinstance(data, wx.Bitmap):
                do = wx.BitmapDataObject()
                do.SetBitmap(data)
                wx.TheClipboard.SetData(do)
            wx.TheClipboard.Close()
    except:
        pass

if __name__ == "__main__":
    app = wx.App(redirect=False)
    set_data("hello world!")
    assert get_data() == "hello world!"

