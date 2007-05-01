import gtk

class play_queue(gtk.VBox):
	def __init__(self):
		gtk.VBox.__init__(self)

		self.pack_start(gtk.Label("Play Queue"))
