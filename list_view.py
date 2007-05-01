#TODO: right now, breaks if there is songs by the same name,
#	but different artists

import gtk
import breadcrumb

(TITLE_COL, ARTIST_COL, ALBUM_COL, PATH_COL)= range(4)

class list_view(gtk.VBox):
	def __init__(self, song_data):
		gtk.VBox.__init__(self)
		#gtk.ScrolledWindow.__init__(self)
		#self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
		self.bread_crumb = breadcrumb.bread_crumb()
		self.pack_start(self.bread_crumb, False, True)
		
		self.scrolled_window = gtk.ScrolledWindow()
		self.scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
		self.pack_start(self.scrolled_window)
		
		"""
		self.model = gtk.ListStore(str, str, str, str)
		populate_model(self.model)
	
		self.view = gtk.TreeView(self.model)
		self.view.set_headers_visible(False)
		column = gtk.TreeViewColumn("Songname", renderer, text=TITLE_COL)
		self.view.append_column(column)
		column = gtk.TreeViewColumn("Artist", renderer, text=ARTIST_COL)
		self.view.append_column(column)
		column = gtk.TreeViewColumn("Album", renderer, text=ALBUM_COL)
		self.view.append_column(column)
		"""

		self.renderer = gtk.CellRendererText()

		#self.view.set_enable_search(False)

		self.song_data = song_data
		self.artist_view = self.create_view(song_data, "artist", "Artists")
		self.current_view = self.artist_view

		self.album_view = None
		self.song_view = None

		self.scrolled_window.add(self.artist_view)
	
	"""
	def create_artist_view(self, song_data):
		artist_store = self.create_store(song_data, "artist")
		artist_view = gtk.TreeView(artist_store)

		column = gtk.TreeViewColumn("Artist", self.renderer, text=0)
		artist_view.append_column(column)

		artist_view.set_enable_search(False)

		return artist_view

	def create_album_view(self, song_data, artist):
		new_data = [x for x in self.song_data if x["artist"]==artist]
		album_store = self.create_store(new_data, "album")
		album_view = gtk.TreeView(album_store)

		column = gtk.TreeViewColumn("Album", self.renderer, text=0)
		album_view.append_column(column)

		album_view.set_enable_search(False)

		return album_view
	"""

	def create_view(self, song_data, col_name, col_header):
		store = self.create_store(song_data, col_name)

		view = gtk.TreeView(store)

		column = gtk.TreeViewColumn(col_header, self.renderer, text=0)
		view.append_column(column)

		view.set_enable_search(False)

		return view


	def create_store(self, song_data, col_name):
		"""Creates a list store based on one field, and removed duplicates"""
		val_list = []
		for song in song_data:
			val_list.append(song[col_name])

		val_list = sorted(set(val_list))
		
		store = gtk.ListStore(str)

		for val in val_list:
			iter = store.insert_after(None, None)
			store.set_value(iter, 0, val)

		return store

	def grab_focus(self):
		self.current_view.grab_focus()

	#moves the selection by amount
	def change_selection(self, amount):
		view = self.current_view
		((path,), col) = view.get_cursor()
		path += amount
		path = max(0, path)
		rows = view.get_model().iter_n_children(None)
		path = min(rows-1, path)

		view.set_cursor((path))

	#Performs the default action on the currently selected item
	def make_selection(self):
		view = self.current_view
		
		(store, iter) = view.get_selection().get_selected()
		val = store.get_value(iter, 0)

		if(view == self.artist_view): #Goto album view
			new_data = [x for x in self.song_data if x["artist"]==val]
			self.album_view = self.create_view(new_data, "album", "Albums")
			self.set_current_view(self.album_view)

			self.bread_crumb.set_artist(val)
		elif(view == self.album_view): #Goto song view
			new_data = [x for x in self.song_data if x["album"]==val]
			self.song_view = self.create_view(new_data, "title", "Songs")
			self.set_current_view(self.song_view)

			self.bread_crumb.set_album(val)
		elif(view == self.song_view): #Play song
			songs = [x for x in self.song_data if x["title"]==val]
			song = songs[0]
			print "Song "+song["title"]+" selected"

	def set_current_view(self, new_view):
		self.scrolled_window.remove(self.current_view)
		
		self.current_view = new_view
		self.scrolled_window.add(self.current_view)
		self.current_view.show()
		self.current_view.grab_focus()

	def move_forward(self):
		view = self.current_view

		if(view == self.artist_view):
			if(self.album_view != None):
				self.set_current_view(self.album_view)
				self.bread_crumb.highlight_artist()
		elif(view == self.album_view):
			if(self.artist_view != None):
				self.set_current_view(self.song_view)
				self.bread_crumb.highlight_album()

	def move_backwards(self):
		view = self.current_view

		if(view == self.album_view):
			self.set_current_view(self.artist_view)
		elif(view == self.song_view):
			self.set_current_view(self.album_view)
			self.bread_crumb.highlight_artist()


list_data = [("MX Missiles", "Andrew Bird", "The Myterious Production of Eggs"),
			("Come Together", "The Beatles", "Abbey Road"),
			("Black Dog", "Led Zeppelin", "IV")] * 30

g_song_data = [{"artist":"The Beatles", "album":"Abbey Road",
					"title":"Come Together"},
				{"artist":"The Beatles", "album":"Abbey Road",
					"title":"Polythene Pam"},
				{"artist":"Led Zeppelin", "album":"IV", "title":"Black Dog"},
				{"artist":"Led Zeppelin", "album":"II", "title":"Ramble On"},
				{"artist":"Andrew Bird", 
					"album":"The Mysterious Production of Eggs",
					"title":"MX Missiles"}]

def populate_model(model):
	for (song, artist, album) in list_data:
		iter = model.insert_before(None, None)
		model.set_value(iter, TITLE_COL, song)
		model.set_value(iter, ARTIST_COL, artist)
		model.set_value(iter, ALBUM_COL, album)
	

def test():
	main_win = gtk.Window()
	list_test = list_view(g_song_data)
	main_win.add(list_test)
	main_win.show_all()

	main_win.connect("destroy", gtk.main_quit)
	gtk.main()

if __name__=="__main__":
	test()
