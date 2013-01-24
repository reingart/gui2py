#!/usr/bin/python
# -*- coding: latin-1 -*-

import wx

from gui2py.windows import HtmlWindow

search_html = """
<form method="get" action="/wiki/default/_pages"> 
	<fieldset> 
    <label>test label:</label>
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
from gluon.html import INPUT, FORM, LABEL, P, BR, SELECT, OPTION, A, CENTER, BODY, TEXTAREA, OBJECT, TAG
from gluon.validators import IS_NOT_EMPTY, IS_EXPR
from gluon.storage import Storage
from gluon import current


# web2py SQLFORM expects T in current (thread-local data) to translate messages
current.T = lambda x: x


if __name__ == '__main__':
    app = wx.App(False)
    w = HtmlWindow(None, title="test html", visible=False, resizeable=True)
    if '--login' in sys.argv:
        form = FORM(
            LABEL("Username", _width="25%"),
            INPUT(_type='text', _name='username', requires=IS_NOT_EMPTY(), _width="75%"),
            LABEL("Password", _width="25%"),
            INPUT(_type='password', _name='password', requires=IS_NOT_EMPTY(), _width="75%"),
            LABEL("Options:", _width="25%"),
            INPUT(_type='checkbox', _name='rememberme', _width="10%"),
            LABEL("Remember me", _width="65%"),
            LABEL("", _width="25%"),
            INPUT(_type='checkbox', _name='superuser', _width="10%"),
            LABEL("Log in as root", _width="65%"),
            CENTER(
                INPUT(_type='submit', _name='login', _value="Login"),
                BR(),
                A("lost password", _href="saraza"), " | ",
                A("register", _href="saraza"), ))
    elif '--form' in sys.argv:
        form = FORM(
            "hola2!", BR(),
            LABEL("hola1", _width="25%"),
            INPUT(_type='text', _name='myvar', requires=IS_NOT_EMPTY(), _width="75%"),
            LABEL("hola2", _width="25%"),
            INPUT(_type='text', _name='myvar', requires=IS_NOT_EMPTY(), _width="25%"),
            LABEL("hola2", _width="25%"),
            SELECT(OPTION("1", _value="uno"), OPTION("2", _value="dos"), 
                   OPTION("3", _value="tres"), _name='mysel', _width="25%"),
            LABEL("hola3", _width="25%"),
            INPUT(_type='text', _name='myvar', requires=IS_NOT_EMPTY(), _width="75%"),
            LABEL("Options:", _width="25%"),
            INPUT(_type='checkbox', _name='myvar', _width="10%"),
            LABEL("check1", _width="65%"),
            LABEL("", _width="25%"),
            INPUT(_type='checkbox', _name='myvar', _width="10%"),
            LABEL("check1", _width="65%"),
            LABEL("", _width="25%"),
            INPUT(_type='checkbox', _name='myvar', _width="10%"),
            LABEL("check1", _width="65%"),
            TEXTAREA("hola!", _name='mytextarea', _width="100%"),
            "hola3!",
            INPUT(_type='submit', _name='submit'),
            )
    elif '--sqlform' in sys.argv:
        form = SQLFORM.factory(
            Field("test","string", requires=IS_NOT_EMPTY(), comment="some data"),
            Field("test1","string", requires=IS_NOT_EMPTY(), comment="some data"),
            Field("test2","string", requires=IS_NOT_EMPTY(), comment="some data"),
            Field("test3","string", requires=IS_NOT_EMPTY(), comment="some data"),
            formname=None,
        )
    elif '--object' in sys.argv:
        form = OBJECT(TAG.PARAM(_name='label', _value='"test"'), 
                      TAG.PARAM(_name='name', _value='"btnTest"'),
                      _class="Button")
    else:
        raise RuntimeError("please use\npython forms_example.py --login, --form or --sqlform")
        
    form_xml = BODY(form, _text="#000000", _bgcolor="#bebec5", _link="#0000FF",
                         _vlink="#FF0000", _alink="#000088").xml()
    print form_xml
    w.html.write(form_xml)
    #<form action="" enctype="multipart/form-data" method="post"><table><tr id="no_table_test__row"><td class="w2p_fl"><label for="no_table_test" id="no_table_test__label">Test: </label></td><td class="w2p_fw"><input class="string" id="no_table_test" name="test" type="text" value="" /></td><td class="w2p_fc">some data</td></tr><tr id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw"><input type="submit" value="Submit" /></td><td class="w2p_fc"></td></tr></table></form>
    #html.SetPage(search_html)
    #html.LoadFile(r"C:\htmlt.html")

    def on_form_submit(evt):
        print "Submitting to %s via %s with args %s"% (evt.form.action, evt.form.method, evt.data)
        if form.accepts(evt.data, formname=None, keepvalues=True):
            print "accepted!"
        elif form.errors:
            print "errors", form.errors
            w.html.set_page(form.xml())
    w.html.onsubmit = on_form_submit
    if '--inspect' in sys.argv:
        import wx.lib.inspection
        wx.lib.inspection.InspectionTool().Show()

    w.show()
    app.MainLoop()
