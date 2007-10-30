import cairo

def cairo_color(color):
	"""Helper function to convert 0xXXXXXX colors to cairo values"""
	ccolor=((float(color>>16)/255.0),
		(float(color>>8&0xff)/255.0),
		(float(color&0xff)/255.0))

	return ccolor

def draw_bg_gradient(cr,color, rect):
	bgcolor = cairo_color(color)
	cr.save()
	cr.translate(rect.x, rect.y)
	cr.scale(rect.width, rect.height)
	cr.rectangle(0,0, 1,1)
	bg = cairo.LinearGradient(.5, 0, .5, 1)
	bg.add_color_stop_rgba(0, bgcolor[0]+.2, bgcolor[1]+.2, bgcolor[2]+.2, 1)
	bg.add_color_stop_rgba(1, bgcolor[0], bgcolor[1], bgcolor[2], 1)
	cr.set_source(bg)
	cr.fill()
	cr.restore()


def draw_bg(cr,color, rect):
	bgcolor = cairo_color(color)
	cr.save()
	cr.translate(rect.x, rect.y)
	cr.scale(rect.width, rect.height)
	cr.rectangle(0,0, 1,1)
	cr.set_source_rgb(bgcolor[0],bgcolor[1],bgcolor[2])
	cr.fill()
	cr.restore()


