#!/usr/bin/env python
# vim: sw=4
# Test application for diagram items.
#

import sys
import gtk
import diagram
import diacanvas
import UML
import tree
import ui

uc = getattr (UML, 'UseCase')
print 'getattr (UML, "UseCase") ->', uc

def mainquit(*args):
    for k in UML.elements.keys():
	print "Element", k, ":", UML.elements[k].__dict__
    print "Forcing Garbage collection:"
    gtk.main_quit()


model = UML.Model()

print "diagram creating"
dia = diagram.Diagram()
dia.namespace = model
print dia.namespace
print model.ownedElement.list
print "diagram created"

treemodel = tree.NamespaceModel(model)

#item = canvas.root.add (diagram.Comment)
#item.move (30, 50)
#item = canvas.root.add (diagram.Actor)
#item.move (150, 50)
item = dia.create_item (diagram.UseCase, (50, 150))
usecase = item.get_subject()
dia.create_item (diagram.UseCase, (50, 200), subject=usecase)

item = dia.create_item (diagram.Actor, (150, 50))
actor = item.get_subject()
actor.name = "Actor"

item = dia.create_item (diagram.Comment, (10,10))
comment = item.get_subject()

del item, actor, usecase, comment

#print "Comment.presentation:", comment.presentation.list
#print "Actor.presentation:", actor.presentation.list
#print "UseCase.presentation:", usecase.presentation.list

diagram_view = ui.DiagramView (dia)
diagram_view.window.connect ('destroy', mainquit)
print "diagram displayed"
del dia, diagram_view

#for k in UML.Element._hash.keys():
#    print "Element", k, ":", UML.Element._hash[k].__dict__

treemodel.dump()

print 'Going into main'
gtk.main()

#diagram_view.destroy()

UML.save('x.xml')

treemodel.dump()

UML.flush()

#print "Comment.presentation:", comment.presentation.list
#print "Actor.presentation:", actor.presentation.list
#print "UseCase.presentation:", usecase.presentation.list
#print "removing diagram..."
#dia.unlink()
#del dia
#UML.update_model()
#print "Comment.presentation:", comment.presentation.list
#print "Actor.presentation:", actor.presentation.list
#print "UseCase.presentation:", usecase.presentation.list
#del actor
#del usecase
#del comment

print "Garbage collection after gtk.main() has finished (should be empty):",
#UML.update_model()
for k in UML.elements.keys():
    print "Element", k, ":", UML.elements[k].__dict__

print "Program ended normally..."
