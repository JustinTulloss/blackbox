#!/usr/bin/python
#
#Justin Tulloss
#

"""Emits signals to GTK to allow for processing of WiiMote events"""

import gtk
gtk.gdk.threads_init()
import gobject
import cwiid
import math
import struct
import threading

#thresholds for emitting events
X_THRESHOLD = .9
PITCH_THRESHOLD = .35

class gtkWiimote(gtk.Widget):

	__gsignals__=dict(selected=(gobject.SIGNAL_RUN_FIRST, 
						gobject.TYPE_NONE,()),
					home=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE,()),
					scroll=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, (gobject.TYPE_INT, gobject.TYPE_INT)),
					enqueue=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					dequeue=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					play_pressed=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					play_released=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					song_forward_pressed=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					song_forward_released=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					song_back_pressed=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					song_back_released=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					nav_forward=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					nav_back=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
				)
	_mote = None
	_actions = {}

	def __init__(self):
		super(gtkWiimote, self).__init__()
		self._mote = cwiid.Wiimote(cwiid.FLAG_MESG_IFC)
		self._mote.command(cwiid.CMD_RPT_MODE, cwiid.RPT_BTN|cwiid.RPT_ACC)
		self._mote.set_callback(self.cwiidCallback)

		#state machine variables
		self._xabove = False
		self._no_scroll = False

		self._btnmask = 0

		#read in accelerometer calibration
		accel_buf = self._mote.read(cwiid.RW_EEPROM, 0x16, 7)
		self._accel_calib = struct.unpack("BBBBBBB", accel_buf)
		
		#initialize different callbacks
		self._actions[cwiid.MESG_BTN] = self.btn_cllbck
		self._actions[cwiid.MESG_ACC] = self.acc_cllbck
	

	def cwiidCallback(self, mesgs):
		#Loop through each message
		for msg in mesgs:
			if self._actions.has_key(msg[0]):
				self._actions[msg[0]](msg[1])
	
	def acc_cllbck(self, accdict):
		x = float(accdict["x"])
		y = float(accdict["y"])
		z = float(accdict["z"])

		#Weight the accelerations according to calibration data and
		#center around 0
		a_x = (x - self._accel_calib[0])/(self._accel_calib[4]-self._accel_calib[0])
		a_y = (y - self._accel_calib[1])/(self._accel_calib[5]-self._accel_calib[1])
		a_z = (z - self._accel_calib[2])/(self._accel_calib[6]-self._accel_calib[2])

		b_on = self._btnmask & cwiid.BTN_B

		roll = math.atan(float(a_x)/float(a_z))
		if a_z<=0:
			if (a_x>0):
				roll -= math.pi
			else:
				roll += math.pi
		roll = -roll
		pitch = math.atan(a_y/a_z*math.cos(roll))

		if (a_x>X_THRESHOLD and b_on and (self._xabove == False)):

			self._xabove = True
			gobject.idle_add(self.emit, "enqueue")

		if (a_x<X_THRESHOLD and self._xabove == True):
			self._xabove = False

		if (a_x<-X_THRESHOLD and b_on and (self._xbelow == False)):
			
			self.xabove = True
			gobject.idle_add(self.emit, "dequeue")
		
		if pitch>PITCH_THRESHOLD and self._no_scroll == False and not b_on:
			self._no_scroll=True;
			t = threading.Timer(.4-.2*pitch, self.scroll_again)
			t.start()
			gobject.idle_add(self.emit, "scroll", 1, 0)

		if pitch<-PITCH_THRESHOLD and self._no_scroll == False and not b_on:
			self._no_scroll=True;
			t = threading.Timer(.1-.1*pitch, self.scroll_again)
			t.start()
			gobject.idle_add(self.emit, "scroll", -1, 0)
	
	def scroll_again(self):
		self._no_scroll = False
			

	def btn_cllbck(self, btndict):
		btns = btndict["buttons"]
		omask = self._btnmask
		self._btnmask = btns

		if(btns & cwiid.BTN_A):
			gobject.idle_add(self.emit, "selected")
		if(btns & cwiid.BTN_HOME):
			gobject.idle_add(self.emit, "home")

		if(btns & cwiid.BTN_UP):
			gobject.idle_add(self.emit, "play_pressed")
		elif(omask & cwiid.BTN_UP):
			gobject.idle_add(self.emit, "play_released")

		if(btns & cwiid.BTN_RIGHT):
			gobject.idle_add(self.emit, "song_forward_pressed")
		elif(omask & cwiid.BTN_RIGHT):
			gobject.idle_add(self.emit, "song_forward_released")
		
		if(btns & cwiid.BTN_LEFT):
			gobject.idle_add(self.emit, "song_back_pressed")
		elif(omask & cwiid.BTN_LEFT):
			gobject.idle_add(self.emit, "song_back_released")

		if(btns & cwiid.BTN_MINUS):
			gobject.idle_add(self.emit, "nav_back")
		if(btns & cwiid.BTN_PLUS):
			gobject.idle_add(self.emit, "nav_forward")
		

if __name__ == "__main__":

	def selected_callback(widget):
		print "Selected!"


	window = gtk.Window()
	test = gtkWiimote()
	test.acc_cllbck({"x":131, "y":145, "z":126})
	window.add(test)
	test.connect("selected", selected_callback)
	#window.show_all()

	gtk.main()

