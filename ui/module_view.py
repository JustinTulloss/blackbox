#!/usr/bin/python
#
#
#This file causes me pain

import gtk
gtk.gdk.threads_init()
import gtkwiid
import radialmenuitem

menu_items = []
module_order = [1, 7, 0, 2, 6, 8, 3, 5] #The order modules are revealed
sel_item = -1 #currently selected item
xwaiting, ywaiting = 0, 0

def acc_handler(widget, x, y, z):
	global sel_item, ywaiting, xwaiting
	print "%d %d %d" % (x,y,z)

	if x<120:
		col = 0
	elif x<150:
		col = 1
	else:
		col = 2

	if y<124:
		row = 0
	elif y<134:
		row = 1
		col = 1
		if x>=150:
			row = 0
			col = 2
		elif x<120:
			row = 2
			col = 0
	else:
		row = 2

	new_sel_item = row*3 + col
	"""if x < 100:
		if xwaiting == 0 and sel_item %3==0: #isn't waiting or left edge
			menu_items[sel_item].deselect()
			sel_item = sel_item-1
			xwaiting=1
	elif x > 200:
		if xwaiting == 0  and sel_item %3 == 1: #isn't waiting or right edge
			menu_items[sel_item].deselect()
			sel_item = sel_item+1
			xwaiting=1
	elif xwaiting == 1:
		xwaiting = 0
	
	if y < 100:
		if ywaiting == 0 and sel_item >2:
			menu_items[sel_item].deselect()
			sel_item = sel_item-3
			ywaiting = 1
	elif y > 200:
		print "Move up"
		if ywaiting == 0 and sel_item <6:
			menu_items[sel_item].deselect()
			sel_item = sel_item+3
			ywaiting = 1
	elif ywaiting == 1:
		ywaiting = 0
	"""
	if sel_item != new_sel_item:	
		menu_items[sel_item].deselect()
		menu_items[new_sel_item].select()
		sel_item = new_sel_item

def create_module_view():
	table = gtk.Table(3, 3, True)
	wii = gtkwiid.gtkWiimote()
	sel_item = 0

	table.attach(wii, 0,1,0,1)
	wii.connect("acc_event", acc_handler)

	for i in range(0, 9):
		row = i/3
		col = i%3

		flags = gtk.EXPAND | gtk.FILL

		if(i!=4): #This is a module spot
			menu_item = radialmenuitem.RadItem()
			menu_items.append(menu_item)
			table.attach(menu_item, col, col+1, row, row+1, flags, flags, 5, 5)
		else: #Middle spot
			menu_item = radialmenuitem.RadItem()
			menu_items.append(menu_item)
			table.attach(menu_item, col, col+1, row, row+1, flags, flags, 30,30)
			menu_item.show()
			

	return table

def set_module_options(table, option_list):
	for i in range(0, 8):
		if(i!=4):
			menu_items[i].hide()

	for i in range(0, len(option_list)):
		menu_items[module_order[i]].set_text(option_list[i])
		menu_items[module_order[i]].show()

def test():
	main_win = gtk.Window()
	main_win.connect("destroy", gtk.main_quit)

	module_view = create_module_view()
	set_module_options(module_view, ["1", "2", "3", "4", "5", "6"])

	main_win.add(module_view)
	module_view.show()
	main_win.show()
	
	gtk.main()

if __name__=="__main__":
	test()
