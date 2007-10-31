#
#Justin Tulloss
#
#

"""
Adhering to our model interface with mock data
"""

from basemodel import BaseModel

class MockModel(BaseModel):
	def __init__(self):
		super(MockModel, self).__init__()
		
		self._tracks= [MockData(artist="The Beatles",
		 						album="Abbey Road",
								name="Come Together",
								path="/home/brian/machome/Music/Abbey Road/01 Come Together.mp3"),
					MockData(artist="The Beatles",
							album="Abbey Road",
							name="Polythene Pam",
							path="/home/brian/machome/Music/Abbey Road/12 Polythene Pam.mp3"),
					MockData(artist="Led Zeppelin",
							album="IV",
							name="Black Dog"),
					MockData(artist="Led Zeppelin",
							album="II",
							name="Black Dog"),
					MockData(artist="Andrew Bird",
							album="The Mysterious Production of Eggs",
							name="MX Missiles")]
class MockData:
	"""
	This has the same fields (kind of) that DAAPTrack has
	"""
	
	artist = None
	album = None
	name= None
	path = None
	
	def __init__(self, **kwargs):
		for arg in kwargs.keys():
			setattr(self, arg, kwargs[arg])


