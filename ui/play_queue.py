import gtk
import gobject
import cairo
from cairo_help import *
import pango

GRADIENT_COLOR = 0

class play_queue(gtk.EventBox):
	_vbox = gtk.VBox()
	_bgcolor = 0x334466
	
	__gsignals__ = dict(play_song=(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, \
			(gobject.TYPE_PYOBJECT,)))

	def __init__(self):
		super(play_queue, self).__init__() 

		#connect to necessary events
		#self.connect("expose_event", self.expose)
		
		#setup background
		self.set_visible_window(True)
		bgcolor = cairo_color(self._bgcolor)
		self.modify_bg(gtk.STATE_NORMAL, 
			gtk.gdk.Color(int(bgcolor[0]*65535), int(bgcolor[1]*65535), int(bgcolor[2]*65535)))

		#push title on
		self._pltitle = "Play Queue"

		#attributes of playlist title
		font = pango.FontDescription("Sans bold 14")
		attrs = pango.AttrList()
		attrs.insert(pango.AttrForeground(0xffff, 0xffff, 0xffff,0,45))
		attrs.insert(pango.AttrFontDesc(font, 0, 45))
		self._pllabel = gtk.Label(self._pltitle)
		self._pllabel.set_attributes(attrs)

		self._vbox.pack_start(self._pllabel, False, True)
		
		#setup list that takes care of queue
		self.queue_store = gtk.ListStore(gobject.TYPE_PYOBJECT)
		self.queue_view = gtk.TreeView(self.queue_store)
		self.queue_view.set_headers_visible(False)
		#self.queue_view.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_NONE)

		renderer = QueueRenderer()
		column = gtk.TreeViewColumn("Play Queue", renderer, text=0)
		column.set_property("spacing", 5)
		self.queue_view.append_column(column)

		self._vbox.pack_end(self.queue_view, False, True)

		self.add(self._vbox)
		self.set_size_request(150,400)

		self.song_list = []

	def enqueue(self, songs):
		store = self.queue_store
		for song in songs:
			if(self.song_list == []):
				top = None
			else:
				top = store.get_iter((0))
			iter = store.insert_before(top, None)
			store.set_value(iter, 0, song)
			
			self.song_list.append(song)

	def dequeue(self, widget=None):
		if(len(self.song_list) < 1):
			return

		store = self.queue_store
		ilast = store.iter_n_children(None)
		last = store.iter_nth_child(None, ilast-1)
		
		if(last==None):
			return None

		store.remove(last)

		self.emit("play_song", self.song_list.pop(0))
	
######################event handlers################
	def expose(self, widget, event):
		"""we have our own expose event to make everything pretty"""
		cr = widget.window.cairo_create() #CAIRO!!
		rect = self.get_allocation()
		cr.move_to(rect.width, 0)
		cr.line_to(rect.width, rect.height)
		cr.set_source_rgb(0,0,0)
		cr.set_line_width(1)
		cr.stroke()



		#self.draw(context)
	
class QueueRenderer(gtk.GenericCellRenderer):
	_bgcolor = 0x334466
	
	__gproperties__= {'text' : (gobject.TYPE_PYOBJECT, 'text to display',
								"This is the text to display in the queue",
								gobject.PARAM_WRITABLE)}
	def __init__(self):
		super(QueueRenderer, self).__init__()
	
	def do_set_property(self, pspec, value):
		if pspec.name == 'text':
			self._text = value
		else:
			raise AttributeError, 'unknown property %s' % pspec.name
	
	def do_get_property(self, pspec):
		if pspec.name == 'text':
			return self._text
		else:
			raise AttributeError, 'unknown property %s' % pspec.name
	
	def on_render(self, window, widget, background_area, expose_area, flags, other):
		
		#setup
		cr = window.cairo_create()
		#gray version
		draw_bg_gradient(cr, 0x909090, expose_area)
		#blue version
		#draw_bg_gradient(cr, 0x334466, background_area)

		"""
		Gray without gradient & white separator
		cr.rectangle(expose_area)
		cr.save()
		cr.translate(expose_area.x, expose_area.y)
		cr.scale(expose_area.width, expose_area.height)
		bgcolor = cairo_color(0xbfbfbf)
		cr.set_source_rgb(bgcolor[0],bgcolor[1],bgcolor[2])
		cr.fill()
		"""

		#cr.restore()
		#cr.move_to(0,5)
		#cr.line_to(expose_area.width, expose_area.height)
		#cr.set_source_rgb(0,0,0)
		#cr.set_line_width(1)
		#cr.stroke()

		#start figuring out font size and location
		cr.save()
		cr.translate(expose_area.x, expose_area.y)
		cr.scale(expose_area.height, expose_area.height)
		
		#title
		theight=aheight=lheight=0
		cr.set_font_size(.8)
		cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
		tasc, tdesc, theight, tmax_x, tmax_y = cr.font_extents()
		cr.move_to(.1, theight+.1)
		cr.show_text(self._text.name)
		cr.stroke()

		"""
		cr.set_font_size(.15)
		cr.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
		#artist
		if hasattr(self._text,"artist"):
			aasc, adesc, aheight, amax_x, amax_y = cr.font_extents()
			cr.move_to(.2, aheight+theight+.1)
			cr.show_text(self._text.artist)
			cr.stroke()

		#album
		if hasattr(self._text, "album"):
			lasc, ldesc, lheight, lmax_x, lmax_y = cr.font_extents()
			cr.move_to(.2, lheight+aheight+theight+.1)
			cr.show_text(self._text.album)
			cr.stroke()

		"""
		cr.restore()

	
	def on_get_size(self, widget, cell_area):
		return (0,0, 150,10)
		
def test():
	main_win = gtk.Window()
	queue = play_queue()
	main_win.add(queue)
	main_win.show_all()

	queue.enqueue([{"title":"Come Together", "artist":"The Beatles", "album":"Abbey Road"}, 
					{"title":"Black Dog", "artist":"The Beatles", "album":"Abbey Road"}])
	queue.enqueue([{"title":"MX Missiles"}, {"title":"Ramble On", "album":"IV"}])
	
	#for i in range(5):
	#	next_song = queue.dequeue()
	#	#print "Dequeueing "+next_song["title"]

	main_win.connect("destroy", gtk.main_quit)
	gtk.main()

if __name__=="__main__":
	test()
