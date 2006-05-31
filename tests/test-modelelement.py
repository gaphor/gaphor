"""Testing the interaction between model elements and diagram items.

A model element (gaphor.UML.Element) can be removed in two ways:
1. It has a representation and the diagram item is linked to another subject
2. The diagramitem is removed from the canvas.
"""

import gc

import gaphor
import gaphor.UML as UML
import gaphor.diagram


elemfact = gaphor.resource(UML.ElementFactory)
diagram = elemfact.create(UML.Diagram)

assert len(elemfact.values()) == 1

print '*** 1'
actoritem = diagram.create(gaphor.diagram.ActorItem)
actor = elemfact.create(UML.Actor)
actoritem.set_property('subject', actor)

assert len(elemfact.values()) == 2, len(elemfact.values())
assert actoritem.parent is diagram.canvas.root
assert len(actor.presentation) == 1, len(actor.presentation)
assert actor.presentation[0] is actoritem
assert actoritem.subject is actor

# Now remove the actoritem from the diagram
# this should cause the actor to be removed too

diagram.canvas.clear_undo()

gc.collect()
print '*** 2'
del actoritem.subject

assert len(elemfact.values()) == 1, len(elemfact.values())
#assert actoritem.parent is None
assert len(actor.presentation) == 0, len(actor.presentation)
#assert actoritem.subject is None

print '*** 3'
diagram.canvas.pop_undo()

assert actoritem.parent is diagram.canvas.root
assert len(actor.presentation) == 1, len(actor.presentation)
assert actoritem.subject is actor
assert len(elemfact.values()) == 2, len(elemfact.values())

# Now see what happens when actoritem is removed from the canvas

print '*** 4'
diagram.canvas.push_undo()
diagram.canvas.clear_undo()

actoritem.unlink()

assert actoritem.parent is None
assert actoritem.subject is None
assert len(elemfact.values()) == 1, len(elemfact.values())
assert len(actor.presentation) == 0, len(actor.presentation)

print '*** 5'
diagram.canvas.pop_undo()

assert actoritem.parent is diagram.canvas.root
assert actoritem.subject is actor
assert len(elemfact.values()) == 2, len(elemfact.values())
assert len(actor.presentation) == 1, len(actor.presentation)

