#!/usr/bin/python
#
#Justin Tulloss
#

"""Emits signals to GTK to allow for processing of WiiMote events"""

import gtk
gtk.gdk.threads_init()
import gobject
import cwiidpy
from cwiidpy import cwiid


class gtkWiimote(gtk.Widget):

    __gsignals__=dict(acc_event=(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                      (gobject.TYPE_INT, gobject.TYPE_INT,gobject.TYPE_INT))
                      )

    def __init__(self):
        super(gtkWiimote, self).__init__()
        self._mote = cwiidpy.cwiid(self.cwiidCallback)

    def cwiidCallback(self, id, mesgs):
        #Loop through each message
        for msg in mesgs:
            if msg[0] == cwiidpy.MESG_ACC:
                self.emit("acc_event", msg[1]["x"], msg[1]["y"], msg[1]["z"])


if __name__ == "__main__":

    def acc_callback(widget, x, y, z):
        print x,y,z

    window = gtk.Window()
    test = gtkWiimote()
    window.add(test)
    test.connect("acc_event", acc_callback)
    #window.show_all()

    gtk.main()

