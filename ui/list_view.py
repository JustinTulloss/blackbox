#TODO: right now, breaks if there are songs by the same name,
#	but different artists
#
#TODO: Rework this so it's not a giant hardcoded if/else parade

import gtk
#import gobject
import breadcrumb
from cairo_help import *
import song_info
import gobject

(TITLE_COL, ARTIST_COL, ALBUM_COL, PATH_COL)= range(4)
(HOME_CRUMB, ARTIST_CRUMB, ALBUM_CRUMB) = range(3)

class list_view(gtk.VBox):
	__gsignals__ = dict(play_song=(gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, \
			(gobject.TYPE_PYOBJECT,)))

	def __init__(self, song_data):
		super(list_view, self).__init__()

		self.bread_crumb = breadcrumb.bread_crumb()
		self.pack_start(self.bread_crumb, False, True)
		
		self.scrolled_window = gtk.ScrolledWindow()
		self.scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
		self.pack_start(self.scrolled_window)
		
		self.renderer = gtk.CellRendererText()
		#self.renderer = ListRenderer()

		self.song_data = song_data
		
		if hasattr(self.song_data, "connect"):
			self.song_data.connect("add_tracks", self._update_view)

		self.artist_view = self.create_view("artist", "Artists")
		self.current_view = self.artist_view

		self.album_view = None
		self.song_view = None

		self.scrolled_window.add(self.artist_view)
	
	def create_view(self, col_name, col_header, filters={}):
		store = self.create_store(col_name, filters)

		view = gtk.TreeView(store)

		column = gtk.TreeViewColumn(col_header, self.renderer, text=0)
		view.append_column(column)

		view.set_enable_search(False)

		return view

	def create_store(self, col_name, filters={}):
		"""Creates a list store based on one field, and removed duplicates"""
		val_list = []
		for song in self.song_data.query(filters):
			val_list.append(getattr(song,col_name))

		val_list = sorted(set(val_list))
		
		store = gtk.ListStore(str)
		store.set_sort_column_id(0, gtk.SORT_ASCENDING)

		for val in val_list:
			iter = store.insert_after(None, None)
			store.set_value(iter, 0, val)

		return store

	def grab_focus(self):
		self.current_view.grab_focus()
		#Trying to delay setting this till after show_all
		self.bread_crumb.set_crumb(0, "Home")

	#moves the selection by amount
	def change_selection(self, src, amount, crap):
		view = self.current_view
		((path,), col) = view.get_cursor()
		path += amount
		path = max(0, path)
		rows = view.get_model().iter_n_children(None)
		path = min(rows-1, path)

		view.set_cursor((path))

	#Performs the default action on the currently selected item
	def make_selection(self, src):
		view = self.current_view
		
		(store, iter) = view.get_selection().get_selected()
		val = store.get_value(iter, 0)
		
		if(view == self.artist_view): #Goto album view
			#new_data = [x for x in self.song_data if getattr(x, "artist")==val]
			self.album_view = self.create_view("album", "Albums", dict(artist=val))
			self.set_current_view(self.album_view)
			self.bread_crumb.set_crumb(ARTIST_CRUMB, val)
		elif(view == self.album_view): #Goto song view
			#new_data = [x for x in self.song_data if getattr(x,"album")==val]
			self.song_view = self.create_view("name", "Songs", dict(album=val))
			self.set_current_view(self.song_view)

			self.bread_crumb.set_crumb(ALBUM_CRUMB, val)
		elif(view == self.song_view): #Play song
			#songs = [x for x in self.song_data if getattr(x,"title")==val]
			songs = self.song_data.query(dict(name=val))
			song = songs[0]
			self.emit("play_song", song)

	def set_current_view(self, new_view):
		self.scrolled_window.remove(self.current_view)
		
		self.current_view = new_view
		self.scrolled_window.add(self.current_view)
		self.current_view.show()
		self.current_view.grab_focus()

	def move_forward(self, src):
		view = self.current_view

		if(view == self.artist_view):
			if(self.album_view != None):
				self.set_current_view(self.album_view)
				self.bread_crumb.move_forward()
		elif(view == self.album_view):
			if(self.artist_view != None):
				self.set_current_view(self.song_view)
				self.bread_crumb.move_forward()

	def move_backwards(self, src):
		view = self.current_view

		if(view == self.album_view):
			self.set_current_view(self.artist_view)
			self.bread_crumb.move_backwards()
		elif(view == self.song_view):
			self.set_current_view(self.album_view)
			self.bread_crumb.move_backwards()
	
	def move_home(self, src):
		self.bread_crumb.set_crumb(HOME_CRUMB, "Home")
		self.set_current_view(self.artist_view)

	def enqueue_selection(self, src):
		view = self.current_view
		
		(store, iter) = view.get_selection().get_selected()
		val = store.get_value(iter, 0)

		if(view == self.artist_view):
			songs = self.song_data.query({'artist':val})
			self.play_queue.enqueue(songs)
		elif(view == self.album_view):
			songs = self.song_data.query({'album':val})
			self.play_queue.enqueue(songs)
		elif(view == self.song_view):
			songs = self.song_data.query({'name':val})
			self.play_queue.enqueue(songs)
	
	def _update_view(self, data):
		self.artist_view = self.create_view("artist", "Artist")
		self.set_current_view(self.artist_view)

class RubiListStore(gtk.TreeView):
	def __init__(self):
		super(RubiListStore, self).__init__()
		self.connect("expose_event", self.expose)
	
	def expose(self, widget, event):
		cr = widget.window.cairo_create()
		cr.rectangle(event.area)

		self.draw(cr)
		return False
	
	def draw(self, cr):
		draw_bg(cr, 0x558899, self.get_allocation())

def test():
	main_win = gtk.Window()
	#list_test = list_view(g_song_data)
	list_test = list_view(song_info.get_song_list("/mnt/windows/MyMusic"))
	main_win.add(list_test)
	main_win.show_all()

	main_win.connect("destroy", gtk.main_quit)
	gtk.main()

if __name__=="__main__":
	test()
