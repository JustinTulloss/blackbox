#!/usr/bin/python
#
#
#Justin Tulloss
#
#Rubicon Settop Box View

import gtk
import radialmenuitem

def main():
    """The main function that sets up our app. Should also draw background"""
    mainWin = gtk.Window()
    
    #initialize additional widgets
    mainLayout = gtk.Layout()
    artMenuItem = radialmenuitem.RadItem()
    #Connect particular events to particular widgets
    #Add above widgets to window
    mainWin.add(artMenuItem)

    mainWin.fullscreen()
    mainWin.set_decorated(0)
    mainWin.show_all()

    gtk.main() #main loop


if __name__ == "__main__":
    main()
