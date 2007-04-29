import gtk

(SONG_COL, ARTIST_COL, ALBUM_COL)= range(3)

class list_view(gtk.ScrolledWindow):
	def __init__(self):
		gtk.ScrolledWindow.__init__(self)
		self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
		
		self.model = gtk.ListStore(str, str, str)
		populate_model(self.model)

		self.view = gtk.TreeView(self.model)
		#self.view.set_headers_visible(False)
		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Song", renderer, text=SONG_COL)
		self.view.append_column(column)
		column = gtk.TreeViewColumn("Artist", renderer, text=ARTIST_COL)
		self.view.append_column(column)
		column = gtk.TreeViewColumn("Album", renderer, text=ALBUM_COL)
		self.view.append_column(column)

		self.add(self.view)


list_data = [("MX Missiles", "Andrew Bird", "The Myterious Production of Eggs"),
			("Come Together", "The Beatles", "Abbey Road"),
			("Black Dog", "Led Zeppelin", "IV")] * 10

def populate_model(model):
	for (song, artist, album) in list_data:
		iter = model.insert_before(None, None)
		model.set_value(iter, SONG_COL, song)
		model.set_value(iter, ARTIST_COL, artist)
		model.set_value(iter, ALBUM_COL, album)
	

def test():
	main_win = gtk.Window()
	list_test = list_view()
	main_win.add(list_test)
	main_win.show_all()

	main_win.connect("destroy", gtk.main_quit)
	gtk.main()

if __name__=="__main__":
	test()
