#
# Test the behavior of a UML tree with a Diagram as leaf. The whole tree
# should be freed...
#

import UML
from diagram import *
import gc

factory = UML.ElementFactory()
model = factory.create(UML.Model)
model.name = "MyModel"

package = factory.create(UML.Package)
package.name = "Package"

model.ownedElement = package
assert len(model.ownedElement.list) == 1
assert model.ownedElement.list[0] is package
assert package.namespace is model

actor = factory.create(UML.Actor)
actor.namespace = package
assert len(package.ownedElement.list) == 1
assert package.ownedElement.list[0] is actor
assert actor.namespace is package

usecase = factory.create (UML.UseCase)
usecase.namespace = package
assert len(package.ownedElement.list) == 2
assert package.ownedElement.list[0] is actor
assert package.ownedElement.list[1] is usecase
assert usecase.namespace is package

dia = factory.create(diagram.Diagram)
print dia
dia.namespace = package
assert len(package.ownedElement.list) == 3
assert package.ownedElement.list[0] is actor
assert package.ownedElement.list[1] is usecase
assert package.ownedElement.list[2] is dia
assert dia.namespace is package

dia.create(diagramitem.ActorItem, pos=(0, 0), subject=actor)
dia.create(diagramitem.UseCaseItem, pos=(100, 100), subject=usecase)

#dia.destroy_diagrams()

model.unlink()
del model
usecase.unlink()
del usecase
actor.unlink()
del actor
package.unlink()
del package
dia.unlink()
del dia

gc.collect()
gc.set_debug (gc.DEBUG_LEAK)

print "Uncollectable objects found:", gc.garbage


