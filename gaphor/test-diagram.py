#!/usr/bin/env python
# vim: sw=4
# Test application for diagram items.
#

import sys
import gtk
import diagram
import diacanvas
import UML
import gc

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

print "diagram creating"
dia = diagram.Diagram()
print "diagram created"
#item = canvas.root.add (diagram.Comment)
#item.move (30, 50)
#item = canvas.root.add (diagram.Actor)
#item.move (150, 50)
item = dia.create_item (diagram.Actor, (150, 50))
actor = item.get_subject()
#actor.name = "Actor"
item.set(name="Actor")

item = dia.create_item (diagram.UseCase, (50, 150))
usecase = item.get_subject()
dia.create_item (diagram.UseCase, (50, 200), usecase)

item = dia.create_item (diagram.Generalization, (150, 50))
item = dia.create_item (diagram.CommentLine, (150, 50))

item = dia.create_item (diagram.Comment, (10,10))
comment = item.get_subject()

del item

#view = diacanvas.CanvasView().set_canvas (dia.canvas)
#display_diagram (dia)
#display_canvas_view (diacanvas.CanvasView().set_canvas (dia.canvas))
win = dia.new_view()
win.connect ('destroy', mainquit)
del win
print "diagram displayed"

for k in UML.Element._hash.keys():
    print "Element", k, ":", UML.Element._hash[k]().__dict__

gtk.main()

#print "Comment.ann.Elem.:", comment.annotatedElement.list
#print "Actor.comment:", actor.comment.list
#print "UseCase.comment:", usecase.comment.list
print "Comment.presentation:", comment.presentation.list
print "Actor.presentation:", actor.presentation.list
print "UseCase.presentation:", usecase.presentation.list
print "removing diagram..."
del dia
gc.collect()
UML.Element_hash_gc()
print "Comment.presentation:", comment.presentation.list
print "Actor.presentation:", actor.presentation.list
print "UseCase.presentation:", usecase.presentation.list
del actor
del usecase
del comment
#del dia

print "Garbage collection after gtk.main() has finished:"
UML.Element_hash_gc()
for k in UML.Element._hash.keys():
    print "Element", k, ":", UML.Element._hash[k]().__dict__

print "Program ended normally..."
