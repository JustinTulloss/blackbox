import gtk


w = gtk.Window()
t = gtk.Button()
s = t.get_style()
print s

w.add(t)

w.show_all()
rect = w.get_allocation()
s.paint_vline(t.window, gtk.STATE_NORMAL, rect, w, "",0,300, 300)

gtk.main()
