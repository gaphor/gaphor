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
    for k in UML.Element._hash.keys():
	print "Element", k, ":", UML.Element._hash[k]().__dict__
    print "Forcing Garbage collection:"
    gtk.main_quit()

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

del dia
del pack
UML.Element_hash_gc()
for k in UML.Element._hash.keys():
    print "Element", k, ":", UML.Element._hash[k]().__dict__

dia = diagram.Diagram()

#item = canvas.root.add (diagram.Comment)
#item.move (30, 50)
#item = dia.create_item (diagram.Comment, (10,10))

#item = canvas.root.add (diagram.Actor)
#item.move (150, 50)
item = dia.create_item (diagram.Actor, (150, 50))
actor = item.get_subject()
actor.name = "Actor"
#item.set(name="Some text")
del actor
#item = dia.create_item (diagram.UseCase, (50, 150))

item = dia.canvas.root.add(diacanvas.CanvasLine, add_point=(0, 0))
item.set (add_point=(100,100))
del item

#view = diacanvas.CanvasView().set_canvas (dia.canvas)
#display_diagram (dia)
#display_canvas_view (diacanvas.CanvasView().set_canvas (dia.canvas))
win = dia.new_view()
win.connect ('destroy', mainquit)
del win
print "diagram displayed"

gtk.main()

print "Garbage collection after gtk.main() has finished:"
UML.Element_hash_gc()
for k in UML.Element._hash.keys():
    print "Element", k, ":", UML.Element._hash[k]().__dict__

del dia
print "removed Diagram:"
UML.Element_hash_gc()
for k in UML.Element._hash.keys():
    print "Element", k, ":", UML.Element._hash[k]().__dict__

print "Program ended normally..."
