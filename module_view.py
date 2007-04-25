#!/usr/bin/python
#
#
#This file causes me pain

import gtk
gtk.gdk.threads_init()
import gtkwiid
import radialmenuitem

menu_items = []
module_order = [1, 6, 3, 4, 0, 2, 5, 7] #The order modules are revealed
morder = (	[5,1,6],
			[3,0,4],
			[7,2,8])
sel_item = 0
xwaiting, ywaiting = 0, 0

def acc_handler(widget, x, y, z):
	global sel_item, ywaiting, xwaiting
	if sel_item in morder[0]:
		i=0
	elif sel_item in morder[1]:
		i=1
	elif sel_item in morder[2]:
		i=2

	j=morder[i].index(sel_item)

	if x < 100:
		if xwaiting == 0 and sel_item != morder[i][0]:
			menu_items[sel_item-1].deselect()
			sel_item = morder[i][j-1]
			xwaiting=1
	elif x > 200:
		if xwaiting == 0  and sel_item != morder[i][2]:
			menu_items[sel_item-1].deselect()
			sel_item = morder[i][j+1]
			xwaiting=1
	elif xwaiting == 1:
		xwaiting = 0
	
	if y < 50:
		if ywaiting == 0 and sel_item != morder[0][j]:
			menu_items[sel_item-1].deselect()
			sel_item = morder[i][j]
			ywaiting = 1
	elif y > 250:
		if ywaiting == 0 and sel_item != morder[2][j]:
			menu_items[sel_item-1].deselect()
			sel_item = morder[i+1][j]
			ywaiting = 1
	elif ywaiting == 1:
		ywaiting = 0

	menu_items[sel_item-1].select()

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
			table.attach(menu_item, col, col+1, row, row+1, flags, flags, 30,30)
			menu_item.show()
			

	return table

def set_module_options(table, option_list):
	for i in range(0, 8):
		menu_items[i].hide()

	for i in range(0, len(option_list)):
		menu_items[module_order[i]].set_text(option_list[i])
		menu_items[module_order[i]].show()

def test():
	main_win = gtk.Window()
	main_win.connect("destroy", gtk.main_quit)

	module_view = create_module_view()
	set_module_options(module_view, ["1", "2", "3", "4", "5", "6", "7", "8"])

	main_win.add(module_view)
	module_view.show()
	main_win.show()
	
	gtk.main()

if __name__=="__main__":
	test()
