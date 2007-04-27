import gtk

(SONG_COL, ARTIST_COL, ALBUM_COL)= range(3)

class list_view(gtk.HBox):
	def __init__(self):
		gtk.HBox.__init__(self)
		self.pack_start(gtk.Label("asdf"))
		
		self.scroll_bar = gtk.VScrollbar()
		self.pack_start(self.scroll_bar, False, True)

		self.model = gtk.ListStore(str, str, str)
		iter = self.model.insert_before(None, None)
		self.model.set_value(iter, SONG_COL, "MX Missiles")
		self.model.set_value(iter, ARTIST_COL, "Andrew Bird")
		self.model.set_value(iter, ALBUM_COL, "The Mysterious Production of Eggs")

		self.view = gtk.TreeView(self.model)
		self.view.set_headers_visible(False)
		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Song", renderer, text=SONG_COL)
		self.view.append_column(column)
		column = gtk.TreeViewColumn("Artist", renderer, text=ARTIST_COL)
		self.view.append_column(column)
		column = gtk.TreeViewColumn("Album", renderer, text=ALBUM_COL)
		self.view.append_column(column)
		self.pack_start(self.view)


def test():
	main_win = gtk.Window()
	list_test = list_view()
	main_win.add(list_test)
	main_win.show_all()

	main_win.connect("destroy", gtk.main_quit)
	gtk.main()

if __name__=="__main__":
	test()
