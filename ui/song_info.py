import os
import re
from mutagen.easyid3 import EasyID3

is_mp3 = re.compile(r".*.mp3$")

def get_song_list(path):
	song_list = []
	
	for (dir, subdirs, files) in os.walk(path):
		for file in files:
			if(is_mp3.match(file) != None):
				path = os.path.join(dir, file)
				
				try:
					song = create_song_hash(path)
				except:
					continue
				song_list.append(song)
	
	return song_list

song_fields = ["artist", "album", "title"]

def create_song_hash(path):
	song_metadata = EasyID3(path)
	song = {"path":path}

	for field in song_fields:
		song[field] = song_metadata[field][0]
		if(len(song[field]) < 2):
			raise BadTags
	
	return song
