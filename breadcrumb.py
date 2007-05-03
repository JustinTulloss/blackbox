import gtk

MAX_CRUMBS = 4

class bread_crumb(gtk.HBox):
	def __init__(self):
		gtk.HBox.__init__(self)

		self.crumb_list = [] #This will hold label, value, seperator triples
		for i in range(MAX_CRUMBS):
			label = gtk.Label()
			value = None
			if(i==0): #This is the top element, so it doesn't have a seperator
				seperator = None
			else:
				seperator = gtk.Label(">")

			self.crumb_list.append((label, value, seperator))

		self.highlighted_crumb = 0

		self.initialized = False

	def get_crumb(self, num):
		(label, value, seperator) = self.crumb_list[num]
		return value

	def set_crumb(self, num, new_value):
		if(self.initialized == False):
			for (label, value, seperator) in self.crumb_list:
				if(seperator != None):
					self.pack_start(seperator, False, True)
				self.pack_start(label, False, True)
			
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
		(label, value, seperator) = self.crumb_list[self.highlighted_crumb]
		label.set_text(value)

		(label, value, seperator) = self.crumb_list[num]
		label.set_markup("<u>"+value+"</u>")
		label.show()
		self.highlighted_crumb = num

	def move_forward(self):
		new_i = self.highlighted_crumb+1
		if(new_i < MAX_CRUMBS):
			self.highlight_crumb(new_i)
	
	def move_backwards(self):
		new_i = self.highlighted_crumb-1
		if(new_i >= 0):
			self.highlight_crumb(new_i)
