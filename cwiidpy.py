#!/usr/bin/python
#
#
#Justin Tulloss
#
#
#
"""Provides a python interface to the CWIID driver"""

from cwiidmodule import *

#Set up the massive number of enumerations that don't actually work in py
# Report Mode Flags 
RPT_STATUS=0x01
RPT_BTN=0x02
RPT_ACC=0x04
RPT_IR=0x08
RPT_NUNCHUK=0x10
RPT_CLASSIC=0x20
RPT_EXT=(RPT_NUNCHUK | RPT_CLASSIC)

# LED flags #
LED1_ON=0x01
LED2_ON=0x02
LED3_ON=0x04
LED4_ON=0x08

# Button flags #
BTN_2=0x0001
BTN_1=0x0002
BTN_B=0x0004
BTN_A=0x0008
BTN_MINUS=0x0010
BTN_HOME=0x0080
BTN_LEFT=0x0100
BTN_RIGHT=0x0200
BTN_DOWN=0x0400
BTN_UP=0x0800
BTN_PLUS=0x1000

NUNCHUK_BTN_Z=0x01
NUNCHUK_BTN_C=0x02

CLASSIC_BTN_UP=0x0001
CLASSIC_BTN_LEFT=0x0002
CLASSIC_BTN_ZR=0x0004
CLASSIC_BTN_X=0x0008
CLASSIC_BTN_A=0x0010
CLASSIC_BTN_Y=0x0020
CLASSIC_BTN_B=0x0040
CLASSIC_BTN_ZL=0x0080
CLASSIC_BTN_R=0x0200
CLASSIC_BTN_PLUS=0x0400
CLASSIC_BTN_HOME=0x0800
CLASSIC_BTN_MINUS=0x1000
CLASSIC_BTN_L=0x2000
CLASSIC_BTN_DOWN=0x4000
CLASSIC_BTN_RIGHT=0x8000

# Data Read/Write flags #
RW_EEPROM=0x00
RW_REG=0x04
RW_DECODE=0x01

# Maximum Data Read Length #
MAX_READ_LEN=0xFFFF

# IR Defs #
IR_SRC_COUNT=4
IR_X_MAX=1024
IR_Y_MAX=768

# Battery #
BATTERY_MAX=0xD0

# Classic Controller Maxes #
CLASSIC_L_STICK_MAX=0x3F
CLASSIC_R_STICK_MAX=0x1F
CLASSIC_LR_MAX=0x1F

# Environment Variables #
WIIMOTE_BDADDR="WIIMOTE_BDADDR"

# Callback Maximum Message Count #
MAX_MESG_COUNT=5

#Enumerations##########################
[CMD_STATUS,
CMD_LED,
CMD_RUMBLE,
CMD_RPT_MODE] = range(4)

[MESG_STATUS,
MESG_BTN,
MESG_ACC,
MESG_IR,
MESG_NUNCHUK,
MESG_CLASSIC,
MESG_ERROR,
MESG_UNKNOWN] = range(8)

[EXT_NONE,
EXT_NUNCHUK,
EXT_CLASSIC,
EXT_UNKNOWN] = range(4)

[ERROR_DISCONNECT,
ERROR_COMM] = range(2)




class cwiid:
    def __init__(self, callback):
        self._callback = callback
        self._wii = cwiidmodule(self._callback)
        #self._wii = cwiidmodule(test)
        print self._wii
        self._wii.command(CMD_RPT_MODE, RPT_BTN|RPT_ACC)
    

if __name__=="__main__":
    def test(id, values):
        print id, values

    myWii = cwiid(test)

    while 1:
        pass
