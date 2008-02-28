#!/usr/bin/python
#
#Justin Tulloss
#

"""Emits signals to GTK to allow for processing of WiiMote events"""

import gtk
gtk.gdk.threads_init()
import time
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
					one_pressed=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					one_released=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					two_pressed=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					two_released=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					nav_forward=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					nav_back=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
					disconnect=(gobject.SIGNAL_RUN_FIRST,
						gobject.TYPE_NONE, ()),
				)
	_mote = None
	_actions = {}

	def __init__(self):
		super(gtkWiimote, self).__init__()
		self.scan = True
		self._connect_thread = threading.Thread(None, self._scan_for_mote)
		self._connect_thread.setDaemon(True)
		self._connect_thread.start()

		#state machine variables
		self._xabove = False
		self._no_scroll = False

		self._btnmask = 0

		
		#initialize different callbacks
		self._actions[cwiid.MESG_BTN] = self.btn_cllbck
		self._actions[cwiid.MESG_ACC] = self.acc_cllbck
		self._actions[cwiid.MESG_ERROR] = self.err_cllbck

		# Initialize scrolling stuff
		"""
		self._velocity = 0;
		self.scroll = True
		self._scroll_thread = threading.Thread(None, self._scroller)
		self._scroll_thread.start()
	


	def _scroller(self):
		while(self.scroll):
			gobject.idle_add(self.emit, "scroll", 1*self._velocity, 0)
			time.sleep(.05)

	"""
	def __del__(self):
		if self._connect_thread.isAlive():
			self.scan = False
			self._connect_thread.join(0)
		self._mote.close()
	
	def _scan_for_mote(self):
		print "Scanning for wiimote"
		while self._mote == None and self.scan == True:
			try: 
				self._mote = cwiid.Wiimote(flags=cwiid.FLAG_MESG_IFC)
				self._mote.rpt_mode = cwiid.RPT_BTN|cwiid.RPT_ACC
				self._mote.mesg_callback = self.cwiidCallback

				#read in accelerometer calibration
				accel_buf = self._mote.read(cwiid.RW_EEPROM, 0x16, 7)
				self._accel_calib = struct.unpack("BBBBBBB", accel_buf)

				self._mote.led = self._led_bitmask
			except:
				time.sleep(5)
		
	def cwiidCallback(self, mesgs):
		#Loop through each message
		for msg in mesgs:
			self._actions.get(msg[0])(msg[1])
	
	def acc_cllbck(self, accs):
		(xi, yi, zi) = accs
		
		x = float(xi)
		y = float(yi)
		z = float(zi)		

		# Weight the accelerations according to calibration data and
		# center around 0
		a_x = (x - self._accel_calib[0])/(self._accel_calib[4]-self._accel_calib[0])
		a_y = (y - self._accel_calib[1])/(self._accel_calib[5]-self._accel_calib[1])
		a_z = (z - self._accel_calib[2])/(self._accel_calib[6]-self._accel_calib[2])

		#self._velocity = a_y*3 + self._velocity

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
			self.rumble(.1)

		if (a_x<X_THRESHOLD and self._xabove == True):
			self._xabove = False

		if (a_x<-X_THRESHOLD and b_on and (self._xbelow == False)):
			
			self.xabove = True
			gobject.idle_add(self.emit, "dequeue")
		
		if pitch>PITCH_THRESHOLD and self._no_scroll == False and not b_on:
			self._no_scroll=True;
			wait = .4-.4*pitch
			t = threading.Timer(wait, self.scroll_again)
			t.start()
			gobject.idle_add(self.emit, "scroll", 1, 0)

		if pitch<-PITCH_THRESHOLD and self._no_scroll == False and not b_on:
			self._no_scroll=True;
			wait = -(-.4-.4*pitch)
			t = threading.Timer(wait, self.scroll_again)
			t.start()
			gobject.idle_add(self.emit, "scroll", -1, 0)
	
	def scroll_again(self):
		self._no_scroll = False
			

	def err_cllbck(self, error):
		if error == cwiid.ERROR_DISCONNECT:
			self._mote.close()
			self._mote = None
			self._connect_thread.run()
			gobject.idle_add(self.emit, "disconnect")

	def btn_cllbck(self, btns):
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

		if(btns & cwiid.BTN_1):
			gobject.idle_add(self.emit, "one_pressed")
		elif(omask & cwiid.BTN_1):
			gobject.idle_add(self.emit, "one_released")

		if(btns & cwiid.BTN_2):
			gobject.idle_add(self.emit, "two_pressed")
		elif(omask & cwiid.BTN_2):
			gobject.idle_add(self.emit, "two_released")

	
	def set_leds(self,led_bitmask):
		self._led_bitmask = led_bitmask
		if self._mote != None:
			self._mote.led=led_bitmask

	def rumble(self, seconds):
		if self._mote != None:
			self._mote.rumble = True
			time.sleep(seconds)
			self._mote.rumble = False
	
	def get_battery(self):
		if self._mote != None:
			self._mote.request_status()
			return int(float(self._mote.state['battery'])/ \
				float(cwiid.BATTERY_MAX) * 100)
		else:
			return -1

	battery = property(get_battery, None)

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

