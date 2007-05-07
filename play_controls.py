#!/usr/bin/python
#
#Justin Tulloss
#
#
"""Module to display play controls"""

import gtk
import cairo
from cairo_help import *

class play_controls(gtk.EventBox):

	_hbox = gtk.HBox(True)
	_bgcolor = 0x334466
	def __init__(self):
		super(play_controls, self).__init__()

		#connect to various signals
		self.connect("expose_event", self.expose)
		
		#push icons on
		self._backButton = gtk.Image()
		self._playButton = gtk.Image()
		self._nextButton = gtk.Image()

		#TODO: Get rid of hardcoded paths
		self._backButton.set_from_file("icons/Back_nohover.png")
		self._playButton.set_from_file("icons/Play_nohover.png")
		self._nextButton.set_from_file("icons/Next_nohover.png")

		#Setup our hbox
		self.add(self._hbox)
		self._hbox.pack_start(self._backButton, padding=5)
		self._hbox.pack_start(self._playButton, padding=5)
		self._hbox.pack_start(self._nextButton, padding=5)

		self.set_visible_window(False)

	def expose(self, widget, event):
		cr = widget.window.cairo_create()
		cr.rectangle(event.area.x, event.area.y,
            event.area.width, event.area.height)
		cr.clip()

		rect=self.get_allocation()
		draw_bg_gradient(cr, self._bgcolor, rect)
		
if __name__ == "__main__":
	w = gtk.Window()
	pc = play_controls()
	w.add(pc)

	w.show_all()

	gtk.main()
		
