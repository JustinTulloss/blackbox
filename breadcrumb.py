import gtk


class bread_crumb(gtk.HBox):
	def __init__(self):
		gtk.HBox.__init__(self)
		self.artist_label = gtk.Label()
		self.artist_val = ""
		self.album_label = gtk.Label()
		self.album_val = ""
		self.seperator = gtk.Label(">")

		self.pack_start(self.artist_label, False, True)
		
		self.initialized = False

	def get_artist(self):
		return self.artist_label.get_text()

	def highlight_artist(self):
		self.artist_label.set_markup("<u>"+self.artist_val+"</u>")
		self.album_label.set_text(self.album_val)

	def set_artist(self, value):
		self.artist_val = value
		self.seperator.hide()
		self.album_label.hide()

		self.highlight_artist()

		if(self.initialized == False):
			self.pack_start(self.seperator, False, True)
			self.pack_start(self.album_label, False, True)
			
			self.initialized = True

	def get_album(self):
		return self.album_label.get_text()

	def highlight_album(self):
		self.album_label.set_markup("<u>"+self.album_val+"</u>")
		self.artist_label.set_text(self.artist_val)

	def set_album(self, value):
		self.album_val = value
		self.album_label.show()
		self.seperator.show()

		self.highlight_album()

