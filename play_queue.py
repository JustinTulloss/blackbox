import gtk

class play_queue(gtk.VBox):
	def __init__(self):
		gtk.VBox.__init__(self) 

		self.pack_start(gtk.Label("Play Queue"), False, True)
		
		self.queue_store = gtk.ListStore(str)
		self.queue_view = gtk.TreeView(self.queue_store)
		self.queue_view.set_headers_visible(False)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Play Queue", renderer, text=0)
		self.queue_view.append_column(column)

		self.pack_end(self.queue_view, False, True)

		self.song_list = []

	def enqueue(self, songs):
		store = self.queue_store
		for song in songs:
			if(self.song_list == []):
				top = None
			else:
				top = store.get_iter((0))
			iter = store.insert_before(top, None)
			store.set_value(iter, 0, song["title"])
			
			self.song_list.append(song)

	def dequeue(self):
		store = self.queue_store
		ilast = store.iter_n_children(None)
		last = store.iter_nth_child(None, ilast-1)
		
		if(last==None):
			return None

		store.remove(last)

		return self.song_list.pop(0)

def test():
	main_win = gtk.Window()
	queue = play_queue()
	main_win.add(queue)
	main_win.show_all()

	queue.enqueue_songs([{"title":"Come Together"}, {"title":"Black Dog"}])
	queue.enqueue_songs([{"title":"MX Missiles"}, {"title":"Ramble On"}])
	
	for i in range(5):
		next_song = queue.dequeue_song()
		print "Dequeueing "+next_song["title"]

	main_win.connect("destroy", gtk.main_quit)
	gtk.main()

if __name__=="__main__":
	test()
