#!/usr/bin/python
# -*- coding: utf-8 -*-

"Sample gui2py application using a resource & controller (skeleton)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"
__license__ = "LGPL 3.0"


import gui


class MyController(gui.Controller):

    def on_load(self, evt):
        print "initializing!"
        self.component['mypanel']['mybutton'].label = "Click ME!!!!"
        self.component.show()
    
    def on_menu_file_about_click(self, event):
        pass
    
    def on_menu_file_exit_click(self, evt):
        self.component.close()
        
    def on_field1_change(self, evt):
        print "Changed, new text: ", self.component['field1'].value

    def on_field1_keypress(self, evt):
        print "Keypress: ", evt.key
        if evt.key == 13:
            gui.alert(self.component['field1'].value, "hello world!")
        
    def on_mypanel_mybutton_click(self, etv):
        gui.alert("btn clicked!!!!")
        

if __name__ == '__main__':
    c = MyController()
    gui.main_loop()

