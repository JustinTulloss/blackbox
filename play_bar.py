import gtk
import cairo
from cairo_help import *

#This class shows what is playing and eventually should handle all music
#It will need to dequeue songs from the song list when it needs them
class play_bar(gtk.HBox):
	def __init__(self, bg=0x000000):
		gtk.HBox.__init__(self)
		self._bgcolor = bg

		#self.pack_start(gtk.Label("Now Playing: "), False, True)
		self.pack_start(PlayDetails(self._bgcolor))

		self.now_playing = None

	def play_song(self, song):
		if(self.now_playing == None): #need to initialize
			#self.now_playing = gtk.Label()
			#self.now_playing = PlayDetails(self._bg)
			self.now_playing.show()
			#self.pack_start(self.now_playing, False, True)

		self.now_playing.set_text(song["title"])

class PlayDetails(gtk.DrawingArea):
	def __init__(self, bg):
		super(PlayDetails, self).__init__()
		#connect events
		self.connect("expose_event", self.expose)

		#decompose bg color into cairo values (floats between 0 and 1)
		self._bgcolor = cairo_color(bg)
		self.set_size_request(700, 100)
	
	def expose(self, widget, event):
		cr = widget.window.cairo_create()

		cr.rectangle(event.area.x, event.area.y, 
			event.area.width, event.area.height)
		cr.clip()

		self.draw(cr)
	
	def do_size_request(self, request):
		print "Hey"

	def draw(self, cr):
		cr.save()
		rect = self.get_allocation()
		cr.scale(rect.width, rect.height)
		
		self.draw_background(cr)
		cr.restore()
		self.draw_progressbar(cr)
		self.draw_text(cr)
	
	def draw_background(self, cr):
		bgcolor = self._bgcolor
		dispbgcolor = 0xfeffbf #TODO: Make this not hardcoded
		dbc = cairo_color(dispbgcolor)
		cr.rectangle(0,0, 1,1)
		bg = cairo.LinearGradient(.5, 0, .5, 1)
		bg.add_color_stop_rgba(0, bgcolor[0]+.2, bgcolor[1]+.2, bgcolor[2]+.2, 1)
		bg.add_color_stop_rgba(1, bgcolor[0], bgcolor[1], bgcolor[2], 1)
		cr.set_source(bg)
		cr.fill()

		cr.rectangle(.1,.166, .75,.66)
		#save off this size for fonts
		self._dispcorner = cr.user_to_device(.1,.25)
		self._dispdim = cr.user_to_device_distance(.75, .5)
		cr.set_source_rgb(dbc[0], dbc[1], dbc[2])
		cr.fill()
	
	def draw_progressbar(self, cr):
		"""Draws a indicator of how long there is in the song"""

		#Our world is the yellow box
		cr.save()
		cr.translate(self._dispcorner[0], self._dispcorner[1])
		#cr.scale(self._dispdim[0], self._dispdim[1])
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
		self._song = {"title": "Title", "artist":"Artist", "album": "Album"}

		#draw title
		cr.set_font_size(self._dispdim[1]/2)
		cr.select_font_face("Comic Sans MS", cairo.FONT_SLANT_NORMAL, 
			cairo.FONT_WEIGHT_NORMAL)#Trebuchet MS for serious
		x_bear, y_bear, width, theight, x_adv, y_adv = \
			cr.text_extents(self._song["title"])

		cr.set_source_rgb(0,0,0)
		cr.move_to(self._dispdim[0]/2-width/2, theight)
		cr.show_text(self._song["title"])
		cr.stroke()

		#draw other string
		cr.set_font_size(self._dispdim[1]/5)
		cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL,
			cairo.FONT_WEIGHT_NORMAL)
		x_bear, y_bear, width, oheight, x_adv, y_adv = \
			cr.text_extents(self._song["artist"]+" - " + self._song["album"])
		cr.move_to(self._dispdim[0]/2 - width/2, theight+oheight+self._dispdim[1]*.1)
		cr.show_text(self._song["artist"]+" - " + self._song["album"])
		cr.stroke()
		cr.restore()





if __name__ == "__main__":
	w= gtk.Window()
	w.connect("destroy", gtk.main_quit)
	p = play_bar(0x334466)
	w.add(p)
	w.show_all()

	gtk.main()
