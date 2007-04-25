#!/usr/bin/python
#
#
#Justin Tulloss
#
#Trying to make a radial menu container.

import gtk
from gtk import gdk
import gobject

class RadContainer(gtk.Container):

	def add(self, child):
		print "Adding child..."
		self.child_list.append(child)
		child.set_parent(self)

	def remove(self):
		print "Removing child"

	def do_size_request(self, req):
		req.height = 500
		req.width = 500
		print "Reporting minimum size"

	def do_size_allocate(self, allocation):
		print "Size allocation"
		
		self.child_list[0].size_allocate(allocation)
		#self.set_allocation(allocation)
		#child_alloc = gtk.Allocation()
		#child_alloc.height = allocation.height
		#child_alloc.width = allocation.width
		#child_alloc.x = 0
		#child_alloc.y = 0

	def child_type(self):
		print "Reporting child type"
		if(self.child_list.count() < 8):
			return gtk.Widget.get_type()

	#def do_realize(self):
	#	print "Realizing"
	#	self.set_flags(self.flags() | gtk.REALIZED)

	def foreach(self, callback, callback_data):
		print "foreach called"
		callback(self.child_list[0], callback_data)

	def forall(self, callback, callback_data):
		print "forall called"
		callback(self.child_list[0], callback_data)

	def __init__(self):
		gtk.Container.__init__(self)
		self.set_flags(self.flags() | gtk.NO_WINDOW)
		print "Initializing"
		self.child_list = []

gobject.type_register(RadContainer)

def test():
	main_win = gtk.Window()
	main_win.connect("destroy", gtk.main_quit)

	button = gtk.Button("Hello World")

	#container = RadContainer()
	container = gtk.Frame()
	container.add(button)
	
	box = gtk.VBox()
	box.pack_start(gtk.Label("Test program"), False)
	box.pack_start(container)
	
	main_win.add(box)
	container.show()
	button.show()
	main_win.show_all()

	gtk.main()

if __name__ == "__main__":
	test()
