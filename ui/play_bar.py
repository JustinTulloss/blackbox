import gtk
import cairo
from cairo_help import *
import gobject

import signal
import os

#playback modules
import pygst
import gst

#This class shows what is playing and eventually should handle all music
#It will need to dequeue songs from the song list when it needs them
class play_bar(gtk.HBox):

	__gsignals__ = dict(song_ended=(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, () ))

	def __init__(self):
		super(play_bar, self).__init__()

		self._details = PlayDetails()
		self.pack_start(self._details)

		self.now_playing = None

		self.pipeline = gst.element_factory_make("playbin", "my-playbin")

		bus = self.pipeline.get_bus()
		bus.add_signal_watch()
		bus.connect('message', self.gst_message)

	def __del__(self):
		self.pipeline.set_state(gst.STATE_NULL)
		
	def new_decode_pad(dbin, pad, islast):
		pad.link(self.convert.get_pad("sink"))

	def play_song(self, widget, song):
		print "Playing song now..."
		self._details.song = song
		
		songurl = song.request_url()
		state = self.pipeline.get_state()
		if state >= gst.STATE_PAUSED:
			self.pipeline.set_state(gst.STATE_READY)

		self.pipeline.set_property('uri', songurl)
		self.pipeline.set_state(gst.STATE_PLAYING)

	def pause_song(self):
		self.pipeline.set_state(gst.STATE_PAUSED)
		#print "%s paused" % self._details.song.title
	
	def resume_song(self):
		self.pipeline.set_state(gst.STATE_PLAYING)
		#print "%s resumed" % self._details.song.title

	def change_song(self, song):
		songurl = song.request_url()
		self.pipeline.set_property('uri', songurl)

	def update_battery(self, percentage):
		self._details.battery = percentage

	def gst_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			gobject.idle_add(self.emit, "song_ended")
		elif t == gst.MESSAGE_ERROR:
			self.pipeline.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print "Error: %s", err, debug

class PlayDetails(gtk.DrawingArea):
	_song = {}
	_bgcolor = 0x334466
	def __init__(self):
		super(PlayDetails, self).__init__()
		#connect events
		self.connect("expose_event", self.expose)
		self._battery = 100

		#decompose bg color into cairo values (floats between 0 and 1)
		#self.set_size_request(700, 100)
	
	def set_battery(self, percentage):
		self._battery = percentage
		cr = self.window.cairo_create()
		self.draw(cr, False)

	battery = property(None, set_battery)

	def set_song(self, song):
		if song != None:
			self._song = song
		else:
			song = {}
		#redraw the info box
		cr = self.window.cairo_create()
		self.draw(cr, False)
	
	def get_song(self):
		return self._song
	
	
	song = property(lambda self: self.get_song(), lambda self, s: self.set_song(s))

	def expose(self, widget, event):
		cr = widget.window.cairo_create()

		cr.rectangle(event.area.x, event.area.y, 
			event.area.width, event.area.height)
		cr.clip()

		self.draw(cr)
	
	def draw(self, cr, draw_bg=True):
		self.draw_background(cr, draw_bg)
		#self.draw_progressbar(cr)
		self.draw_text(cr)
		self.draw_battery(cr)
	
	def draw_background(self, cr, draw_bg=True):
		rect = self.get_allocation()
		if draw_bg:
			bgcolor = cairo_color(self._bgcolor)
			cr.save()
			cr.scale(rect.width, rect.height)
			cr.rectangle(0,0, 1,1)
			bg = cairo.LinearGradient(.5, 0, .5, 1)
			bg.add_color_stop_rgba(0, bgcolor[0]+.2, bgcolor[1]+.2, bgcolor[2]+.2, 1)
			bg.add_color_stop_rgba(1, bgcolor[0], bgcolor[1], bgcolor[2], 1)
			cr.set_source(bg)
			cr.fill()
			cr.restore()


		cr.save()
		cr.scale(rect.width, rect.height)

		dispbgcolor = 0xfeffbf #TODO: Make this not hardcoded
		dbc = cairo_color(dispbgcolor)
		cr.rectangle(.1,.166,.75,.66)
		#save off this size for fonts
		self._dispcorner = cr.user_to_device(.1,.25)
		self._dispdim = cr.user_to_device_distance(.75, .5)
		cr.set_source_rgb(dbc[0], dbc[1], dbc[2])
		cr.fill()
		cr.restore()
	
	def draw_progressbar(self, cr):
		"""Draws a indicator of how long there is in the song"""

		#Our world is the yellow box
		cr.save()
		cr.translate(self._dispcorner[0], self._dispcorner[1])
		cr.rectangle(.1*self._dispdim[0], .8*self._dispdim[1],
			.8*self._dispdim[0], .2*self._dispdim[1])
		cr.set_line_width(1)
		cr.set_source_rgb(0,0,0)
		cr.stroke()
		cr.restore()
	
	def draw_text(self, cr):
		"""Draws song information in the play bar"""
		#need to square rectangle off or the fonts look funny (Stretched)
		cr.save()
		cr.translate(self._dispcorner[0], self._dispcorner[1])
		#cr.scale(min(self._dispdim), min(self._dispdim))
		#self._song = {"title": "Title", "artist":"Artist", "album": "Album"}

		#draw title
		if hasattr(self.song,"name"):
			title = self.song.name
		else:
			title = "Rubicon Music Player"

		cr.set_font_size(self._dispdim[1]/2)
		cr.select_font_face("Comic Sans MS", cairo.FONT_SLANT_NORMAL, 
			cairo.FONT_WEIGHT_NORMAL)
		x_bear, y_bear, width, theight, x_adv, y_adv = \
			cr.text_extents(title)

		cr.set_source_rgb(0,0,0)
		cr.move_to(self._dispdim[0]/2-width/2, theight)
		cr.show_text(title)
		cr.stroke()

		#draw other string
		if hasattr(self.song,"artist") and hasattr(self.song,"album"):
			infostring = self.song.artist+ " - " + self.song.album
		elif hasattr(self.song,"artist"):
			infostring = self.song.artist
		elif hasattr(self.song, "album"):
			infostring = self.song.album
		else:
			infostring = "The free, legal, user friendly music swapping software"

		cr.set_font_size(self._dispdim[1]/3)
		cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL,
			cairo.FONT_WEIGHT_NORMAL)
		x_bear, y_bear, width, oheight, x_adv, y_adv = \
			cr.text_extents(infostring)
		cr.move_to(self._dispdim[0]/2 - width/2, theight+oheight+self._dispdim[1]*.1)
		cr.show_text(infostring)
		cr.stroke()
		cr.restore()

	def draw_battery(self, cr):
		batstring = "Battery: %s%%" % self._battery
		rect = self.get_allocation()
		cr.save()
		#cr.scale(rect.width, rect.height)
		cr.set_font_size(self._dispdim[1]/3)
		cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL,
			cairo.FONT_WEIGHT_NORMAL)
		x_bear, y_bear, width, height, x_adv, y_adv = \
			cr.text_extents(batstring)
		cr.set_source_rgb(0xFF,0xFF,0xFF)
		cr.move_to(rect.width-width-5, rect.height-5)
		cr.show_text(batstring)
		cr.stroke()
		cr.restore()





if __name__ == "__main__":
	w= gtk.Window()
	w.connect("destroy", gtk.main_quit)
	p = play_bar()
	w.add(p)
	w.show_all()

	gtk.main()
