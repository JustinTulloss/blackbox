import gtk

class bread_crumb(gtk.HBox):
	def __init__(self):
		gtk.HBox.__init__(self)
		self.artist_label = None
		self.album_label = None

	def get_artist(self):
		return self.artist_label.get_text()

	def set_artist(self, value):
		if(self.artist_label == None):
			self.artist_label = gtk.Label(value)
			self.pack_start(self.artist_label, False, True)
			self.artist_label.show()

			self.seperator = gtk.Label(" > ")
			self.pack_start(self.seperator, False, True)
			self.seperator.show()
		else:
			self.artist_label.set_text(value)

		#TODO: breadcrumbs should be in a list with enum'ed posistions
		#	on setting a breadcrumb, need to select that breadcrumb, deselect
		#	all others, and hide breadcrumbs/seperators below current one
