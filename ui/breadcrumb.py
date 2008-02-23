import gtk
import pango
from cairo_help import *

MAX_CRUMBS = 4

class bread_crumb(gtk.EventBox):
	_hbox = gtk.HBox()
	def __init__(self):
		super(bread_crumb, self).__init__()

		#connect events
		self.connect("expose_event", self.expose)

		self.crumb_list = [] #This will hold label, value, seperator triples
		#attributes of breadcrumb text
		font = pango.FontDescription("Sans 12")
		attrs = pango.AttrList()
		attrs.insert(pango.AttrForeground(0xffff, 0xffff, 0xffff,0,45))
		attrs.insert(pango.AttrFontDesc(font, 0, 45))
		attrs.insert(pango.AttrWeight(pango.WEIGHT_NORMAL, 0, 45))

		for i in range(MAX_CRUMBS):
			label = gtk.Label()
			label.set_attributes(attrs)
			value = None
			if(i==0): #This is the top element, so it doesn't have a seperator
				seperator = None
			else:
				seperator = gtk.Label(">")
				seperator.set_attributes(attrs)

			self.crumb_list.append((label, value, seperator))

		self.highlighted_crumb = 0

		self.initialized = False
		self.add(self._hbox)
		self.set_visible_window(False)
	
	def expose(self, widget, event):
		cr = widget.window.cairo_create()

		cr.rectangle(*event.area)
		cr.clip()

		self.draw(cr)
		return False
	
	def draw(self, cr):
		rect = self.get_allocation()
		draw_bg_gradient(cr, 0x334466, rect)
		self.draw_highlighted(cr)

	def get_crumb(self, num):
		(label, value, seperator) = self.crumb_list[num]
		return value

	def set_crumb(self, num, new_value):
		if(self.initialized == False):
			for (label, value, seperator) in self.crumb_list:
				if(seperator != None):
					self._hbox.pack_start(seperator, False, True)
				self._hbox.pack_start(label, False, True, 5)
			
			self.initialized = True

		(label, value, seperator) = self.crumb_list[num]
		if(seperator != None):
			seperator.show()

		self.crumb_list[num] = (label, new_value, seperator)
		self.highlight_crumb(num)
 		
		#We want to hide all crumbs above current one
		for i in range(num+1, MAX_CRUMBS):
			(label, value, seperator) = self.crumb_list[i]
			label.hide()
			seperator.hide()
	
	def highlight_crumb(self, num):

		(nlabel, nvalue, nseperator) = self.crumb_list[num]
		nattrs=nlabel.get_attributes()
		nattrs.change(pango.AttrWeight(pango.WEIGHT_BOLD, 0, 45))
		nlabel.set_attributes(nattrs)
		nlabel.set_label(nvalue)
		nlabel.show()

		(olabel, ovalue, oseperator) = self.crumb_list[self.highlighted_crumb]
		oattrs=olabel.get_attributes()
		oattrs.change(pango.AttrWeight(pango.WEIGHT_NORMAL, 0, 45))
		olabel.set_attributes(oattrs)
		olabel.set_label(ovalue)
		olabel.show()

		self.highlighted_crumb = num
	
	def draw_highlighted(self, cr):
		pass

	def move_forward(self):
		new_i = self.highlighted_crumb+1
		if(new_i < MAX_CRUMBS):
			self.highlight_crumb(new_i)
	
	def move_backwards(self):
		new_i = self.highlighted_crumb-1
		if(new_i >= 0):
			self.highlight_crumb(new_i)
