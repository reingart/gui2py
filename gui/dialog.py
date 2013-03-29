#!/usr/bin/python
# -*- coding: utf-8 -*-

"Common dialogs (function wrappers for wxPython dialogs)"


import wx
from wx.lib import dialogs
from .font import Font


def alert(message, title="", parent=None, scrolled=False, icon="exclamation"):
    "Show a simple pop-up modal dialog"
    if not scrolled:
        icons = {'exclamation': wx.ICON_EXCLAMATION, 'error': wx.ICON_ERROR,
             'question': wx.ICON_QUESTION, 'info': wx.ICON_INFORMATION}
        style = wx.OK | icons[icon]
        result = dialogs.messageDialog(parent, message, title, style)
    else:
        result = dialogs.scrolledMessageDialog(parent, message, title)


def prompt(message="", title="", default="", multiline=False, password=None, 
           parent=None):
    "Modal dialog asking for an input, returns string or None if cancelled"
    if password:
        style = wx.TE_PASSWORD | wx.OK | wx.CANCEL
        result = dialogs.textEntryDialog(parent, message, title, default, style)
    elif multiline:
        style = wx.TE_MULTILINE | wx.OK | wx.CANCEL
        result = dialogs.textEntryDialog(parent, message, title, default, style)
        # workaround for Mac OS X
        result.text = '\n'.join(result.text.splitlines())
    else:
        result = dialogs.textEntryDialog(parent, message, title, default)
    if result.accepted:
        return result.text


def confirm(message="", title="", default=False, ok=False, cancel=False,
            parent=None):
    "Ask for confirmation (yes/no or ok and cancel), returns True or False"
    style = wx.CENTRE
    if ok:
        style |= wx.OK 
    else:
        style |= wx.YES | wx.NO
        if default:
            style |= wx.YES_DEFAULT
        else:
            style |= wx.NO_DEFAULT
    if cancel:
        style |= wx.CANCEL
    result = dialogs.messageDialog(parent, message, title, style)
    if cancel and result.returned == wx.ID_CANCEL:
        return None
    return result.accepted  # True or False
    

def select_font(message="", title="", font=None, parent=None):
    "Show a dialog to select a font"
    if font is not None:
        wx_font = font._get_wx_font()                   # use as default
    else:
        wx_font = None
        font = Font()                                   # create an empty font
    result = dialogs.fontDialog(parent, font=wx_font)
    if result.accepted:
        font_data = result.fontData
        result.color = result.fontData.GetColour().Get()
        wx_font = result.fontData.GetChosenFont()
        font.set_wx_font(wx_font)
        wx_font = None
        return font


def select_color(message="", title="", color=None, parent=None):
    "Show a dialog to pick a color"
    result = dialogs.colorDialog(parent, color=color)
    return result.accepted and result.color


def open_file(title="Open",  directory='', filename='', 
              wildcard='All Files (*.*)|*.*', multiple=False, parent=None):
    "Show a dialog to select files to open, return path(s) if accepted"
    style = wx.OPEN 
    if multiple:
        style |= wx.MULTIPLE
    result = dialogs.fileDialog(parent, title, directory, filename, wildcard, 
                                style)
    return result.paths


def save_file(title="Save",  directory='', filename='', 
              wildcard='All Files (*.*)|*.*', overwrite=False, parent=None):
    "Show a dialog to select file to save, return path(s) if accepted"
    style = wx.SAVE 
    if not overwrite:
        style |= wx.OVERWRITE_PROMPT
    result = dialogs.fileDialog(parent, title, directory, filename, wildcard, 
                                style)
    return result.paths


def choose_directory(message='Choose a directory', path="", parent=None):
    "Show a dialog to choose a directory"
    result = dialogs.directoryDialog(parent, message, path)
    return result.path


def single_choice(options=[], message='', title='', parent=None):
    result = dialogs.singleChoiceDialog(parent, message, title, options)
    return result.selection


def multiple_choice(options=[], message='', title='', parent=None):
    result = dialogs.multipleChoiceDialog(parent, message, title, options)
    return result.selection


def find(default='', whole_words=0, case_sensitive=0, parent=None):
    "Shows a find text dialog"
    result = dialogs.findDialog(parent, default, whole_words, case_sensitive)
    return {'text': result.searchText, 'whole_words': result.wholeWordsOnly,
            'case_sensitive': result.caseSensitive}


if __name__ == "__main__":
    app = wx.App(redirect=False)
    
    alert("hola!", "Alert!", icon="error")
    text = prompt("Input your name:", "Prompt...", "mariano")
    print text
    ok = confirm("do you agree?", "Confirm?", default=True, cancel=True)
    print ok
    font = select_font("Select a font!")
    print font
    color = select_color("Pick a color")
    print color
    print open_file()
    print save_file(overwrite=True)
    print choose_directory()
    print single_choice(["1", 'b', '$'])
    print multiple_choice(["1", 'b', '$'])
    print find("hola")
    
