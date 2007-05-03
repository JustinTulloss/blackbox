import gtk
import list_view
import play_queue
import play_bar

#Various widgets
main_list = list_view.list_view(list_view.g_song_data)
iplay_queue = play_queue.play_queue()
iplay_bar = play_bar.play_bar()

def destroy(src, data=None):
	gtk.main_quit()

#Send a destroy event if the q button was pressed
def quit_on_q(src, data=None):
	if(data.keyval == 113): #113 is ascii code for q, don't ask
		destroy(src)
	elif(data.keyval == 100): #d moves selection down
		main_list.change_selection(1)
	elif(data.keyval == 117): #u moves selection up
		main_list.change_selection(-1)
	elif(data.keyval == 115): #s makes a selection
		main_list.make_selection()
	elif(data.keyval == 102): #f moves forward
		main_list.move_forward()
	elif(data.keyval == 98): #b moves backwards
		main_list.move_backwards()
	elif(data.keyval == 101): #e enqueues songs
		main_list.enqueue_selection()
	elif(data.keyval == 114): #r dequeues (remove)
		next_song = iplay_queue.dequeue()
		iplay_bar.play_song(next_song)

def main():
	main_win = gtk.Window()

	#Allow us to quit by pressing 'q'
	main_win.connect("destroy", destroy)
	main_win.connect("key_press_event", quit_on_q)

	#This table will serve as the main layout container
	main_table = gtk.Table(2, 2)
	main_win.add(main_table)

	main_table.attach(iplay_bar, 1, 2, 1, 2, gtk.FILL, gtk.FILL)

	#main_list = list_view.list_view()
	main_table.attach(main_list, 1, 2, 0, 1)

	main_table.attach(iplay_queue, 0, 1, 0, 1, 0, gtk.FILL)

	#Connect components
	main_list.play_queue = iplay_queue

	#Display window
	main_win.fullscreen()
	main_win.set_decorated(0)
	main_win.show_all()
	main_list.grab_focus()

	gtk.main()

if __name__=="__main__":
	main()
