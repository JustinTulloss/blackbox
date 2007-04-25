import gtk
import radialmenuitem

menu_items = []
module_order = [1, 6, 3, 4, 0, 2, 5, 7] #The order modules are revealed

def create_module_view():
	table = gtk.Table(3, 3, True)

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
