#!/usr/bin/env python
# vim: sw=4
# Test application for diagram items.
#

import sys
import gtk
import diagram
import diacanvas
import UML

def mainquit(*args):
    gtk.main_quit()
    print "Comment.body:", comment.body
    print "Actor.name:", actor.name
    #sys.exit(0)

def display_canvas_view(view):
	win = gtk.Window()
	win.connect ('destroy', mainquit)
	win.set_title ('DiaCanvas Python example')
	win.set_default_size (300, 300)
	
	vbox = gtk.VBox()
	win.add (vbox)
	vbox.show()
	
	print "table"
	table = gtk.Table(2,2, gtk.FALSE)
	table.set_row_spacings (4)
	table.set_col_spacings (4)
	vbox.pack_start (table)
	table.show()

	print "frame"
	frame = gtk.Frame()
	frame.set_shadow_type (gtk.SHADOW_IN)
	table.attach (frame, 0, 1, 0, 1,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)
	frame.show()

	print "view"
	view = diacanvas.CanvasView (canvas=diagram.canvas)
	view.set_scroll_region(0, 0, 600, 450)
	frame.add (view)
	view.show()
	del view

	print "sbar"
	sbar = gtk.VScrollbar (view.get_vadjustment())
	table.attach (sbar, 1, 2, 0, 1, gtk.FILL,
		      gtk.EXPAND | gtk.FILL | gtk.SHRINK)
	sbar.show()

	print "sbar"
	sbar = gtk.HScrollbar (view.get_hadjustment())
	table.attach (sbar, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL | gtk.SHRINK,
		      gtk.FILL)
	sbar.show()

	print "showing"
	win.show()
	print "done"

diagram_list = [ ]
	
def display_diagram(diagram):
    view = diacanvas.CanvasView()
    diagram_list.append(view)
    view.set_canvas(diagram.canvas)
    display_canvas_view (view)

# First some consistency tests
dia = diagram.Diagram()
pack = UML.Package()

assert (dia.id == 1)
assert (pack.id == 2)

pack.ownedElement = dia
#dia.namespace = pack
print pack.ownedElement.list
print dia.namespace

assert (dia in pack.ownedElement.list)

#dia = diacanvas.Canvas()
dia = diagram.Diagram()

#item = canvas.root.add (diagram.Comment)
#item.move (30, 50)
item = dia.create_item (diagram.Comment, (10,10))
comment = item.get_subject()

#item = canvas.root.add (diagram.Actor)
#item.move (150, 50)
item = dia.create_item (diagram.Actor, (150, 50))
actor = item.get_subject()
actor.name = "Some text"

item = dia.create_item (diagram.UseCase, (50, 150))

item = dia.canvas.root.add(diacanvas.CanvasLine, add_point=(0, 0))
item.set (add_point=(100,100))

#view = diacanvas.CanvasView().set_canvas (dia.canvas)
#display_diagram (dia)
#display_canvas_view (diacanvas.CanvasView().set_canvas (dia.canvas))
dia.new_view()
#win.connect ('destroy', mainquit)
print "diagram displayed"

gtk.main()

print "Comment.body:", comment.body
print "Actor.name:", actor.name
