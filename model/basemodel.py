#!/usr/bin/python
#
#
#Justin Tulloss
#
"""
A base interface for our model so we can run with and without daap
"""

import gobject

class BaseModel(gobject.GObject):
	"""
	The base of our model
	"""
	#signals that indicate that you should probably update your view
	__gsignals__ = dict(
		add_tracks=(gobject.SIGNAL_RUN_FIRST,
					gobject.TYPE_NONE,()),
		remove_tracks=(gobject.SIGNAL_RUN_FIRST,
					gobject.TYPE_NONE,()))

	_tracks = []

	def __init__(self):
		"""Make a new music data provider."""
		super(BaseModel, self).__init__()

	def destroy(self):
		pass

	def query(self, filters={}):
		"""	Finds a list of songs that match the
		arbitrary number of filters passed in"""
		def ffunc(track):
			"""Filter function goes through each filter condition and
			sees if the DAAPTrack matches"""
			match = True
			for key in filters.keys():
				if not getattr(track, key) == filters[key]:
					return False
			return True

		return filter(ffunc, self._tracks)
