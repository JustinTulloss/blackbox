import gtk

#This class shows what is playing and eventually should handle all music
#It will need to dequeue songs from the song list when it needs them
class play_bar(gtk.HBox):
	def __init__(self):
		gtk.HBox.__init__(self)

		self.pack_start(gtk.Label("Now Playing: "), False, True)

		self.now_playing = None

	def play_song(self, song):
		if(self.now_playing == None): #need to initialize
			self.now_playing = gtk.Label()
			self.now_playing.show()
			self.pack_start(self.now_playing, False, True)

		self.now_playing.set_text(song["title"])
