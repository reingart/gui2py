#!/usr/bin/python
# -*- coding: latin-1 -*-

import wx

from gui2py.form import EVT_FORM_SUBMIT

search_html = """
<form method="get" action="/wiki/default/_pages"> 
	<fieldset> 
	<input type="text" id="s" name="query" value="" /> 
	<input type="submit" id="x" value="Buscar" /> 
	</fieldset> 
</form> 
"""
register_html = """
<form action="" enctype="multipart/form-data" method="post"><table><tr id="auth_user_first_name__row"><td class="w2p_fl"><label for="auth_user_first_name" id="auth_user_first_name__label">Nombre: </label></td><td class="w2p_fw"><input class="string" id="auth_user_first_name" name="first_name" type="text" value="" /></td><td class="w2p_fc"></td></tr><tr id="auth_user_last_name__row"><td class="w2p_fl"><label for="auth_user_last_name" id="auth_user_last_name__label">Apellido: </label></td><td class="w2p_fw"><input class="string" id="auth_user_last_name" name="last_name" type="text" value="" /></td><td class="w2p_fc"></td></tr><tr id="auth_user_email__row"><td class="w2p_fl"><label for="auth_user_email" id="auth_user_email__label">Correo Electrónico: </label></td><td class="w2p_fw"><input class="string" id="auth_user_email" name="email" type="text" value="" /></td><td class="w2p_fc"></td></tr><tr id="auth_user_password__row"><td class="w2p_fl"><label for="auth_user_password" id="auth_user_password__label">Contraseña: </label></td><td class="w2p_fw"><input class="password" id="auth_user_password" name="password" type="password" value="" /></td><td class="w2p_fc"></td></tr><tr class="auth_user_password_two__row"><td><label>Verificar Contraseña:</label></td><td><input name="password_two" type="password" /></td><td></td></tr><tr id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw"><input type="submit" value="Enviar" /></td><td class="w2p_fc"></td></tr></table><div class="hidden"><input name="_next" type="hidden" value="/wiki/default/index" /><input name="_formkey" type="hidden" value="dcb7f9dc-ff6d-4d1c-ad6a-2af4ce324053" /><input name="_formname" type="hidden" value="register" /></div></form>
"""

import sys
sys.path.append(r"/home/reingart/web2py")
from gluon.sql import Field
from gluon.sqlhtml import SQLFORM
from gluon.html import INPUT, FORM
from gluon.validators import IS_NOT_EMPTY, IS_EXPR
from gluon.storage import Storage


if __name__ == '__main__':
    app = wx.App(False)
    f = wx.Frame(None)
    
    form = FORM(
            INPUT(_type='text', _name='myvar', requires=IS_NOT_EMPTY()),
            INPUT(_type='submit', _name='submit'),
            )
    #form = SQLFORM.factory(
    #    Field("test","string", requires=IS_NOT_EMPTY(), comment="some data"),
    #    formname=None,
    #)
    
    html = wx.html.HtmlWindow(f, style= wx.html.HW_DEFAULT_STYLE | wx.TAB_TRAVERSAL)
    form_xml = form.xml()
    print form_xml
    html.SetPage(form_xml)
    #<form action="" enctype="multipart/form-data" method="post"><table><tr id="no_table_test__row"><td class="w2p_fl"><label for="no_table_test" id="no_table_test__label">Test: </label></td><td class="w2p_fw"><input class="string" id="no_table_test" name="test" type="text" value="" /></td><td class="w2p_fc">some data</td></tr><tr id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw"><input type="submit" value="Submit" /></td><td class="w2p_fc"></td></tr></table></form>
    #html.SetPage(search_html)
    #html.LoadFile(r"C:\htmlt.html")

    def on_form_submit(evt):
        print "Submitting to %s via %s with args %s"% (evt.form.action, evt.form.method, evt.args)
        if form.accepts(evt.args, formname=None, keepvalues=True):
            print "accepted!"
        elif form.errors:
            print "errors", form.errors
            html.SetPage(form.xml())
    html.Bind(EVT_FORM_SUBMIT, on_form_submit)

    f.Show()
    app.MainLoop()
