import gtk
from ui import list_view
from ui import play_queue
from ui import play_bar
from ui import play_controls
from ui import song_info
import model
import sys #used for command line
from cwiid import gtkwiid
import getopt

PLAYING = 0
PAUSED = 1
STOPPED = 2

playmode = STOPPED

#if(len(sys.argv)>1):
#	song_list = song_info.get_song_list(sys.argv[1])
#else:
#	song_list = list_view.g_song_data

argv = sys.argv[1:]
optlist, args = getopt.getopt(argv, "f:w:d", ["daap", "files=", "use-wiimote"])

use_wii = False
song_list = None
for opt, arg in optlist:
	if opt in("-w", "--use-wiimote"):
		use_wii = True
	if opt in ("-f", "--files"):
		song_list = song_info.get_song_list(arg)
	elif opt in ("-d", "--daap"):
		song_list = model.MusicData()

if song_list == None:
	song_list = list_view.g_song_data

#Various widgets
main_list = list_view.list_view(song_list)
iplay_queue = play_queue.play_queue()
iplay_bar = play_bar.play_bar()
iplay_controls = play_controls.play_controls()

def destroy(src, data=None):
	gtk.main_quit()

#Send a destroy event if the q button was pressed
def quit_on_q(src, data=None):
	if(data.keyval == 113): #113 is ascii code for q, don't ask
		destroy(src)
	elif(data.keyval == 100): #d moves selection down
		main_list.change_selection(None, 1, None)
	elif(data.keyval == 117): #u moves selection up
		main_list.change_selection(None, -1, None)
	elif(data.keyval == 115): #s makes a selection
		main_list.make_selection(src)
	elif(data.keyval == 102): #f moves forward
		main_list.move_forward(src)
	elif(data.keyval == 98): #b moves backwards
		main_list.move_backwards(src)
	elif(data.keyval == 101): #e enqueues songs
		main_list.enqueue_selection(src)
	elif(data.keyval == 114): #r dequeues (remove)
		next_song = iplay_queue.dequeue()

def playfunction(src):
	global playmode
	if playmode == STOPPED:
		iplay_queue.dequeue()
		playmode = PLAYING
	elif playmode == PAUSED:
		iplay_bar.resume_song()
		playmode = PLAYING
	else:
		iplay_bar.pause_song()
		playmode= PAUSED

def main():
	main_win = gtk.Window()

	if use_wii == True:
		wii = gtkwiid.gtkWiimote()

		wii.connect("selected", main_list.make_selection)
		wii.connect("nav_forward", main_list.move_forward)
		wii.connect("nav_back", main_list.move_backwards)
		wii.connect("home", main_list.move_home)
		wii.connect("enqueue", main_list.enqueue_selection)
		wii.connect("scroll", main_list.change_selection)
		wii.connect("play_pressed", iplay_controls.play_pressed)
		wii.connect("play_released", iplay_controls.play_released)
		wii.connect("song_forward_pressed", iplay_controls.forward_pressed)
		wii.connect("song_forward_released", iplay_controls.forward_released)
		wii.connect("song_back_pressed", iplay_controls.back_pressed)
		wii.connect("song_back_released", iplay_controls.back_released)
	
		#We need to replace this with logic that works
		wii.connect("play_released", playfunction) 
		wii.connect("song_forward_released", iplay_queue.dequeue)
	
	#Allow us to quit by pressing 'q'
	main_win.connect("destroy", destroy)
	main_win.connect("key_press_event", quit_on_q)

	#This table will serve as the main layout container
	main_table = gtk.Table(2, 2)
	main_hbox = onepix()
	#main_table.set_col_spacing(0, 1)
	main_win.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,65000,0))
	#main_win.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0,0))
	
	main_win.add(main_table)

	main_table.attach(iplay_bar, 1, 2, 1, 2, gtk.FILL|gtk.EXPAND, gtk.FILL)

	#main_list = list_view.list_view()
	#main_table.attach(main_list, 1, 2, 0, 1)
	#main_table.attach(iplay_queue, 0, 1, 0, 1, 0)
	main_hbox._hbox.pack_end(main_list)
	main_hbox._hbox.pack_end(iplay_queue, False, False, 0)
	main_table.attach(main_hbox, 0, 2, 0, 1)

	main_table.attach(iplay_controls, 0,1,1,2, gtk.FILL, gtk.FILL)

	#Connect components
	main_list.play_queue = iplay_queue
	iplay_bar.connect("song_ended", iplay_queue.dequeue)
	iplay_queue.connect("play_song", iplay_bar.play_song)
	main_list.connect("play_song", iplay_bar.play_song)

	#Display window
	main_win.fullscreen()
	main_win.set_decorated(0)
	main_win.show_all()
	main_list.grab_focus()

	gtk.main()

class onepix(gtk.EventBox):
	_hbox = gtk.HBox(False, 1)
	def __init__(self):
		super(onepix, self).__init__()
		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0))
		self.add(self._hbox)

if __name__=="__main__":
	main()
