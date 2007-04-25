#!/usr/bin/python
#
#
#Justin Tulloss
#
#Trying to comment well for Steve

import gtk
from gtk import gdk
import cairo
import math

class RadItem(gtk.DrawingArea):

    #Background colors for various events
    _normalBG = (0,44/255,1)
    _downBG = (2,102/255,0)
    _overBG = (165/255,1,0)

    #Constructor
    def __init__(self, text=""):
        #Calls gtk.DrawingArea's constructor
        super(RadItem, self).__init__()

        #hook up all necessary events
        self.connect("expose_event", self.expose)
        self.connect("enter_notify_event", self.enter_notify)
        self.connect("leave_notify_event", self.leave_notify)
        self.connect("button_press_event", self.button_press)
        self.connect("button_release_event", self.button_release)

        #unmask necessary events
        self.add_events(gdk.BUTTON_PRESS_MASK |
                        gdk.BUTTON_RELEASE_MASK |
                        gdk.ENTER_NOTIFY_MASK |
                        gdk.LEAVE_NOTIFY_MASK)

        self._text = text #What this button will say

        self._activeBG = self._normalBG

    def set_text(self, text):
		self._text = text

    #####EVENT HANDLERS####
    def expose(self, widget, event):
        context = widget.window.cairo_create() #CAIRO!!

        #clip so we're not constanly redrawing everything
        context.rectangle(event.area.x, event.area.y, \
            event.area.width, event.area.height)

        self.draw(context)

        return False #keep this event coming

    def button_press(self, widget, event):
        self._oldBG = self._activeBG
        self._activeBG = self._downBG
        self.redraw()
        return False

    def button_release(self, widget, event):
        self._activeBG = self._oldBG
        self.redraw()

    def enter_notify(self, widget, event):
        self._activeBG = self._overBG
        self.redraw()
    
    def leave_notify(self, widget, event):
        self._activeBG = self._normalBG
        self.redraw()

    ####END EVENT HANDLERS#######

    def redraw(self):
        if self.window:
            alloc = self.get_allocation()
            self.queue_draw_area(alloc.x, alloc.y, alloc.width, alloc.height)
            self.window.process_updates(True)

    def draw(self, context):
        context.clip()

        rect = self.get_allocation() #how big are we?
        self._centerX = rect.x + rect.width/2
        self._centerY = rect.y + rect.height/2

        #set up a transform
        #TODO:make sure we're always in the middle
            #How do I do this?
        #sets us up to have a 1.0x1.0 square surface scaled to the actual size
        context.scale(min(rect.width,rect.height),min(rect.width,rect.height))

        self._radius = .5 #half the size of the widget

        #draw the circle and background
        self.draw_circle(context)
        #put the title in the appropriate place, size, whatever
        self.draw_text(context)
        #draw glassiness
        self.draw_effect(context)

    def draw_circle(self, cr):
        cr.set_line_width(.01)
        bgcolor = self._activeBG

        #Create background gradient from the center top to the center bottom
        bgGrad = cairo.LinearGradient(.5, 0, .5, 1) # x0,y0,x1, y1
        bgGrad.add_color_stop_rgba(1, 1, 1, 1, .5) # offset, color, alpha
        bgGrad.add_color_stop_rgba(0, bgcolor[0] , bgcolor[1], bgcolor[2], .8)

        #actually draw the circle (center x, center y, radius, degrees)
        cr.arc(.5, .5, self._radius, 0, 2*math.pi)
        cr.set_source(bgGrad)
        cr.fill_preserve() #fill in the circle with the gradient

        #Draw outline around the circle (probably won't keep this)
        cr.set_source_rgba(0, 0, 0, 1)
        cr.stroke()

    def draw_text(self, cr):
        cr.set_source_rgba(0, 0, 0, .5) #font color

        #This finds how much space the text currently takes up. 
        x, y, width, height = cr.text_extents(self._text)[:4]

        #TODO: Make font size dynamic
        cr.set_font_size(.2) #Font size, should be resized from above

        #recalculate how much space the text takes with new font size
        x, y, width, height = cr.text_extents(self._text)[:4]
        #go to the top left of the above rectangle if we were to center it
        cr.move_to(.5-width/2-x, .5-height/2-y)
        cr.show_text(self._text) #actually draw the text from where we are now

    def draw_effect(self, cr):

        #Gradient from transparent to white
        grad = cairo.LinearGradient(.5, 0, .5, 1)
        grad.add_color_stop_rgba(0, 1, 1, 1, .85)
        grad.add_color_stop_rgba(1, 1, 1, 1, 0)

        #What we're doing here is drawing the same circle, but scaling it.
        # It should look like a glassy glow on the top
        cr.save() #save off old context
        cr.translate(.5-.33,.01) #move smaller circle to the middle
        cr.scale(.66, .4) #squish the drawing area
        cr.arc(.5, .5, self._radius, 0, 2*math.pi) #draw in squishe area
        cr.set_source(grad) #set up gradient to be filled in
        cr.fill()
        cr.restore() #restore old context

if __name__ == "__main__":
    mainWin = gtk.Window()
    mainWin.connect("destroy", gtk.main_quit)
    
    #Tests for above class
    trial = RadItem("Trial")

    mainWin.add(trial)
    mainWin.show_all()

    gtk.main() #main loop
