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
    gtk.main_quit()


factory = UML.ElementFactory()
fact2 = UML.ElementFactory()
assert factory is fact2
del fact2

model = factory.create (UML.Model)

dia = factory.create (diagram.Diagram)
print 'diagram created:', dia
dia.namespace = model
print dia.namespace
print model.ownedElement.list
print "diagram created"

treemodel = tree.NamespaceModel(model)

#item = canvas.root.add (diagram.Comment)
#item.move (30, 50)
#item = canvas.root.add (diagram.Actor)
#item.move (150, 50)
item = dia.create (diagram.UseCase, (50, 150))
usecase = item.subject
dia.create (diagram.UseCase, (50, 200), subject=usecase)
print item.subject
print item.subject
print item.subject
print item.subject

item = dia.create (diagram.Actor, (150, 50))
actor = item.subject
actor.name = "Actor"

item = dia.create (diagram.Comment, (10,10))
comment = item.subject

del item# , actor, usecase, comment

#print "Comment.presentation:", comment.presentation.list
#print "Actor.presentation:", actor.presentation.list
#print "UseCase.presentation:", usecase.presentation.list

#del dia

#UML.flush()

#UML.load ('x.xml')

#dia = UML.lookup (2)

diagram_view = ui.DiagramView (dia)
diagram_view.window.connect ('destroy', mainquit)
print "diagram displayed"
del dia, diagram_view

#for k in UML.Element._hash.keys():
#    print "Element", k, ":", UML.Element._hash[k].__dict__

#treemodel.dump()

print 'Going into main'
gtk.main()

#diagram_view.destroy()

factory.save('x.xml')

#treemodel.dump()

factory.flush()

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

#print "Garbage collection after gtk.main() has finished (should be empty):",
#UML.update_model()
#for k in UML.elements.keys():
#    print "Element", k, ":", UML.elements[k].__dict__

print "Program ended normally..."
