#!/usr/bin/env python
# vim: sw=4
# Test application for diagram items.
#

import sys
import gtk
import diagram
import diacanvas
import UML
import tree.namespace as namespace
import ui

uc = getattr (UML, 'UseCase')
print 'getattr (UML, "UseCase") ->', uc

def mainquit(*args):
    gtk.main_quit()

def test_factory_signals(name, obj):
    print 'XXX Signal', name, 'for object', obj

factory = UML.ElementFactory()
fact2 = UML.ElementFactory()
assert factory is fact2
del fact2

factory.connect(test_factory_signals)

model = factory.create (UML.Model)

dia = factory.create (UML.Diagram)
print 'diagram created:', dia
dia.namespace = model
dia.name = "Diagram1"
print dia.namespace
print model.ownedElement.list
print "diagram created"
#dia.canvas.root.add (diacanvas.CanvasLine(head_pos=(0,0), tail_pos=(50,50)))
treemodel = namespace.NamespaceModel(factory)

diafact = diagram.DiagramItemFactory()

item = diafact.create(dia, diagram.CommentItem)
item.move (30, 50)
item = diafact.create(dia, diagram.ActorItem)
#item.subject.namespace = dia
item.move (150, 50)
item.subject.name = "Jaap"
#item = dia.canvas.root.create_item (diagram.UseCase)
#package = factory.create(UML.Package)
#package.namespace = model
usecase = factory.create(UML.UseCase)
usecase.namespace = model
item = diafact.create(dia, diagram.UseCaseItem, subject=usecase)
#usecase = item.subject
item = diafact.create (dia, diagram.UseCaseItem, subject=usecase)
#item.subject
item.subject.namespace = dia
item.move (200, 100)
usecase.name = 'UC1'
#item.subject.name = 'UC1'

diagram_view = ui.DiagramView (dia)
diagram_view.window.connect ('destroy', mainquit)
print "diagram displayed"
dia.canvas.clear_undo()
del dia, diagram_view

ui.TreeView (treemodel)

#for k in UML.Element._hash.keys():
#    print "Element", k, ":", UML.Element._hash[k].__dict__

treemodel.dump()

#usecase.name = 'aap'

print 'Going into main'
gtk.main()

treemodel.dump()

#diagram_view.destroy()

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
