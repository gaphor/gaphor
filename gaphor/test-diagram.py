#!/usr/bin/env python
# vim: sw=4
# Test application for diagram items.
#

import sys
import diagram
import gtk
import diacanvas


def mainquit(*args):
    gtk.main_quit()
    print "Comment.body:", comment.body
    print "Actor.name:", actor.name
    #sys.exit(0)

def display_canvas_view(view):
	win = gtk.Window()
	win.connect ('destroy', mainquit)
	win.set_title ('Diagram items')
	win.set_default_size (400, 400)
	
	vbox = gtk.VBox()
	win.add (vbox)
	vbox.show()
	
	table = gtk.Table(2,2, gtk.FALSE)
	table.set_row_spacings (4)
	table.set_col_spacings (4)
	vbox.pack_start (table)
	table.show()

	frame = gtk.Frame()
	frame.set_shadow_type (gtk.SHADOW_IN)
	table.attach (frame, 0, 1, 0, 1,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)
	frame.show()

	view.set_size_request(600, 450)
	view.set_scroll_region(0, 0, 600, 450)
	frame.add (view)
	view.show()
	
	sbar = gtk.VScrollbar (view.get_vadjustment())
	table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)
	sbar.show()

	sbar = gtk.HScrollbar (view.get_hadjustment())
	table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.FILL)
	sbar.show()

	win.show()
	return win

#dia = diacanvas.Canvas()
dia = diagram.Diagram()

#item = canvas.root.add (diagram.Comment)
#item.move (30, 50)
item = dia.create_item (diagram.Comment)
comment = item.get_subject()

#item = canvas.root.add (diagram.Actor)
#item.move (150, 50)
item = dia.create_item (diagram.Actor, (150, 50))
actor = item.get_subject()
actor.name = "Some text"

#canvas.update_now()

view = diacanvas.CanvasView (canvas=dia, aa=1)

win = display_canvas_view(view)

gtk.main()

print "Comment.body:", comment.body
print "Actor.name:", actor.name
