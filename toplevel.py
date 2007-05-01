import gtk
import list_view
import play_queue

main_list = list_view.list_view(list_view.g_song_data)

def destroy(src, data=None):
	gtk.main_quit()

#Send a destroy event if the q button was pressed
def quit_on_q(src, data=None):
	if(data.keyval == 113): #113 is ascii code for q, don't ask
		destroy(src)
	elif(data.keyval == 100): #d
		main_list.change_selection(1)
	elif(data.keyval == 117): #u
		main_list.change_selection(-1)
	elif(data.keyval == 115): #s selects
		main_list.make_selection()
	elif(data.keyval == 102): #f moves forward
		main_list.move_forward()
	elif(data.keyval == 98): #b moves backwards
		main_list.move_backwards()

def main():
	main_win = gtk.Window()

	#Allow us to quit by pressing 'q'
	main_win.connect("destroy", destroy)
	main_win.connect("key_press_event", quit_on_q)

	#This table will serve as the main layout container
	main_table = gtk.Table(2, 2)
	main_win.add(main_table)

	now_playing = gtk.Label("Now Playing: LCD Soundsystem")
	main_table.attach(now_playing, 1, 2, 1, 2, gtk.FILL, gtk.FILL)

	#main_list = list_view.list_view()
	main_table.attach(main_list, 1, 2, 0, 1)

	iplay_queue = play_queue.play_queue()
	main_table.attach(iplay_queue, 0, 1, 0, 1, 0, gtk.FILL)
	
	"""
	queue_header = gtk.Label("Play Queue")
	play_queue.pack_start(queue_header, False)
	song_list = gtk.VBox()
	play_queue.pack_end(song_list)

	song_list.pack_end(gtk.Label("Next song"), False)
	song_list.pack_end(gtk.Label("Song before that"), False)
	"""
	#Display window
	main_win.fullscreen()
	main_win.set_decorated(0)
	main_win.show_all()
	main_list.grab_focus()

	gtk.main()

if __name__=="__main__":
	main()
